from typing import Any, Dict, List, Optional, Union
import json
import os
from pathlib import Path
from .converter.csv_converter import convert_file_to_json as convert_csv_file
from .converter.python_converter import parse_xml_to_json as convert_xml_python
from .converter.xslt_converter import apply_xslt_to_xml as convert_xml_xslt

def convert_xml(
    directory_path: str,
    repeated_path: str = None,
    repeated_item: str = None,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    converter: str = "python",
    xslt_path: Optional[str] = None,
    namespaces: Optional[Dict[str, str]] = None,
    root_tag: Optional[str] = None,
    field_map: Optional[Dict[str, str]] = None,
    extra_fields: Optional[Dict[str, str]] = None,
    pairs: Optional[Dict[str, str]] = None,
    **kwargs
):
    # Validate input directory exists
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Input directory not found: {directory_path}")

    # Load previously processed IDs to avoid duplicates
    dumped_ids = set()
    if repeated_path and os.path.exists(repeated_path):
        with open(repeated_path, "r", encoding="utf-8") as f:
            dumped_ids = set(line.strip() for line in f if line.strip())

    file_count = 0
    new_ids = []
    result = None
    
    # Process each XML file in the directory
    for file_name in os.listdir(directory_path):
        if file_name.lower().endswith('.xml'):
            file_path = os.path.join(directory_path, file_name)

            # Convert XML using selected converter
            if converter == 'python':
                result = convert_xml_python(
                    file_path,
                    repeated_path,
                    fields=fields,
                    namespaces=namespaces,
                    root_tag=root_tag,
                    field_map=field_map,
                    extra_fields=extra_fields,
                    pairs=pairs,
                )
            elif converter == 'xslt':
                if not xslt_path:
                    raise ValueError("XSLT converter requires an XSLT file path")
                result = convert_xml_xslt(file_path, repeated_path, xslt_path)
            else:
                raise ValueError(f"Unsupported XML converter: {converter}")
            
            print(result)
            
            # Handle duplicate checking if repeated_item is specified
            if repeated_path and repeated_item and result[repeated_item] is not None:
                unique_attr = result[repeated_item]
                # Extract name from list of dictionaries or single dictionary
                if isinstance(unique_attr, list) and len(unique_attr) > 0 and isinstance(unique_attr[0], dict):
                    unique_attr = unique_attr[0].get('name', '')
                elif isinstance(unique_attr, dict) and 'name' in unique_attr:
                    unique_attr = unique_attr['name']
                
                if unique_attr in dumped_ids or unique_attr in new_ids:
                    continue
                
            # Save converted JSON if output path is specified
            if output_path:
                output_dir = Path(output_path)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / f"{Path(file_path).stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)            
                file_count += 1

                if repeated_path:
                    new_ids.append(str(unique_attr))
                
    # Update processed IDs file
    if new_ids and repeated_path:
        with open(repeated_path, 'a', encoding='utf-8') as f:
            for new_id in new_ids:
                f.write(f"{new_id}\n")

    return {"message": f"Conversion completed: {file_count} files created in {output_path}"}

def convert_csv(
    file_path: str,
    repeated_path: str = None,
    repeated_item: str = None,
    output_path: Optional[str] = None,
    fields: Optional[List[str]] = None,
    delimiter: str = ",",
    skiprows: int = 0,
):
    # Validate input file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # Set up output directory
    output_dir = output_path if output_path is not None else os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert CSV to JSON
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
    # Validate input file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")
        
    # Set up output directory
    output_dir = output_path if output_path is not None else os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert TXT to JSON using CSV converter with custom delimiter
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
