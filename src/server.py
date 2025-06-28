#!/usr/bin/env python3
"""
LibreOffice MCP Server
Provides tools for interacting with LibreOffice through MCP protocol
"""

import os
import json
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

# Import form letter generator
try:
    # When running as a module (e.g. during tests)
    from src.form_letters import FormLetterGenerator
except ImportError:
    # When running directly
    from form_letters import FormLetterGenerator

app = FastAPI(title="LibreOffice MCP Server")

# Configuration
LIBREOFFICE_PATH = "soffice"  # Assumes LibreOffice is in PATH


# Models
class ConversionResponse(BaseModel):
    output_path: str
    success: bool
    message: str


class FormLetterRequest(BaseModel):
    template_id: str
    recipients: list[dict[str, str]]
    output_format: str = "pdf"


class FormLetterResponse(BaseModel):
    output_paths: list[str]
    success: bool
    message: str


# Utility functions
def ensure_directory(directory_path: str) -> None:
    """Ensure the specified directory exists."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_temp_directory() -> str:
    """Get a temporary directory for file operations."""
    temp_dir = os.path.join(tempfile.gettempdir(), "libreoffice_mcp", str(uuid.uuid4()))
    ensure_directory(temp_dir)
    return temp_dir


def convert_to_pdf(input_path: str, output_directory: str = None) -> str:
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
        LIBREOFFICE_PATH,
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


# API Endpoints
@app.post("/convert-to-pdf", response_model=ConversionResponse)
async def api_convert_to_pdf(
    file: UploadFile = File(...), output_directory: Optional[str] = None
):
    """Convert a document to PDF using LibreOffice."""
    try:
        # Save the uploaded file
        temp_dir = get_temp_directory()
        input_path = os.path.join(temp_dir, file.filename)

        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Convert to PDF
        output_path = convert_to_pdf(input_path, output_directory)

        return ConversionResponse(
            output_path=output_path, success=True, message="Conversion successful"
        )

    except Exception as e:
        return ConversionResponse(output_path="", success=False, message=str(e))


@app.post("/generate-form-letters", response_model=FormLetterResponse)
async def api_generate_form_letters(
    template_file: UploadFile = File(...),
    recipients_json: str = Form(...),
    output_format: str = Form("pdf"),
):
    """
    Generate form letters using a template and recipient data.
    """
    try:
        # Save the uploaded template file
        temp_dir = get_temp_directory()
        template_path = os.path.join(temp_dir, template_file.filename)

        with open(template_path, "wb") as f:
            content = await template_file.read()
            f.write(content)

        # Parse the recipients JSON
        try:
            recipients = json.loads(recipients_json)
            if not isinstance(recipients, list):
                raise ValueError("Recipients must be a JSON array")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for recipients")

        # Generate form letters
        generator = FormLetterGenerator(LIBREOFFICE_PATH)
        output_paths = generator.generate_form_letters(
            template_path=template_path,
            recipients=recipients,
            output_format=output_format,
        )

        return FormLetterResponse(
            output_paths=output_paths,
            success=True,
            message=f"Successfully generated {len(output_paths)} form letters",
        )

    except Exception as e:
        return FormLetterResponse(output_paths=[], success=False, message=str(e))


# MCP Server Configuration
@app.get("/mcp/list-tools")
async def list_tools():
    """List the available tools for the MCP protocol."""
    tools = [
        {
            "name": "convert_docx_to_pdf",
            "description": "Convert a .docx document to PDF format",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the .docx file to convert",
                    },
                    "output_directory": {
                        "type": "string",
                        "description": "Optional directory to save the PDF",
                    },
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "generate_form_letters",
            "description": "Generate form letters from a template and recipient data",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_path": {
                        "type": "string",
                        "description": "Path to the template document",
                    },
                    "recipients": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Array of recipient data objects with field values",
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (pdf or docx)",
                        "default": "pdf",
                    },
                },
                "required": ["template_path", "recipients"],
            },
        },
    ]

    return {"tools": tools}


@app.post("/mcp/invoke/{tool_name}")
async def invoke_tool(tool_name: str, parameters: dict[str, Any]):
    """Invoke an MCP tool with the given parameters."""
    if tool_name == "convert_docx_to_pdf":
        file_path = parameters.get("file_path")
        output_directory = parameters.get("output_directory")

        if not file_path:
            raise HTTPException(status_code=400, detail="file_path is required")

        try:
            output_path = convert_to_pdf(file_path, output_directory)
            return {"result": {"output_path": output_path}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif tool_name == "generate_form_letters":
        template_path = parameters.get("template_path")
        recipients = parameters.get("recipients")
        output_format = parameters.get("output_format", "pdf")

        if not template_path or not recipients:
            raise HTTPException(
                status_code=400, detail="template_path and recipients are required"
            )

        try:
            generator = FormLetterGenerator(LIBREOFFICE_PATH)
            output_paths = generator.generate_form_letters(
                template_path=template_path,
                recipients=recipients,
                output_format=output_format,
            )

            return {"result": {"output_paths": output_paths}}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    else:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
