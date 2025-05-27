"""
jsonify - A flexible Python package for converting various file formats to JSON.

This package provides a simple and extensible way to convert different file formats
to JSON, with support for field selection and format-specific options.

Currently supported formats:
- CSV files
- XML files (with Python or XSLT conversion)
"""

from .api import (
    convert_file,
    convert_csv,
    convert_xml
)

__version__ = '0.1.0'
__all__ = ['convert_file', 'convert_csv', 'convert_xml']
