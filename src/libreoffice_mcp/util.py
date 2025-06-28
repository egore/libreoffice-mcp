"""Utility functions for file operations."""

from pathlib import Path
import os
import tempfile
import uuid

def ensure_directory(directory_path: str) -> None:
    """Ensure the specified directory exists."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_temp_directory() -> str:
    """Get a temporary directory for file operations."""
    temp_dir = os.path.join(tempfile.gettempdir(), "libreoffice_mcp", str(uuid.uuid4()))
    ensure_directory(temp_dir)
    return temp_dir