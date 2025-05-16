# JSONIFY

A Python package to easily convert different types of files into JSON format.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Structure](#structure)
4. [Usage](#usage)
5. [License](#license)
6. [Contact](#contact)

## Installation

Install via PyPI:

```bash
pip install jsonify
```

Or install locally for development:

```bash
pip install -e .
```

## Structure
The project is organized as follows:

```
jsonify/
├── README.md                  # Project documentation
├── config.ini                 # Configuration file
├── conversion_xslt.xslt       # XSLT stylesheet for XML conversion
├── setup.py                   # Setup script for installation
└── src/
    └── jsonify/
        ├── __init__.py
        ├── config_loader.py   # Configuration manager (in-memory)
        ├── converter/         # Conversion logic for different file types
        │   ├── __init__.py
        │   ├── csv_converter.py      # CSV to JSON conversion
        │   ├── python_converter.py   # XML to JSON (Python method)
        │   ├── xslt_converter.py     # XML to JSON (XSLT method)
        ├── info/              # Folder for log and info files
        ├── json/              # Output folder for JSON files
        ├── api.py             # API definition
        ├── main.py            # Main entry point for the package
        └── types/             # Input folder for files to convert
    └── jsonify.egg-info/      # Metadata for the installed package
```

## Usage
Use the run_conversion function to convert files programmatically:

```python

from jsonify import run_conversion

summary = run_conversion(
    input_dir="data/input",
    output_dir="data/output",
    file_types=["xml", "csv", "txt"],
    conversion_method="python",  # or "xslt"
    log_dir="data/logs"
)
```

**Parameters**:

`input_dir (str)`: Base folder containing subfolders for each file type (e.g. `xml_files/`, `csv_files/`).

`output_dir (str)`: Base folder where the JSON output will be saved.

`file_types (list of str)`: File types to convert. Supported: "xml", "csv", "txt".

`conversion_method (str)`: Conversion method for XML. Either "python" or "xslt".

`log_dir (str, optional)`: Directory to store logs (missing fields, unconverted files, etc.).


## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
GitHub: https://github.com/crpereir/jsonify
