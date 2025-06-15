import os
import json
import datetime

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

def append_to_log(log_file_path, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")

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
