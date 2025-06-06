"""
jsonify - A flexible Python package for converting various file formats to JSON.

This package provides a simple and extensible way to convert different file formats
to JSON, with support for field selection and format-specific options.

Currently supported formats:
- CSV files
- XML files (with Python or XSLT conversion)
"""

from .api import (
    convert_csv,
    convert_xml,
    convert_txt
)

__version__ = '0.1.7'
__all__ = ['convert_csv', 'convert_xml', 'convert_txt']
