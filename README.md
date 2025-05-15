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

## Configuration
The package reads input files from a specified input directory and outputs JSON files into an output directory. Configuration can be done via a config file.

Example `config.ini` snippet:
```ini
[general]
conversion_method=python
file_type=xml, csv

[folders]
base_input_folder=/path/to/input/folder
base_output_folder=/path/to/output/folder

[log_files]
log_file=/path/to/logs/missing_fields_log.txt
unconverted_file=/path/to/logs/unconverted_files.txt
processed_medications_file=/path/to/logs/drugs.txt
processing_summary_file=/path/to/logs/summary.txt
```

**Configuration Parameters:**
- `conversion_method`: Specifies the method to use for xml **(only)** conversion. Options are "python" or "xslt".
- `file_type`: Specifies the file types to convert. Options are "csv", "xml".
- `base_input_folder`: Specifies the base directory where the input files are located.
- `base_output_folder`: Specifies the base directory where the output files will be saved.
- `log_file`: Specifies the file path to save the log of missing fields.
- `unconverted_file`: Specifies the file path to save the list of unconverted files.
- `processed_medications_file`: Specifies the file path to save the list of processed drugs.
- `processing_summary_file`: Specifies the file path to save the summary of the processing.

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
        ├── config_loader.py   # Loads and parses configuration files
        ├── converter/         # Conversion logic for different file types
        │   ├── __init__.py
        │   ├── csv_converter.py      # CSV to JSON conversion
        │   ├── python_converter.py   # XML to JSON (Python method)
        │   ├── xslt_converter.py     # XML to JSON (XSLT method)
        ├── info/              # Folder for log and info files
        ├── json/              # Output folder for JSON files
        ├── main.py            # Main entry point for the package
        └── types/             # Input folder for files to convert
    └── jsonify.egg-info/      # Metadata for the installed package
```

## Usage
As a command line tool:
```bash
jsonify --config config.ini --input-dir path/to/input --output-dir path/to/output
```

As a Python Module:
```python
from jsonify.main import main

if __name__ == "__main__":
    main()
```

## License
MIT License © Carolina Pereira

## Contact
GitHub: https://github.com/crpereir/jsonify
