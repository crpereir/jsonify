import os
import json
import pytest
import logging
from pathlib import Path
from jsonifyer import convert_xml, convert_csv, convert_file
from jsonifyer.config import init_directory_manager, get_directory_manager
from jsonifyer.converter.python_converter import parse_xml_to_json
import xml.etree.ElementTree as ET

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def test_env():

    base_dir = Path(__file__).parent
    
    dir_manager = init_directory_manager(str(base_dir))
    
    for dir_type in ['csv_files', 'xml_files', 'text_files']:
        input_dir = base_dir / 'input' / dir_type
        output_dir = base_dir / 'output' / dir_type
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    
    for dir_type in ['csv_files', 'xml_files', 'text_files']:
        output_dir = base_dir / 'output' / dir_type
        if output_dir.exists():
            files = list(output_dir.glob('*.json'))
            if files:
                logger.info(f"\n{dir_type}:")
                for f in files:
                    logger.info(f"  - {f.name}")
    
    return dir_manager

def test_convert_xml_specific_fields(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd.xml'
    output_file = dir_manager.get_output_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd_python.json'

    fields = [
        './/id/@root',
        './/code/@code',
        './/code/@codeSystem',
        './/code/@displayName',
        './/author/assignedEntity/representedOrganization/name',
        './/effectiveTime/@value',
    ]

    result = parse_xml_to_json(
        str(input_file),
        fields=fields,
        namespaces=None,
        root_tag='document'
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    assert output_file.exists(), f"Output file was not created at {output_file}"

    assert 'root' in result
    assert 'code' in result
    assert 'codeSystem' in result
    assert 'displayName' in result
    assert 'name' in result
    assert 'value' in result

def test_convert_csv(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('csv') / 'purplebook-search-march-data-download.csv'
    output_dir = dir_manager.get_output_dir('csv')

    result = convert_csv(str(input_file), skiprows=3)

    files = list(output_dir.glob('*.json'))
    assert len(files) > 0, f"No JSON files were created in {output_dir}"

    record_file = output_dir / 'record_1.json'
    assert record_file.exists(), f"File record_1.json was not created in {output_dir}"

    with open(record_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert isinstance(data, dict), "The JSON file must contain an object"

def test_convert_txt(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('txt') / 'products.txt'
    output_dir = dir_manager.get_output_dir('txt')
    
    result = convert_file(str(input_file), file_type='txt')
    
    files = list(output_dir.glob('record_*.json'))
    assert len(files) > 0, f"No JSON files were created in {output_dir}"
    
    with open(files[0], 'r', encoding='utf-8') as f:
        saved_result = json.load(f)
        assert isinstance(saved_result, dict)

def test_convert_xml_structured_alymsys(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd.xml'
    output_file = dir_manager.get_output_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd_python_structured.json'

    ns = {'': 'urn:hl7-org:v3'}
    field_map = {
        'id': './/id/@root',
        'code.code': './/code/@code',
        'code.codeSystem': './/code/@codeSystem',
        'code.displayName': './/code/@displayName',
        'organization': './/author/assignedEntity/representedOrganization/name',
        'name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/name',
        'effectiveTime': './/effectiveTime/@value'
    }

    result = parse_xml_to_json(
        str(input_file),
        field_map=field_map,
        namespaces=None,
        root_tag='document'
    )

    if isinstance(result.get('name'), list):
        result['name'] = result['name'][0]

    tree = ET.parse(str(input_file))
    root = tree.getroot()
    ingredients = []
    manufactured_products = root.findall('.//component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct', ns)
    for product in manufactured_products:
        ing_elems = product.findall('ingredient', ns)
        for ing in ing_elems:
            sub = ing.find('ingredientSubstance', ns)
            if sub is not None:
                ing_name = ''.join(sub.find('name', ns).itertext()).strip() if sub.find('name', ns) is not None else None
                ing_code = sub.find('code', ns).attrib.get('code') if sub.find('code', ns) is not None else None
                if {'name': ing_name, 'code': ing_code} not in ingredients:
                    ingredients.append({'name': ing_name, 'code': ing_code})
    result['ingredients'] = ingredients

    def extract_section_text(code_value):
        for section in root.findall('.//section', ns):
            code = section.find('code', ns)
            if code is not None and code.attrib.get('code') == code_value:
                text_elem = section.find('text', ns)
                if text_elem is not None and ''.join(text_elem.itertext()).strip():
                    return ''.join(text_elem.itertext()).strip()
                excerpt_elem = section.find('excerpt', ns)
                if excerpt_elem is not None:
                    return ' '.join([t.strip() for t in excerpt_elem.itertext() if t.strip()])
        return None

    result['indications'] = extract_section_text('34067-9')
    result['contraindications'] = extract_section_text('34068-7')
    result['warningsAndPrecautions'] = extract_section_text('34069-5')
    result['adverseReactions'] = extract_section_text('34070-3')

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    expected = {
        "id": "0017a82d-4f35-4d17-ab5c-4744dc0effdd",
        "code": {
            "code": "34391-3",
            "codeSystem": "2.16.840.1.113883.6.1",
            "displayName": "HUMAN PRESCRIPTION DRUG LABEL"
        },
        "name": "ALYMSYS",
        "organization": "Amneal Pharmaceuticals LLC",
        "effectiveTime": "20220423",
        "ingredients": [
            {"name": "BEVACIZUMAB", "code": "2S9ZZM9Q9V"},
            {"name": "TREHALOSE DIHYDRATE", "code": "7YIN7J07X4"},
            {"name": "POLYSORBATE 20", "code": "7T1F30V5YH"},
            {"name": "SODIUM PHOSPHATE, DIBASIC, ANHYDROUS", "code": "22ADO53M6F"},
            {"name": "SODIUM PHOSPHATE, MONOBASIC, MONOHYDRATE", "code": "593YOG76RN"},
            {"name": "WATER", "code": "059QF0KO0R"}
        ],
        "indications": result["indications"],
        "contraindications": result["contraindications"],
        "warningsAndPrecautions": result["warningsAndPrecautions"],
        "adverseReactions": result["adverseReactions"]
    }

    for k in ["id", "code", "name", "organization", "effectiveTime"]:
        assert result[k] == expected[k]

    assert len(result["ingredients"]) == len(expected["ingredients"])
    for r, e in zip(result["ingredients"], expected["ingredients"]):
        assert r["name"] == e["name"]
        assert r["code"] == e["code"]

    for k in ["indications", "contraindications", "warningsAndPrecautions", "adverseReactions"]:
        assert result[k] is not None and isinstance(result[k], str) and len(result[k]) > 0

def test_convert_xml_with_xslt(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd.xml'
    output_file = dir_manager.get_output_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd_xslt.json'
    xslt_file = Path(__file__).parent / 'conversion_xslt.xslt'

    result = convert_xml(
        str(input_file),
        converter='xslt',
        xslt_path=str(xslt_file)
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    assert output_file.exists(), f"Output file was not created at {output_file}"

    assert 'id' in result
    assert 'code' in result
    assert isinstance(result['code'], dict)
    assert 'code' in result['code']
    assert 'codeSystem' in result['code']
    assert 'displayName' in result['code']
    assert 'title' in result
    assert 'effectiveTime' in result
    assert 'ingredients' in result
    assert isinstance(result['ingredients'], list)
    assert 'contraindications' in result
    assert isinstance(result['contraindications'], list)
    assert 'warningsAndPrecautions' in result
    assert isinstance(result['warningsAndPrecautions'], list)
    assert 'adverseReactions' in result
    assert isinstance(result['adverseReactions'], list)

    assert result['id'] == '0017a82d-4f35-4d17-ab5c-4744dc0effdd'
    assert result['code']['code'] == '34391-3'
    assert result['code']['codeSystem'] == '2.16.840.1.113883.6.1'
    assert result['code']['displayName'] == 'HUMAN PRESCRIPTION DRUG LABEL'
    assert result['effectiveTime'] == '20220423'

    assert len(result['ingredients']) > 0
    for ingredient in result['ingredients']:
        assert 'name' in ingredient
        assert 'code' in ingredient
        assert isinstance(ingredient['name'], str)
        assert isinstance(ingredient['code'], str)

    assert len(result['contraindications']) > 0
    assert len(result['warningsAndPrecautions']) > 0
    assert len(result['adverseReactions']) > 0

def test_convert_xml_auto(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd.xml'
    output_file = dir_manager.get_output_dir('xml') / '0017a82d-4f35-4d17-ab5c-4744dc0effdd_auto.json'

    result = convert_file(
        file_path=str(input_file),
        file_type="xml",
        xml_converter="python"
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    assert output_file.exists(), f"Output file was not created at {output_file}"

    assert isinstance(result, dict), "The result should be a dictionary"
    assert len(result) > 0, "The result should not be empty"

    assert 'id' in result, "The result must contain the document ID"
    assert 'code' in result, "The result must contain the code"
    assert 'effectiveTime' in result, "The result must contain the effective time"

    assert isinstance(result['code'], dict), "The code must be a dictionary"
    assert 'code' in result['code'], "The code must contain the code value"
    assert 'codeSystem' in result['code'], "The code must contain the code system"
    assert 'displayName' in result['code'], "The code must contain the display name"

    assert 'component' in result, "The result must contain components"
    assert 'structuredBody' in result['component'], "The result must contain the structured body"

    print("XML automatic conversion test completed successfully!")
    print(f"Result saved at: {output_file}")
