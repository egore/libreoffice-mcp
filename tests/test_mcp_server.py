#!/usr/bin/env python3
"""
Tests for the MCP server implementation
"""

import os
import unittest
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import mcp_server, tool_convert_docx_to_pdf, tool_generate_form_letters

class TestMCPServer(unittest.TestCase):
    """Test cases for MCP server"""
    
    def test_server_initialization(self):
        """Test that the MCP server initializes correctly"""
        self.assertEqual(mcp_server.name, "LibreOffice MCP Server")
        self.assertEqual(mcp_server.description, "MCP server for interacting with LibreOffice")
        self.assertEqual(mcp_server.version, "1.0.0")
    
    def test_server_tools(self):
        """Test that the server has the correct tools registered"""
        # Get the list of tools
        tools = mcp_server.list_tools()
        
        # Check that we have exactly 2 tools
        self.assertEqual(len(tools), 2)
        
        # Check that the tools have the expected names
        tool_names = [tool.name for tool in tools]
        self.assertIn("convert_docx_to_pdf", tool_names)
        self.assertIn("generate_form_letters", tool_names)
        
        # Check details of the convert_docx_to_pdf tool
        convert_tool = next(tool for tool in tools if tool.name == "convert_docx_to_pdf")
        self.assertEqual(convert_tool.description, "Convert a .docx document to PDF format")
        self.assertEqual(len(convert_tool.parameters), 2)
        
        # Check parameters of convert_docx_to_pdf tool
        param_names = [param.name for param in convert_tool.parameters]
        self.assertIn("file_path", param_names)
        self.assertIn("output_directory", param_names)
        
        # Check that file_path is required
        file_path_param = next(param for param in convert_tool.parameters if param.name == "file_path")
        self.assertTrue(file_path_param.required)
        
        # Check details of the generate_form_letters tool
        form_tool = next(tool for tool in tools if tool.name == "generate_form_letters")
        self.assertEqual(form_tool.description, "Generate form letters from a template and recipient data")
        self.assertEqual(len(form_tool.parameters), 3)
        
        # Check parameters of generate_form_letters tool
        param_names = [param.name for param in form_tool.parameters]
        self.assertIn("template_path", param_names)
        self.assertIn("recipients", param_names)
        self.assertIn("output_format", param_names)
        
        # Check that template_path and recipients are required
        template_param = next(param for param in form_tool.parameters if param.name == "template_path")
        self.assertTrue(template_param.required)
        
        recipients_param = next(param for param in form_tool.parameters if param.name == "recipients")
        self.assertTrue(recipients_param.required)
        
        # Check that output_format is not required and has a default value
        output_format_param = next(param for param in form_tool.parameters if param.name == "output_format")
        self.assertFalse(output_format_param.required)
        self.assertEqual(output_format_param.default, "pdf")
    
    @patch('src.mcp_server.convert_to_pdf')
    def test_convert_docx_to_pdf_tool(self, mock_convert):
        """Test the convert_docx_to_pdf tool function"""
        # Set up the mock to return a specific path
        mock_convert.return_value = "/tmp/output.pdf"
        
        # Call the tool function
        result = tool_convert_docx_to_pdf(file_path="/path/to/document.docx")
        
        # Check that the mock was called with the correct arguments
        mock_convert.assert_called_once_with("/path/to/document.docx", None)
        
        # Check the result
        self.assertEqual(result["output_path"], "/tmp/output.pdf")
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Conversion successful")
    
    @patch('src.mcp_server.FormLetterGenerator')
    def test_generate_form_letters_tool(self, mock_generator_class):
        """Test the generate_form_letters tool function"""
        # Set up the mock
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_generator.generate_form_letters.return_value = ["/tmp/letter1.pdf", "/tmp/letter2.pdf"]
        
        # Test data
        template_path = "/path/to/template.docx"
        recipients = [
            {"name": "John Doe", "address": "123 Main St"},
            {"name": "Jane Smith", "address": "456 Oak Ave"}
        ]
        
        # Call the tool function
        result = tool_generate_form_letters(
            template_path=template_path,
            recipients=recipients,
            output_format="pdf"
        )
        
        # Check that the mock was called with the correct arguments
        mock_generator_class.assert_called_once()
        mock_generator.generate_form_letters.assert_called_once_with(
            template_path=template_path,
            recipients=recipients,
            output_format="pdf"
        )
        
        # Check the result
        self.assertEqual(result["output_paths"], ["/tmp/letter1.pdf", "/tmp/letter2.pdf"])
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Successfully generated 2 form letters")

if __name__ == "__main__":
    unittest.main()
