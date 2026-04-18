from pathlib import Path
from weasyprint import HTML


def convert_html_to_pdf(html_string: str, output_path: Path) -> Path:
    """
    Takes a rendered HTML string and writes a PDF to output_path.
    Returns the output path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_string).write_pdf(str(output_path))
    return output_path
