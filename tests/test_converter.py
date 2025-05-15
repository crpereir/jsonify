from jsonify.converter.csv_converter import convert_file_to_json
from jsonify.converter.python_converter import parse_xml_to_json
import json

def test_convert_file_to_json(tmp_path):
    csv_content = "Ingredient,Amount\nSugar,2\nSalt,1"
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    output_dir = tmp_path / "out"
    result = convert_file_to_json(str(csv_file), str(output_dir))
    assert "files created" in result.lower()

def test_convert_txt_to_json(tmp_path):
    txt_content = "Ingredient~Amount\nSugar~2\nSalt~1"
    txt_file = tmp_path / "test.txt"
    txt_file.write_text(txt_content, encoding="utf-8")

    output_dir = tmp_path / "out_txt"
    result = convert_file_to_json(str(txt_file), str(output_dir), delimiter="~")
    assert "files created" in result.lower()

def test_parse_xml_to_json(tmp_path):
    xml_content = """<?xml version="1.0"?>
    <ClinicalDocument xmlns="urn:hl7-org:v3">
        <id root="12345"/>
        <code code="A1" codeSystem="SYS" displayName="Test Drug"/>
        <manufacturedProduct>
            <name>TestDrugName</name>
        </manufacturedProduct>
        <representedOrganization>
            <name>TestOrg</name>
        </representedOrganization>
        <effectiveTime value="20250101"/>
        <ingredient>
            <ingredientSubstance>
                <name>Sugar</name>
                <code code="ING1"/>
            </ingredientSubstance>
        </ingredient>
        <ingredient>
            <ingredientSubstance>
                <name>Salt</name>
                <code code="ING2"/>
            </ingredientSubstance>
        </ingredient>
    </ClinicalDocument>
    """
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(xml_content, encoding="utf-8")

    data = parse_xml_to_json(str(xml_file))
    assert data["name"] == "TestDrugName"
    assert data["organization"] == "TestOrg"
    assert data["ingredients"][0]["name"] == "Sugar"
    assert data["ingredients"][1]["name"] == "Salt"