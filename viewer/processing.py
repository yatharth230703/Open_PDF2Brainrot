# viewer/processing.py
from pathlib import Path
from .main import convert_pdf

def process_pdf(pdf_path: Path, output_root: Path) -> None:
    convert_pdf(pdf_path, output_root)
