import os
import json
import logging
from lxml import etree
from glob import glob

# Configure logging for the module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)


def apply_xslt_to_xml(xml_file: str, repeated_file: str, xslt_file: str) -> dict:
    try:
        # Verify input files exist
        if not os.path.exists(xml_file) or not os.path.exists(xslt_file):
            return {}

        try:
            # Configure XML parser with security settings
            parser = etree.XMLParser(load_dtd=False, no_network=True, resolve_entities=False)
            
            # Read and preprocess XML content
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Remove XML stylesheet reference to prevent external dependencies
            xml_content = xml_content.replace('<?xml-stylesheet type="text/xsl" href="https://www.accessdata.fda.gov/spl/stylesheet/spl.xsl"?>', '')
            xml_doc = etree.fromstring(xml_content.encode('utf-8'), parser)

            # Log first 5 elements for debugging
            for child in xml_doc[:5]:
                logger.info(f"  {child.tag}: {child.attrib}")
                
        except Exception as e:
            return {}
            
        try:
            # Load XSLT transformation file
            xslt_doc = etree.parse(xslt_file)
        except Exception as e:
            return {}
            
        try:
            # Create XSLT transformer
            transform = etree.XSLT(xslt_doc)
        except Exception as e:
            return {}
            
        try:
            # Define namespace for HL7 v3
            ns = {'v3': 'urn:hl7-org:v3'}
            # Apply transformation
            result_tree = transform(xml_doc)
            
            try:
                # Convert transformed XML to JSON
                result_dict = json.loads(str(result_tree))
                return result_dict
            except json.JSONDecodeError as e:
                return {}
                
        except Exception as e:
            return {}
            
    except Exception as e:
        return {}

# ----------------------------------------------------------------------------------------

def process_folder_with_xslt(input_folder, output_folder, log_file, unconverted_log_file, xslt_path):
    # Create output directory
    os.makedirs(output_folder, exist_ok=True)
    # Get all XML files in input folder
    xml_files = glob(os.path.join(input_folder, '*.xml'))
    missing_fields_log = []
    unconverted_files = []
    converted_count = 0

    # Process each XML file
    for xml_file in xml_files:
        try:
            # Convert XML to JSON using XSLT
            json_data = apply_xslt_to_xml(xml_file, xslt_path)
            output_file = os.path.join(output_folder, os.path.basename(xml_file).replace('.xml', '.json'))

            # Save JSON output
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)

            print(f"Converted: {xml_file} -> {output_file}")
            converted_count += 1

            # Check for missing or null fields
            null_or_empty_fields = check_null_and_empty_fields(json_data)
            if null_or_empty_fields:
                missing_fields_log.append({
                    "file": os.path.basename(xml_file),
                    "missing_fields": null_or_empty_fields
                })

        except Exception as e:
            print(f"Error processing {xml_file}: {e}")
            unconverted_files.append(os.path.basename(xml_file))

    # Write missing fields log
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

    # Write unconverted files log
    with open(unconverted_log_file, 'w', encoding='utf-8') as unconverted_log:
        unconverted_log.write(f"-------------------------------------------------------------------------\n")
        unconverted_log.write("Unconverted files:\n")

        for file in unconverted_files:
            unconverted_log.write(f"  - {file}\n")
    
    # Print summary
    print(f"Missing fields in {log_file}")
    print(f"Unconverted files in {unconverted_log_file}")
    print(f"Total of JSON files converted: {converted_count}")
    print(f"Total of unconverted files: {len(unconverted_files)}")



# ----------------------------------------------------------------------------------------

def check_null_and_empty_fields(json_data):
    null_or_empty_fields = []

    def recursive_check(data, parent_key=""):
        # Check dictionary fields
        if isinstance(data, dict):
            for key, value in data.items():
                full_key = f"{parent_key}.{key}" if parent_key else key
                if value is None or (isinstance(value, list) and not value):
                    null_or_empty_fields.append(full_key)
                else:
                    recursive_check(value, full_key)
        # Check list items
        elif isinstance(data, list):
            for index, item in enumerate(data):
                recursive_check(item, f"{parent_key}[{index}]")

    recursive_check(json_data)
    return null_or_empty_fields
