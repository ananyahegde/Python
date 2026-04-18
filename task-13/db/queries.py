import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_monthly_summary(conn: sqlite3.Connection, year: int, month: int) -> dict:
    """
    Total revenue, units sold, order count, avg order value for the given month.
    """
    query = """
        SELECT
            COUNT(*)            AS order_count,
            SUM(units)          AS units_sold,
            SUM(revenue)        AS total_revenue,
            AVG(revenue)        AS avg_order_value
        FROM sales
        WHERE strftime('%Y', sale_date) = ?
          AND strftime('%m', sale_date) = ?
    """
    row = conn.execute(query, (str(year), f"{month:02d}")).fetchone()
    return dict(row)


def get_previous_month_revenue(conn: sqlite3.Connection, year: int, month: int) -> float:
    """
    Total revenue for the month prior to the given month.
    Used for MoM growth calculation.
    """
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    query = """
        SELECT SUM(revenue) AS total_revenue
        FROM sales
        WHERE strftime('%Y', sale_date) = ?
          AND strftime('%m', sale_date) = ?
    """
    row = conn.execute(query, (str(prev_year), f"{prev_month:02d}")).fetchone()
    return row["total_revenue"] or 0.0


def get_revenue_by_region(conn: sqlite3.Connection, year: int, month: int) -> list[dict]:
    """
    Revenue and units per region for the given month, ordered by revenue desc.
    """
    query = """
        SELECT
            region,
            SUM(revenue)    AS total_revenue,
            SUM(units)      AS units_sold
        FROM sales
        WHERE strftime('%Y', sale_date) = ?
          AND strftime('%m', sale_date) = ?
        GROUP BY region
        ORDER BY total_revenue DESC
    """
    rows = conn.execute(query, (str(year), f"{month:02d}")).fetchall()
    return [dict(r) for r in rows]


def get_previous_month_revenue_by_region(conn: sqlite3.Connection, year: int, month: int) -> dict[str, float]:
    """
    Revenue per region for the prior month.
    Returns a dict: { region_name: revenue }
    Used to compute per-region MoM change.
    """
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    query = """
        SELECT region, SUM(revenue) AS total_revenue
        FROM sales
        WHERE strftime('%Y', sale_date) = ?
          AND strftime('%m', sale_date) = ?
        GROUP BY region
    """
    rows = conn.execute(query, (str(prev_year), f"{prev_month:02d}")).fetchall()
    return {r["region"]: r["total_revenue"] for r in rows}


def get_daily_sales_trend(conn: sqlite3.Connection, year: int, month: int) -> list[dict]:
    """
    Revenue per day for the given month, ordered by date asc.
    Used for the line chart.
    """
    query = """
        SELECT
            sale_date,
            SUM(revenue) AS daily_revenue
        FROM sales
        WHERE strftime('%Y', sale_date) = ?
          AND strftime('%m', sale_date) = ?
        GROUP BY sale_date
        ORDER BY sale_date ASC
    """
    rows = conn.execute(query, (str(year), f"{month:02d}")).fetchall()
    return [dict(r) for r in rows]


def get_record_count(conn: sqlite3.Connection, year: int, month: int) -> int:
    """
    Raw row count for the given month. Used in the CLI progress log.
    """
    query = """
        SELECT COUNT(*) AS cnt
        FROM sales
        WHERE strftime('%Y', sale_date) = ?
          AND strftime('%m', sale_date) = ?
    """
    row = conn.execute(query, (str(year), f"{month:02d}")).fetchone()
    return row["cnt"]
