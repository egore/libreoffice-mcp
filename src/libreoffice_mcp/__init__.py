from pathlib import Path
import logging
import sys
import click
from .server import serve

@click.command()
@click.option("--libreoffice-path", "-r", type=Path, help="Path to LibreOffice executable", default="soffice")
@click.option("-v", "--verbose", count=True)
def main(libreoffice_path: Path, verbose: bool) -> None:
    """LibreOffice MCP Server"""
    import asyncio

    logging_level = logging.WARN
    if verbose == 1:
        logging_level = logging.INFO
    elif verbose >= 2:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve(libreoffice_path))

if __name__ == "__main__":
    main(False)
