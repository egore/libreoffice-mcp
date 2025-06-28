#!/usr/bin/env python3
"""
Tests for the MCP server tool listing functionality
"""

import os
import unittest
import json
from fastapi.testclient import TestClient

# Add parent directory to path to import modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.server import app

class TestServerTools(unittest.TestCase):
    """Test cases for MCP server tool listing"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = TestClient(app)
    
    def test_list_tools(self):
        """Test that the server correctly lists both tools"""
        # Make a request to the list-tools endpoint
        response = self.client.get("/mcp/list-tools")
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the response JSON
        data = response.json()
        
        # Check that the response contains a 'tools' key
        self.assertIn("tools", data)
        
        # Get the list of tools
        tools = data["tools"]
        
        # Check that the list contains exactly 2 tools
        self.assertEqual(len(tools), 2)
        
        # Check that the tools have the expected names
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("convert_docx_to_pdf", tool_names)
        self.assertIn("generate_form_letters", tool_names)
        
        # Check details of the convert_docx_to_pdf tool
        convert_tool = next(tool for tool in tools if tool["name"] == "convert_docx_to_pdf")
        self.assertIn("description", convert_tool)
        self.assertIn("parameters", convert_tool)
        self.assertIn("properties", convert_tool["parameters"])
        self.assertIn("file_path", convert_tool["parameters"]["properties"])
        self.assertIn("output_directory", convert_tool["parameters"]["properties"])
        self.assertIn("required", convert_tool["parameters"])
        self.assertIn("file_path", convert_tool["parameters"]["required"])
        
        # Check details of the generate_form_letters tool
        form_tool = next(tool for tool in tools if tool["name"] == "generate_form_letters")
        self.assertIn("description", form_tool)
        self.assertIn("parameters", form_tool)
        self.assertIn("properties", form_tool["parameters"])
        self.assertIn("template_path", form_tool["parameters"]["properties"])
        self.assertIn("recipients", form_tool["parameters"]["properties"])
        self.assertIn("output_format", form_tool["parameters"]["properties"])
        self.assertIn("required", form_tool["parameters"])
        self.assertIn("template_path", form_tool["parameters"]["required"])
        self.assertIn("recipients", form_tool["parameters"]["required"])

if __name__ == "__main__":
    unittest.main()
