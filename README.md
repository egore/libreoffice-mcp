# LibreOffice MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with LibreOffice, specifically for:
1. Converting .docx documents to PDF
2. Generating form letters from templates

## Requirements

- Python 3.7+
- LibreOffice installed and available in PATH
- Python dependencies (see `requirements.txt`)

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Server

Start the server with:

```bash
cd /path/to/libreoffice-mcp
python src/server.py
```

The server will start on port 8000 by default.

## Available Tools

### 1. Convert DOCX to PDF

Converts a Microsoft Word document (.docx) to PDF format using LibreOffice.

**MCP Tool Name:** `convert_docx_to_pdf`

**Parameters:**
- `file_path`: Path to the .docx file to convert
- `output_directory` (optional): Directory to save the PDF

**Example:**
```json
{
  "file_path": "/path/to/document.docx",
  "output_directory": "/path/to/output"
}
```

### 2. Generate Form Letters

Creates personalized documents from a template by replacing placeholders with recipient data.

**MCP Tool Name:** `generate_form_letters`

**Parameters:**
- `template_path`: Path to the template document
- `recipients`: Array of recipient data objects with field values
- `output_format` (optional): Output format (pdf or docx), default: "pdf"

**Example:**
```json
{
  "template_path": "/path/to/template.docx",
  "recipients": [
    {
      "name": "John Doe",
      "address": "123 Main St",
      "city": "Anytown",
      "reference": "ABC123"
    },
    {
      "name": "Jane Smith",
      "address": "456 Oak Ave",
      "city": "Somewhere",
      "reference": "XYZ789"
    }
  ],
  "output_format": "pdf"
}
```

## Template Format

Templates should be .docx files with placeholders in the format `{{field_name}}`. For example:

```
Dear {{name}},

We are writing regarding your account {{reference}}...

Your address on file is:
{{address}}
{{city}}
```

## HTTP API

In addition to the MCP protocol, the server also provides a REST API:

- `POST /convert-to-pdf`: Convert an uploaded document to PDF
- `POST /generate-form-letters`: Generate form letters from an uploaded template and recipient data

## MCP Protocol Endpoints

- `GET /mcp/list-tools`: List available MCP tools
- `POST /mcp/invoke/{tool_name}`: Invoke an MCP tool with parameters
