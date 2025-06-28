"""
Convert a document to PDF using LibreOffice.
"""

import os
import subprocess
from typing import Any, Optional
from .util import get_temp_directory, ensure_directory

class PdfConverter:
    """
    Class for converting documents to PDF using LibreOffice
    """

    def __init__(self, libreoffice_path: str = "soffice"):
        """
        Initialize the PDF converter

        Args:
            libreoffice_path: Path to the LibreOffice executable
        """
        self.libreoffice_path = libreoffice_path

    def convert_to_pdf(self, input_path: str, output_directory: str = None) -> str:
        """
        Convert a document to PDF using LibreOffice.

        Args:
            input_path: Path to the input document
            output_directory: Directory to save the PDF (optional)

        Returns:
            Path to the output PDF file
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if output_directory is None:
            output_directory = get_temp_directory()
        else:
            ensure_directory(output_directory)

        # Construct the LibreOffice command
        cmd = [
            self.libreoffice_path,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_directory,
            input_path,
        ]

        try:
            # Run the conversion
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Get the output filename
            input_filename = os.path.basename(input_path)
            output_filename = os.path.splitext(input_filename)[0] + ".pdf"
            output_path = os.path.join(output_directory, output_filename)

            if not os.path.exists(output_path):
                raise RuntimeError(
                    f"Conversion failed: Output file not found at {output_path}"
                )

            return output_path

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"LibreOffice conversion failed: {e.stderr}")

    def tool_convert_docx_to_pdf(
        self, file_path: str, output_directory: Optional[str] = None
    ) -> dict[str, Any]:
        """Convert a .docx document to PDF format."""
        try:
            output_path = self.convert_to_pdf(file_path, output_directory)
            return {
                "output_path": output_path,
                "success": True,
                "message": "Conversion successful",
            }
        except Exception as e:
            return {"output_path": "", "success": False, "message": str(e)}
