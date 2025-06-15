import unittest
import json
from pathlib import Path
from src.jsonifyer.api import convert_xml
import sys
import io
import unittest.mock

class TestXMLConversion(unittest.TestCase):
    def setUp(self):
        self.xml_path = 'test/input/sample_data.xml'
        self.output_dir = 'test/output/xml_results'
        self.namespaces = {
            'ns': 'urn:hl7-org:v3'
        }
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.expected_data = {
            'id': 'test-123-456-789',
            'title': 'Test Medication Label',
            'effectiveTime': '20240315',
            'versionNumber': '1',
            'manufacturer': {
                'id': '987654321',
                'name': 'Test Pharmaceutical Company'
            },
            'product': {
                'code': 'TEST-123',
                'name': 'TestMed',
                'form': 'TABLET',
                'genericName': 'TESTAMIN',
                'ingredients': [
                    {
                        'name': 'TESTAMIN',
                        'quantity': '500 mg'
                    },
                    {
                        'name': 'LACTOSE'
                    },
                    {
                        'name': 'STARCH'
                    }
                ]
            }
        }

    def tearDown(self):
        temp_input_dir = Path('test/input/temp')
        if temp_input_dir.exists():
            for file in temp_input_dir.glob('*'):
                try:
                    file.unlink()
                except OSError as e:
                    print(f"Warning: Could not delete file {file}: {e}")
            try:
                temp_input_dir.rmdir()
            except OSError as e:
                print(f"Warning: Could not remove directory {temp_input_dir}: {e}")

    def test_xml_full_conversion(self):
        output_file = f"{self.output_dir}/full_conversion.json"
        field_map = {
            'id': './/id/@root',
            'code_code': './/code/@code',
            'code_codeSystem': './/code/@codeSystem',
            'code_displayName': './/formCode/@displayName',
            'organization': './/author/assignedEntity/representedOrganization/name',
            'name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/name',
            'effectiveTime': './/effectiveTime/@value',
            'ingredient_name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/ingredient/ingredientSubstance/name'
        }
        
        temp_input_dir = Path('test/input/temp')
        temp_input_dir.mkdir(parents=True, exist_ok=True)
        temp_input_file = temp_input_dir / 'full_conversion.xml'
        with open(self.xml_path, 'r', encoding='utf-8') as src, open(temp_input_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        
        with io.StringIO() as buf, unittest.mock.patch('sys.stdout', buf):
            result = convert_xml(
                directory_path=str(temp_input_dir),
                output_path=str(Path(output_file).parent),
                namespaces=self.namespaces,
                root_tag='document',
                field_map=field_map
            )
        self.assertIn("Conversion completed", result["message"])
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('id', data)
            self.assertIn('code_code', data)
            self.assertIn('code_codeSystem', data)
            self.assertIn('code_displayName', data)
            self.assertIn('organization', data)
            self.assertIn('name', data)
            self.assertIn('effectiveTime', data)
            self.assertIn('ingredient_name', data)
            
            self.assertEqual(data['id'], 'test-123-456-789')
            self.assertEqual(data['code_code'], 'TEST-123')
            self.assertEqual(data['code_codeSystem'], '2.16.840.1.113883.6.69')
            self.assertEqual(data['code_displayName'], 'TABLET')
            self.assertEqual(data['organization'], 'Test Pharmaceutical Company')
            self.assertEqual(data['name'], 'TestMed')
            self.assertEqual(data['effectiveTime'], '20240315')
            
            self.assertIsInstance(data['ingredient_name'], list)
            self.assertGreaterEqual(len(data['ingredient_name']), 3)
            expected_ingredients = [
                {'name': 'TESTAMIN'},
                {'name': 'LACTOSE'},
                {'name': 'STARCH'}
            ]
            for i, expected in enumerate(expected_ingredients):
                with self.subTest(ingredient=i):
                    self.assertEqual(data['ingredient_name'][i], expected)

    def test_xml_specific_fields(self):
        output_file = f"{self.output_dir}/specific_fields.json"
        fields = ['id', 'title', 'effectiveTime']
        
        temp_input_dir = Path('test/input/temp')
        temp_input_dir.mkdir(parents=True, exist_ok=True)
        temp_input_file = temp_input_dir / 'specific_fields.xml'
        with open(self.xml_path, 'r', encoding='utf-8') as src, open(temp_input_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        
        with io.StringIO() as buf, unittest.mock.patch('sys.stdout', buf):
            result = convert_xml(
                directory_path=str(temp_input_dir),
                output_path=str(Path(output_file).parent),
                namespaces=self.namespaces,
                root_tag='document',
                fields=fields
            )
        self.assertIn("Conversion completed", result["message"])
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(set(data.keys()), set(fields))

    def test_xml_field_mapping(self):
        output_file = f"{self.output_dir}/field_mapping.json"
        field_map = {
            'id': './/id/@root',
            'name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/name',
            'effectiveTime': './/effectiveTime/@value'
        }
        
        temp_input_dir = Path('test/input/temp')
        temp_input_dir.mkdir(parents=True, exist_ok=True)
        temp_input_file = temp_input_dir / 'field_mapping.xml'
        with open(self.xml_path, 'r', encoding='utf-8') as src, open(temp_input_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        
        with io.StringIO() as buf, unittest.mock.patch('sys.stdout', buf):
            result = convert_xml(
                directory_path=str(temp_input_dir),
                output_path=str(Path(output_file).parent),
                namespaces=self.namespaces,
                root_tag='document',
                field_map=field_map
            )
        self.assertIn("Conversion completed", result["message"])
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(set(data.keys()), {'id', 'name', 'effectiveTime'})
            self.assertEqual(data['id'], 'test-123-456-789')
            self.assertEqual(data['name'], 'TestMed')
            self.assertEqual(data['effectiveTime'], '20240315')

    def test_xml_complex_mapping(self):
        output_file = f"{self.output_dir}/complex_mapping.json"
        field_map = {
            'code_code': './/code/@code',
            'code_codeSystem': './/code/@codeSystem',
            'code_displayName': './/formCode/@displayName',
            'organization': './/author/assignedEntity/representedOrganization/name'
        }
        
        temp_input_dir = Path('test/input/temp')
        temp_input_dir.mkdir(parents=True, exist_ok=True)
        temp_input_file = temp_input_dir / 'complex_mapping.xml'
        with open(self.xml_path, 'r', encoding='utf-8') as src, open(temp_input_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        
        with io.StringIO() as buf, unittest.mock.patch('sys.stdout', buf):
            result = convert_xml(
                directory_path=str(temp_input_dir),
                output_path=str(Path(output_file).parent),
                namespaces=self.namespaces,
                root_tag='document',
                field_map=field_map
            )
        self.assertIn("Conversion completed", result["message"])
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(set(data.keys()), {'code_code', 'code_codeSystem', 'code_displayName', 'organization'})
            self.assertEqual(data['code_code'], 'TEST-123')
            self.assertEqual(data['code_codeSystem'], '2.16.840.1.113883.6.69')
            self.assertEqual(data['code_displayName'], 'TABLET')
            self.assertEqual(data['organization'], 'Test Pharmaceutical Company')

if __name__ == '__main__':
    unittest.main()
