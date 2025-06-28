"""
LibreOffice MCP Server using the MCP protocol library
"""
import logging
from pathlib import Path
from enum import Enum
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
from pydantic import BaseModel

from .form_letters import FormLetterGenerator
from .convert_pdf import PdfConverter

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




class LibreOfficeTools(str, Enum):
    """LibreOffice tools to publish via MCP."""
    CONVERT_DOCX_TO_PDF = "convert_docx_to_pdf"
    GENERATE_FORM_LETTERS = "generate_form_letters"

async def serve(libreoffice_path: Path) -> None:

    server = Server("libreoffice_mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=LibreOfficeTools.CONVERT_DOCX_TO_PDF,
                description="Converts a .docx document to PDF format",
                inputSchema=ConversionResponse.model_json_schema(),
            ),
            Tool(
                name=LibreOfficeTools.GENERATE_FORM_LETTERS,
                description="Shows changes in the working directory that are not yet staged",
                inputSchema=FormLetterRequest.model_json_schema(),
                outputSchema=FormLetterResponse.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        match name:
            case LibreOfficeTools.CONVERT_DOCX_TO_PDF:
                result = PdfConverter(libreoffice_path).tool_convert_docx_to_pdf(str(arguments["file_path"]))
                return [TextContent(
                    type="text",
                    text=result
                )]
            case LibreOfficeTools.GENERATE_FORM_LETTERS:
                result = FormLetterGenerator(libreoffice_path).tool_generate_form_letters(str(arguments["template_path"]))
                return [TextContent(
                    type="text",
                    text=result
                )]
            case _:
                raise ValueError(f"Unknown tool: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)