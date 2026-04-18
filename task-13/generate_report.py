import argparse
import sys
from datetime import datetime
from pathlib import Path

from config import DB_PATH, REPORTS_DIR, TEMPLATE_NAME
from db.queries import (
    get_connection,
    get_monthly_summary,
    get_previous_month_revenue,
    get_revenue_by_region,
    get_previous_month_revenue_by_region,
    get_daily_sales_trend,
    get_record_count,
)
from charts.generator import generate_bar_chart, generate_line_chart
from renderer.html_renderer import render_report
from pdf.converter import convert_html_to_pdf


def parse_args():
    parser = argparse.ArgumentParser(description="PDF Sales Report Generator")
    parser.add_argument(
        "--month",
        required=True,
        help="Month to generate report for. Format: YYYY-MM (e.g. 2026-01)",
    )
    parser.add_argument(
        "--template",
        default=TEMPLATE_NAME,
        help="Template name to use (without .html extension)",
    )
    return parser.parse_args()


def parse_month(month_str: str) -> tuple[int, int]:
    try:
        dt = datetime.strptime(month_str, "%Y-%m")
        return dt.year, dt.month
    except ValueError:
        print(f"ERROR: Invalid month format '{month_str}'. Use YYYY-MM.")
        sys.exit(1)


def step(n: int, total: int, msg: str, status: str = "") -> None:
    if status:
        print(f"[{n}/{total}] {msg}... {status}")
    else:
        print(f"[{n}/{total}] {msg}...")


def main():
    args = parse_args()
    year, month = parse_month(args.month)
    month_label = datetime(year, month, 1).strftime("%B %Y")
    total_steps = 4  # email is optional add-on, not counted here

    print(f"\n=== Report Generation ===")

    # DB connection
    step(1, total_steps, "Connecting to database")
    conn = get_connection()
    print(f"[1/{total_steps}] Connecting to database... OK")

    # Query data
    step(2, total_steps, f"Querying {month_label} sales data")
    record_count = get_record_count(conn, year, month)
    summary = get_monthly_summary(conn, year, month)
    prev_revenue = get_previous_month_revenue(conn, year, month)
    region_data = get_revenue_by_region(conn, year, month)
    prev_region_revenue = get_previous_month_revenue_by_region(conn, year, month)
    daily_trend = get_daily_sales_trend(conn, year, month)
    conn.close()
    print(f"[2/{total_steps}] Querying {month_label} sales data... OK ({record_count:,} records)")

    # Render template
    step(3, total_steps, f'Rendering template "{args.template}"')
    bar_chart_png = generate_bar_chart(region_data)
    line_chart_png = generate_line_chart(daily_trend)
    html_string = render_report(
        template_name=args.template,
        summary=summary,
        region_data=region_data,
        prev_region_revenue=prev_region_revenue,
        daily_trend=daily_trend,
        bar_chart_png=bar_chart_png,
        line_chart_png=line_chart_png,
        year=year,
        month=month,
        prev_month_revenue=prev_revenue,
    )
    print(f"[3/{total_steps}] Rendering template \"{args.template}\"... OK")

    # Generate PDF
    step(4, total_steps, "Generating PDF")
    filename = f"sales_report_{year}-{month:02d}.pdf"
    output_path = REPORTS_DIR / filename
    convert_html_to_pdf(html_string, output_path)
    file_size_kb = output_path.stat().st_size / 1024
    print(f"[4/{total_steps}] Generating PDF... OK")
    print(f"\nOutput: {output_path}")
    print(f"Size:   {file_size_kb:.1f} KB")
    print(f"\n=== Done ===\n")

    # Send email
    from email_sender.mailer import send_report
    print(f"[5/5] Sending email...")
    send_report(output_path, month_label)

if __name__ == "__main__":
    main()
