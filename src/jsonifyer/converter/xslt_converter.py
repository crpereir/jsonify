import os
import json
import logging
from lxml import etree
from glob import glob

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)


def apply_xslt_to_xml(xml_file: str, xslt_file: str) -> dict:
    try:
        if not os.path.exists(xml_file):
            return {}
            
        if not os.path.exists(xslt_file):
            return {}

        try:
            parser = etree.XMLParser(load_dtd=False, no_network=True, resolve_entities=False)
            
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            xml_content = xml_content.replace('<?xml-stylesheet type="text/xsl" href="https://www.accessdata.fda.gov/spl/stylesheet/spl.xsl"?>', '')
            xml_doc = etree.fromstring(xml_content.encode('utf-8'), parser)

            for child in xml_doc[:5]:
                logger.info(f"  {child.tag}: {child.attrib}")
                
        except Exception as e:
            return {}
            
        try:
            xslt_doc = etree.parse(xslt_file)
        except Exception as e:
            return {}
            
        try:
            transform = etree.XSLT(xslt_doc)
        except Exception as e:
            return {}
            
        try:
            ns = {'v3': 'urn:hl7-org:v3'}
            result_tree = transform(xml_doc)
            
            try:
                result_dict = json.loads(str(result_tree))
                return result_dict
            except json.JSONDecodeError as e:
                return {}
                
        except Exception as e:
            return {}
            
    except Exception as e:
        return {}

# ----------------------------------------------------------------------------------------

def check_null_and_empty_fields(json_data):
    null_or_empty_fields = []

    def recursive_check(data, parent_key=""):
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                if value is None or (isinstance(value, list) and not value):
                    null_or_empty_fields.append(full_key)
                else:
                    recursive_check(value, full_key)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                recursive_check(item, f"{parent_key}[{index}]")

    recursive_check(json_data)
    return null_or_empty_fields

# ----------------------------------------------------------------------------------------

def process_folder_with_xslt(input_folder, output_folder, log_file, unconverted_log_file, xslt_path):
    os.makedirs(output_folder, exist_ok=True)
    xml_files = glob(os.path.join(input_folder, '*.xml'))
    missing_fields_log = []
    unconverted_files = []
    converted_count = 0

    for xml_file in xml_files:
        try:
            json_data = apply_xslt_to_xml(xml_file, xslt_path)
            output_file = os.path.join(output_folder, os.path.basename(xml_file).replace('.xml', '.json'))

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)

            print(f"Converted: {xml_file} -> {output_file}")
            converted_count += 1

            null_or_empty_fields = check_null_and_empty_fields(json_data)
            if null_or_empty_fields:
                missing_fields_log.append({
                    "file": os.path.basename(xml_file),
                    "missing_fields": null_or_empty_fields
                })

        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
            unconverted_files.append(os.path.basename(xml_file))

    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"-------------------------------------------------------------------------\n")
        log.write(f"Total JSON files converted: {converted_count}\n")
        log.write(f"-------------------------------------------------------------------------\n\n")

        log.write("Files with missing fields:\n")
        for entry in missing_fields_log:
            log.write(f"File: {entry['file']}\n")
            log.write("Missing fields:\n")
            for field in entry['missing_fields']:
                log.write(f"  - {field}\n")
            log.write("\n")

    with open(unconverted_log_file, 'w', encoding='utf-8') as unconverted_log:
        unconverted_log.write(f"-------------------------------------------------------------------------\n")
        unconverted_log.write("Unconverted files:\n")

        for file in unconverted_files:
            unconverted_log.write(f"  - {file}\n")
    
    print(f"Missing fields in {log_file}")
    print(f"Unconverted files in {unconverted_log_file}")
    print(f"Total of JSON files converted: {converted_count}")
    print(f"Total of unconverted files: {len(unconverted_files)}")