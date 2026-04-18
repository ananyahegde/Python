from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "db" / "sales.db"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
CHARTS_TEMP_DIR = BASE_DIR / "charts" / "temp"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
CHARTS_TEMP_DIR.mkdir(parents=True, exist_ok=True)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"

EMAIL_RECIPIENTS = [
    "exec-team@company.com",
    "sales-leads@company.com",
]
EMAIL_FROM = "reports@company.com"

TEMPLATE_NAME = "sales_monthly"
REGIONS = ["North", "South", "East", "West"]
