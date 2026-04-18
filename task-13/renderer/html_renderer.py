import base64
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import TEMPLATES_DIR


def _b64_encode_png(png_bytes: bytes) -> str:
    return base64.b64encode(png_bytes).decode("utf-8")


def _compute_warnings(region_data: list[dict], threshold: float = -5.0) -> list[str]:
    """
    Returns a list of warning strings for any region whose MoM change
    is below the threshold (default: -5%).
    """
    warnings = []
    for r in region_data:
        if r["mom_change"] < threshold:
            warnings.append(
                f"{r['region']} region declined {abs(r['mom_change']):.1f}% MoM"
            )
    return warnings


def _attach_mom_change(region_data: list[dict], prev_region_revenue: dict[str, float]) -> list[dict]:
    """
    Adds a mom_change key to each region dict.
    region_data: output of get_revenue_by_region()
    prev_region_revenue: output of get_previous_month_revenue_by_region()
    """
    for r in region_data:
        prev = prev_region_revenue.get(r["region"], 0.0)
        if prev and prev > 0:
            r["mom_change"] = ((r["total_revenue"] - prev) / prev) * 100
        else:
            r["mom_change"] = 0.0
    return region_data


def render_report(
    template_name: str,
    summary: dict,
    region_data: list[dict],
    prev_region_revenue: dict[str, float],
    daily_trend: list[dict],
    bar_chart_png: bytes,
    line_chart_png: bytes,
    year: int,
    month: int,
    prev_month_revenue: float,
) -> str:
    """
    Renders the Jinja2 template with all data and returns a complete HTML string.
    """
    # MoM growth overall
    prev = prev_month_revenue
    if prev and prev > 0:
        mom_growth = ((summary["total_revenue"] - prev) / prev) * 100
    else:
        mom_growth = 0.0

    # Attach per-region MoM change
    region_data = _attach_mom_change(region_data, prev_region_revenue)

    # Warnings
    warnings = _compute_warnings(region_data)

    # Month label e.g. "January 2026"
    month_label = datetime(year, month, 1).strftime("%B %Y")
    generated_at = datetime.now().strftime("%d %b %Y, %H:%M")

    # Jinja2 environment
    env = Environment(FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template(f"{template_name}.html")

    html = template.render(
        month_label=month_label,
        generated_at=generated_at,
        summary=summary,
        mom_growth=mom_growth,
        region_data=region_data,
        bar_chart_b64=_b64_encode_png(bar_chart_png),
        line_chart_b64=_b64_encode_png(line_chart_png),
        warnings=warnings,
    )

    return html
