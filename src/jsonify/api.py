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

"""
def run_conversion(
    input_dir: str,
    output_dir: str,
    file_types: list,
    conversion_method: str = "python",
    log_dir: str = None
):
    config_loader = ConfigLoader()

    config_loader.base_input_folder = input_dir
    config_loader.base_output_folder = output_dir
    config_loader.file_types = file_types
    config_loader.conversion_method = conversion_method

    if log_dir:
        config_loader.override_log_paths(log_dir)

    return process_file_types(config_loader)
"""

def convert_file(
    file_path: str,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    file_type: Optional[str] = None,
    xml_converter: str = "python",
    xslt_path: Optional[str] = None,
    namespaces: Optional[Dict[str, str]] = None,
    root_tag: Optional[str] = None,
    field_map: Optional[Dict[str, str]] = None,
    **kwargs
) -> Union[Dict, List[Dict]]:

    dir_manager = get_directory_manager()
    
    if not dir_manager.validate_input_file(file_path):
        raise ValueError(f"File must be in the correct input directory for type {file_type}")
    
    if file_type is None:
        file_type = Path(file_path).suffix.lower().lstrip('.')
    
    if output_path is None:
        output_path = str(dir_manager.get_default_output_path(file_path))
    else:
        output_path = Path(output_path)
        if not str(output_path).startswith(str(dir_manager.get_output_dir(file_type))):
            output_path = dir_manager.get_output_dir(file_type) / output_path.name
        output_path = str(output_path)
    
    result = None
    
    if file_type == 'csv':
        output_dir = dir_manager.get_output_dir('csv')
        os.makedirs(output_dir, exist_ok=True)
        result_msg = convert_csv_file(
            file_path,
            str(output_dir),
            fields=fields,
            delimiter=kwargs.get('delimiter', ','),
            skiprows=kwargs.get('skiprows', 0)
        )
        print(result_msg)
        result = {"message": result_msg}
    
    elif file_type == 'txt':
        output_dir = dir_manager.get_output_dir('txt')
        os.makedirs(output_dir, exist_ok=True)
        result_msg = convert_csv_file(
            file_path,
            str(output_dir),
            fields=fields,
            delimiter=kwargs.get('delimiter', '~'),
            skiprows=kwargs.get('skiprows', 0)
        )
        print(result_msg)
        result = {"message": result_msg}
    
    elif file_type == 'xml':
        if xml_converter == 'python':
            result = convert_xml_python(
                file_path,
                fields=fields,
                namespaces=namespaces,
                root_tag=root_tag,
                field_map=field_map
            )
        elif xml_converter == 'xslt':
            if not xslt_path:
                raise ValueError("XSLT converter requires an XSLT file path")
            result = convert_xml_xslt(file_path, xslt_path)
        else:
            raise ValueError(f"Unsupported XML converter: {xml_converter}")
            
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    return result

def convert_csv(
    file_path: str,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    delimiter: str = ",",
    skiprows: int = 0,
    **kwargs
) -> Dict:
    return convert_file(
        file_path,
        output_path,
        fields,
        'csv',
        delimiter=delimiter,
        skiprows=skiprows,
        **kwargs
    )

def convert_xml(
    file_path: str,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    converter: str = "python",
    xslt_path: Optional[str] = None,
    namespaces: Optional[Dict[str, str]] = None,
    root_tag: Optional[str] = None,
    field_map: Optional[Dict[str, str]] = None,
    **kwargs
) -> Dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if converter == 'xslt' and not xslt_path:
        raise ValueError("XSLT converter requires xslt_path parameter")

    if converter == 'xslt':
        from .converter.xslt_converter import apply_xslt_to_xml
        result = apply_xslt_to_xml(file_path, xslt_path)
    else:
        from .converter.python_converter import parse_xml_to_json
        result = parse_xml_to_json(
            file_path,
            field_map=field_map,
            fields=fields,
            namespaces=namespaces,
            root_tag=root_tag
        )

    if output_path:
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{Path(file_path).stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    return result
