import os
import json
import logging
from lxml import etree
from glob import glob

print(">>>> Importando módulo xslt_converter <<<<")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

logger.info(">>>> Módulo xslt_converter inicializado <<<<")

def apply_xslt_to_xml(xml_file: str, xslt_file: str) -> dict:
    """
    Apply XSLT transformation to XML file and return the result as a dictionary.
    
    Args:
        xml_file (str): Path to the input XML file
        xslt_file (str): Path to the XSLT file
        
    Returns:
        dict: The transformed data as a dictionary
    """
    try:
        # Check if files exist
        if not os.path.exists(xml_file):
            logger.error(f"XML file not found: {xml_file}")
            return {}
            
        if not os.path.exists(xslt_file):
            logger.error(f"XSLT file not found: {xslt_file}")
            return {}
            
        logger.info(f"Processing XML file: {xml_file}")
        logger.info(f"Using XSLT file: {xslt_file}")
        
        # Parse XML
        try:
            # Create parser with specific options
            parser = etree.XMLParser(load_dtd=False, no_network=True, resolve_entities=False)
            
            # Read XML content
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Remove XML stylesheet declaration if present
            xml_content = xml_content.replace('<?xml-stylesheet type="text/xsl" href="https://www.accessdata.fda.gov/spl/stylesheet/spl.xsl"?>', '')
            
            # Parse XML
            xml_doc = etree.fromstring(xml_content.encode('utf-8'), parser)
            logger.info(f"XML file parsed successfully. Root element: {xml_doc.tag}")
            logger.info(f"XML root namespace: {xml_doc.nsmap}")
            
            # Debug: Print first few elements
            logger.info("First few elements in XML:")
            for child in xml_doc[:5]:
                logger.info(f"  {child.tag}: {child.attrib}")
                
        except Exception as e:
            logger.error(f"Error parsing XML file: {str(e)}")
            return {}
            
        # Parse XSLT
        try:
            xslt_doc = etree.parse(xslt_file)
            logger.info("XSLT file parsed successfully")
            logger.info(f"XSLT root element: {xslt_doc.getroot().tag}")
            logger.info(f"XSLT namespaces: {xslt_doc.getroot().nsmap}")
        except Exception as e:
            logger.error(f"Error parsing XSLT file: {str(e)}")
            return {}
            
        # Create transformer
        try:
            transform = etree.XSLT(xslt_doc)
            logger.info("XSLT transformer created successfully")
        except Exception as e:
            logger.error(f"Error creating XSLT transformer: {str(e)}")
            return {}
            
        # Apply transformation
        try:
            # Register the namespace
            ns = {'v3': 'urn:hl7-org:v3'}
            logger.info(f"Applying transformation with namespaces: {ns}")
            
            result_tree = transform(xml_doc)
            logger.info(f"XSLT transformation applied successfully. Result tree type: {type(result_tree)}")
            logger.info(f"Result tree content: {str(result_tree)}")
            
            # Save raw output for debugging
            debug_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(xml_file))), 'debug_xslt_output.json')
            os.makedirs(os.path.dirname(debug_file), exist_ok=True)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(str(result_tree))
            logger.info(f"Debug output saved to: {debug_file}")
            
            # Parse the result as JSON
            try:
                result_dict = json.loads(str(result_tree))
                logger.info("Result successfully parsed as JSON")
                logger.info(f"Result keys: {list(result_dict.keys()) if result_dict else 'empty'}")
                return result_dict
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing result as JSON: {str(e)}")
                logger.error(f"Raw result: {str(result_tree)}")
                return {}
                
        except Exception as e:
            logger.error(f"Error applying XSLT transformation: {str(e)}")
            return {}
            
    except Exception as e:
        logger.error(f"Unexpected error in apply_xslt_to_xml: {str(e)}")
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