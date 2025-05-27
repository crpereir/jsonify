import os
import json
import datetime
from glob import glob
from .converter.python_converter import parse_xml_to_json, check_null_fields
from .converter.xslt_converter import apply_xslt_to_xml
from .converter.csv_converter import convert_file_to_json

def normalize_name(name):
    return name.lower().strip() if name else None

def load_processed_names(file_path):
    processed = set()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                item_name = normalize_name(line)
                if item_name:
                    processed.add(item_name)
    return processed

def extract_name_from_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return normalize_name(data.get('Proper Name'))
    return None

def extract_name_from_xml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return normalize_name(data.get('name'))
    return None

def write_log_summary(log_file_path, summary):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(f"\n---------------------- Processing Summary [{timestamp}] ----------------------\n")
        for key, value in summary.items():
            if isinstance(value, dict):
                f.write(f"{key}:\n")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        f.write(f"  {sub_key}:\n")
                        for detail_key, detail_value in sub_value.items():
                            f.write(f"    {detail_key}: {detail_value}\n")
                    else:
                        f.write(f"  {sub_key}: {sub_value}\n")
            else:
                f.write(f"{key}: {value}\n")
        f.write(f"\n------------------------------------------------------------------------------\n")

def append_to_log(log_file_path, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

def process_file_types(config_loader):
    log_file = config_loader.get_log_file_path()
    unconverted_file = config_loader.get_unconverted_file_path()
    processed_names_file = config_loader.get_processed_names_file_path()
    processing_summary_file = config_loader.get_summary_file_path()
    conversion_method = config_loader.get_conversion_method()
    file_types = config_loader.get_file_types()

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    os.makedirs(os.path.dirname(unconverted_file), exist_ok=True)
    os.makedirs(os.path.dirname(processed_names_file), exist_ok=True)

    missing_fields_log = []
    unconverted_files = []
    file_counters = {ft: _init_file_counter() for ft in file_types}
    total_counters = _init_file_counter()

    for file_type in file_types:
        _process_file_type(
            file_type, config_loader, conversion_method, log_file,
            unconverted_file, processed_names_file, missing_fields_log,
            file_counters, total_counters, unconverted_files
        )

    _write_unconverted_files(unconverted_file, unconverted_files)
    _write_missing_fields_log(log_file, missing_fields_log)
    summary = _build_summary(total_counters, file_counters)
    write_log_summary(processing_summary_file, summary)
    return summary

def _init_file_counter():
    return {
        'initial': 0, 'converted': 0, 'unconverted': 0, 'skipped': 0, 'removed_duplicates': 0,
        'files_before_cleaning': 0, 'files_after_cleaning': 0
    }

def _process_file_type(
    file_type, config_loader, conversion_method,
    log_file, unconverted_file, processed_names_file,
    missing_fields_log, file_counters, total_counters, unconverted_files
):
    input_folder = config_loader.get_input_folder_for_type(file_type)
    output_folder = config_loader.get_output_folder_for_type(file_type)
    os.makedirs(output_folder, exist_ok=True)

    input_files = glob(os.path.join(input_folder, f'*.{file_type}'))
    file_counters[file_type]['initial'] = len(input_files)
    total_counters['initial'] += len(input_files)

    append_to_log(log_file, f"Processing {file_type} files: {len(input_files)} found in {input_folder}")

    for input_file in input_files:
        _convert_file(
            file_type, input_file, output_folder, conversion_method,
            log_file, unconverted_file, missing_fields_log,
            file_counters, total_counters, unconverted_files
        )

    files_before = len(glob(os.path.join(output_folder, '*.json')))
    file_counters[file_type]['files_before_cleaning'] = files_before
    total_counters['files_before_cleaning'] += files_before

    removed = clean_repeated_items(processed_names_file, output_folder, file_type, log_file)
    file_counters[file_type]['removed_duplicates'] = removed
    total_counters['removed_duplicates'] += removed

    files_after = len(glob(os.path.join(output_folder, '*.json')))
    file_counters[file_type]['files_after_cleaning'] = files_after
    total_counters['files_after_cleaning'] += files_after

def _convert_file(
    file_type, input_file, output_folder, conversion_method,
    log_file, unconverted_file, missing_fields_log,
    file_counters, total_counters, unconverted_files
):
    output_file = os.path.join(output_folder, os.path.basename(input_file).replace(f'.{file_type}', '.json'))
    try:
        if file_type == 'xml':
            if conversion_method == 'xslt':
                xslt_path = os.path.join(os.path.dirname(__file__), 'conversion_xslt.xslt')
                json_data = apply_xslt_to_xml(xslt_path, input_file)
            else:
                json_data = parse_xml_to_json(input_file)

            missing_fields = check_null_fields(json_data)
            if missing_fields:
                missing_fields_log.append(f"File: {input_file}, Missing fields: {', '.join(missing_fields)}")

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)

            file_counters[file_type]['converted'] += 1
            total_counters['converted'] += 1

        elif file_type == 'csv':
            if convert_file_to_json(input_file, output_folder, delimiter=",", skiprows=3):
                file_counters[file_type]['converted'] += 1
                total_counters['converted'] += 1
            else:
                raise ValueError("Failed CSV conversion")

        elif file_type == 'txt':
            if convert_file_to_json(input_file, output_folder, delimiter="~"):
                file_counters[file_type]['converted'] += 1
                total_counters['converted'] += 1
            else:
                raise ValueError("Failed TXT conversion")

    except Exception as e:
        file_counters[file_type]['unconverted'] += 1
        total_counters['unconverted'] += 1
        unconverted_files.append(input_file)
        with open(unconverted_file, 'a', encoding='utf-8') as f:
            f.write(f"{input_file} - Error: {str(e)}\n")

def _write_unconverted_files(unconverted_file, unconverted_files):
    with open(unconverted_file, 'w', encoding='utf-8') as f:
        for file in unconverted_files:
            f.write(f"{file}\n")

def _write_missing_fields_log(log_file, missing_fields_log):
    with open(log_file, 'w', encoding='utf-8') as f:
        for log_entry in missing_fields_log:
            f.write(f"{log_entry}\n")

def _build_summary(total_counters, file_counters):
    return {
        "Total initial files": total_counters['initial'],
        "Total converted files": total_counters['converted'],
        "Total unconverted files": total_counters['unconverted'],
        "Total files before cleaning": total_counters['files_before_cleaning'],
        "Total files after cleaning": total_counters['files_after_cleaning'],
        "Total duplicates removed": total_counters['removed_duplicates'],
        "Breakdown by file type": file_counters
    }

def clean_repeated_items(processed_names_file, output_folder, file_type, log_file):
    processed_names = load_processed_names(processed_names_file)
    removed_count = 0

    for file in os.listdir(output_folder):
        if not file.endswith('.json'):
            continue

        file_path = os.path.join(output_folder, file)
        try:
            if file_type == "csv":
                item_name = extract_name_from_csv(file_path)
            else:
                item_name = extract_name_from_xml(file_path)

            if item_name and (item_name in processed_names):
                os.remove(file_path)
                removed_count += 1
                append_to_log(log_file, f"Removed duplicate: {file_path} - Name: {item_name}")
            elif item_name:
                with open(processed_names_file, 'a', encoding='utf-8') as f:
                    f.write(f"{item_name}\n")
                processed_names.add(item_name)

        except Exception as e:
            append_to_log(log_file, f"Error processing {file_path}: {str(e)}")

    return removed_count
