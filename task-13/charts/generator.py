import io
import matplotlib
matplotlib.use("Agg")  # non-interactive backend, no GUI window
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


def generate_bar_chart(region_data: list[dict]) -> bytes:
    """
    Bar chart: revenue by region.
    Returns PNG bytes.
    """
    regions = [r["region"] for r in region_data]
    revenues = [r["total_revenue"] for r in region_data]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(regions, revenues, color=["#859499", "#8A8599", "#998A85", "#949985"])

    ax.set_xlabel("Revenue (INR)")
    ax.set_title("Revenue by Region")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    # Value labels on bars
    for bar, val in zip(bars, revenues):
        ax.text(
            bar.get_width() + max(revenues) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"${val:,.0f}",
            va="center",
            fontsize=9,
        )

    ax.invert_yaxis()  # highest revenue at top
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def generate_line_chart(daily_trend: list[dict]) -> bytes:
    """
    Line chart: daily sales trend across the month.
    daily_trend: [{"sale_date": "2026-01-01", "daily_revenue": 45000.0}, ...]
    Returns PNG bytes.
    """
    dates = [d["sale_date"] for d in daily_trend]
    revenues = [d["daily_revenue"] for d in daily_trend]

    # Show only day number on x-axis to avoid clutter
    day_labels = [d.split("-")[2] for d in dates]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(day_labels, revenues, marker="o", markersize=3, linewidth=1.5, color="#4C72B0")
    ax.fill_between(day_labels, revenues, alpha=0.1, color="#4C72B0")

    ax.set_xlabel("Day of Month")
    ax.set_ylabel("Revenue (INR)")
    ax.set_title("Daily Sales Trend")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

    # Show every 5th day label to avoid overlap
    for i, label in enumerate(ax.get_xticklabels()):
        if i % 5 != 0:
            label.set_visible(False)

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
