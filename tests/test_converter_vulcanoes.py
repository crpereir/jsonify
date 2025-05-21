import os
import json
import pytest
import logging
from pathlib import Path
from jsonify import convert_xml, convert_csv, convert_file
from jsonify.config import init_directory_manager, get_directory_manager
from jsonify.converter.python_converter import parse_xml_to_json
from jsonify.converter.csv_converter import convert_file_to_json
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

def test_convert_csv_vulcanoes(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('csv') / 'vulcanoes.csv'
    output_dir = dir_manager.get_output_dir('csv')

    from jsonify.converter.python_converter import convert_csv
    field_map = {
        'name': 0,
        'location': 1,
        'last_eruption': 2,
        'height': 3,
        'type': 4
    }
    
    result = convert_csv(
        str(input_file),
        str(output_dir),
        skiprows=1,
        field_map=field_map
    )

    files = list(output_dir.glob('*.json'))
    assert len(files) > 0, f"No JSON files were created in {output_dir}"

    record_file = output_dir / 'record_1.json'
    assert record_file.exists(), f"File record_1.json was not created in {output_dir}"

    with open(record_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert isinstance(data, dict), "The JSON file must contain an object"
        assert 'name' in data, "The JSON must contain the 'name' field"
        assert 'location' in data, "The JSON must contain the 'location' field"
        assert 'last_eruption' in data, "The JSON must contain the 'last_eruption' field"

def test_convert_txt_vulcanoes(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('txt') / 'vulcanoes.txt'
    output_dir = dir_manager.get_output_dir('txt')

    result = convert_file(
        str(input_file),
        file_type='txt',
        delimiter='~'
    )

    files = list(output_dir.glob('*.json'))
    assert len(files) > 0, f"No JSON files were created in {output_dir}"

    record_file = output_dir / 'record_1.json'
    assert record_file.exists(), f"File record_1.json was not created in {output_dir}"

    with open(record_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        assert isinstance(data, dict), "The JSON file must contain an object"
        assert 'name' in data, "The JSON must contain the 'name' field"
        assert 'height' in data, "The JSON must contain the 'height' field"
        assert 'type' in data, "The JSON must contain the 'type' field"

def test_convert_xml_vulcanoes_full(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('xml') / 'vulcanoes.xml'
    output_file = dir_manager.get_output_dir('xml') / 'vulcanoes_full.json'

    field_map = {
        'name': './/name',
        'location.country': './/location/country',
        'location.region': './/location/region',
        'location.coordinates.latitude': './/location/coordinates/latitude',
        'location.coordinates.longitude': './/location/coordinates/longitude',
        'last_eruption.date': './/last_eruption/date',
        'last_eruption.magnitude': './/last_eruption/magnitude',
        'last_eruption.casualties': './/last_eruption/casualties',
        'height.meters': './/height/meters',
        'height.feet': './/height/feet',
        'type': './/type',
        'description.summary': './/description/summary',
        'description.history.events': ['.//description/history/event/year', './/description/history/event/description'],
        'description.geology.formation': './/description/geology/formation',
        'description.geology.composition.materials': './/description/geology/composition/material',
        'monitoring.status': './/monitoring/status',
        'monitoring.last_inspection': './/monitoring/last_inspection',
        'monitoring.risk_level': './/monitoring/risk_level',
        'monitoring.sensors': ['.//monitoring/sensors/sensor/type', './/monitoring/sensors/sensor/location', './/monitoring/sensors/sensor/status']
    }

    ET.register_namespace('v3', 'urn:hl7-org:v3')

    print(f"Input file path: {input_file}")
    print(f"Input file exists: {input_file.exists()}")
    
    if input_file.exists():
        tree = ET.parse(input_file)
        root = tree.getroot()
        print(f"Root tag: {root.tag}")
        print(f"Root attributes: {root.attrib}")
        
        for child in root:
            print(f"Child tag: {child.tag}")
    
    print("\nDEBUG: Test field_map:")
    print(f"field_map type: {type(field_map)}")
    print(f"field_map content: {field_map}")

    result = convert_xml(
        str(input_file),
        mode='python',
        field_map=field_map,
        output_dir=str(output_file.parent),
        root_tag='vulcano',
        namespaces={'v3': 'urn:hl7-org:v3'}
    )

    print("\nDEBUG: Test result:")
    print(f"Result type: {type(result)}")
    print(f"Result content: {result}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    assert output_file.exists(), f"Output file was not created in {output_file}"
    
    assert 'name' in result
    assert 'location' in result
    assert 'last_eruption' in result
    assert 'height' in result
    assert 'type' in result
    assert 'description' in result
    assert 'monitoring' in result

    assert 'country' in result['location']
    assert 'region' in result['location']
    assert 'coordinates' in result['location']
    assert 'date' in result['last_eruption']
    assert 'magnitude' in result['last_eruption']
    assert 'meters' in result['height']
    assert 'feet' in result['height']
    assert 'summary' in result['description']
    assert 'history' in result['description']
    assert 'geology' in result['description']
    assert 'status' in result['monitoring']
    assert 'sensors' in result['monitoring']

def test_convert_xml_vulcanoes_parts(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('xml') / 'vulcanoes.xml'
    output_file = dir_manager.get_output_dir('xml') / 'vulcanoes_parts.json'

    fields = [
        './/name',
        './/location',
        './/last_eruption',
        './/height',
        './/type'
    ]

    result = parse_xml_to_json(
        str(input_file),
        fields=fields,
        namespaces={'v3': 'urn:hl7-org:v3'},
        root_tag='vulcano'
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    assert output_file.exists(), f"Output file was not created in {output_file}"

    assert 'name' in result
    assert 'location' in result
    assert 'last_eruption' in result
    assert 'height' in result
    assert 'type' in result

def test_convert_xml_vulcanoes_auto(test_env):
    dir_manager = test_env
    input_file = dir_manager.get_input_dir('xml') / 'vulcanoes.xml'
    output_file = dir_manager.get_output_dir('xml') / 'vulcanoes_auto.json'

    # Converter o arquivo XML inteiro sem especificar campos
    result = convert_file(
        file_path=str(input_file),
        file_type="xml",
        xml_converter="python"
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    assert output_file.exists(), f"Output file was not created at {output_file}"

    # Verificar se o resultado contém a estrutura básica esperada
    assert isinstance(result, dict), "O resultado deve ser um dicionário"
    assert len(result) > 0, "O resultado não deve estar vazio"

    # Verificar se contém as tags principais do documento
    assert 'name' in result, "O resultado deve conter o nome do vulcão"
    assert 'location' in result, "O resultado deve conter a localização"
    assert 'last_eruption' in result, "O resultado deve conter a última erupção"
    assert 'height' in result, "O resultado deve conter a altura"
    assert 'type' in result, "O resultado deve conter o tipo"
    assert 'description' in result, "O resultado deve conter a descrição"
    assert 'monitoring' in result, "O resultado deve conter informações de monitoramento"

    # Verificar a estrutura da localização
    assert 'country' in result['location'], "A localização deve conter o país"
    assert 'region' in result['location'], "A localização deve conter a região"
    assert 'coordinates' in result['location'], "A localização deve conter as coordenadas"
    assert 'latitude' in result['location']['coordinates'], "As coordenadas devem conter a latitude"
    assert 'longitude' in result['location']['coordinates'], "As coordenadas devem conter a longitude"

    # Verificar a estrutura da última erupção
    assert 'date' in result['last_eruption'], "A última erupção deve conter a data"
    assert 'magnitude' in result['last_eruption'], "A última erupção deve conter a magnitude"
    assert 'casualties' in result['last_eruption'], "A última erupção deve conter o número de vítimas"

    # Verificar a estrutura da altura
    assert 'meters' in result['height'], "A altura deve conter os metros"
    assert 'feet' in result['height'], "A altura deve conter os pés"

    # Verificar a estrutura da descrição
    assert 'summary' in result['description'], "A descrição deve conter um resumo"
    assert 'history' in result['description'], "A descrição deve conter o histórico"
    assert 'geology' in result['description'], "A descrição deve conter informações geológicas"

    # Verificar a estrutura do monitoramento
    assert 'status' in result['monitoring'], "O monitoramento deve conter o status"
    assert 'last_inspection' in result['monitoring'], "O monitoramento deve conter a última inspeção"
    assert 'risk_level' in result['monitoring'], "O monitoramento deve conter o nível de risco"
    assert 'sensors' in result['monitoring'], "O monitoramento deve conter os sensores"

    print("Teste de conversão automática de XML concluído com sucesso!")
    print(f"Resultado salvo em: {output_file}")
