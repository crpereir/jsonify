from .config_loader import ConfigLoader
from .main import process_file_types
from typing import Any, Dict, List, Optional, Union
import json
import os
from pathlib import Path
from .converter.csv_converter import convert_file_to_json as convert_csv_file
from .converter.python_converter import parse_xml_to_json as convert_xml_python
from .converter.xslt_converter import apply_xslt_to_xml as convert_xml_xslt
from .config import get_directory_manager

def convert_xml(
    file_path: str,
    repeated_path: str = None,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    converter: str = "python",
    xslt_path: Optional[str] = None,
    namespaces: Optional[Dict[str, str]] = None,
    root_tag: Optional[str] = None,
    field_map: Optional[Dict[str, str]] = None,
    **kwargs
):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    result = None
    if converter == 'python':
        result = convert_xml_python(
            file_path,
            repeated_path,
            fields=fields,
            namespaces=namespaces,
            root_tag=root_tag,
            field_map=field_map
        )
    elif converter == 'xslt':
        if not xslt_path:
            raise ValueError("XSLT converter requires an XSLT file path")
        result = convert_xml_xslt(file_path, repeated_path, xslt_path)
    else:
        raise ValueError(f"Unsupported XML converter: {converter}")
        
    if output_path:
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{Path(file_path).stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    return result



def convert_csv(
    file_path: str,
    repeated_path: str = None,
    repeated_item: str = None,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    delimiter: str = ",",
    skiprows: int = 0,
):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    output_dir = output_path if output_path is not None else os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)
    result_msg = convert_csv_file(
        file_path,
        repeated_path,
        repeated_item,
        str(output_dir),
        fields,
        delimiter,
        skiprows
    )
    print(result_msg)
    return {"message": result_msg}



def convert_txt(
    file_path: str,
    repeated_path: str = None,
    repeated_item: str = None,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    delimiter: str = "~",
    skiprows: int = 0
):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
    output_dir = output_path if output_path is not None else os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)
    result_msg = convert_csv_file(
        file_path,
        repeated_path,
        repeated_item,
        str(output_dir),
        fields,
        delimiter,
        skiprows
    )
    print(result_msg)
    return {"message": result_msg}
