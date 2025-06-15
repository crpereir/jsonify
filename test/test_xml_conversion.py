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
        # Ensure output directory exists
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

    def test_xml_full_conversion(self):
        output_file = f"{self.output_dir}/full_conversion.json"
        field_map = {
            'id': './/id/@root',
            'title': './/title[1]',
            'effectiveTime': './/effectiveTime/@value',
            'versionNumber': './/versionNumber/@value',
            'manufacturer_id': './/author/assignedEntity/representedOrganization/id/@extension',
            'manufacturer_name': './/author/assignedEntity/representedOrganization/name',
            'product_code': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/code/@code',
            'product_name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/name',
            'product_form': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/formCode/@displayName',
            'product_generic_name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/asEntityWithGeneric/genericMedicine/name',
            'ingredient_name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/ingredient/ingredientSubstance/name',
            'ingredient_quantity': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/ingredient/quantity/numerator/@value'
        }
        
        # Create a temporary copy of the input file with a different name
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
        
        # Clean up temporary files
        temp_input_file.unlink()
        temp_input_dir.rmdir()
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Check basic fields
            self.assertIn('id', data)
            self.assertIn('title', data)
            self.assertIn('effectiveTime', data)
            self.assertIn('versionNumber', data)
            
            # Check manufacturer fields
            self.assertIn('manufacturer_id', data)
            self.assertIn('manufacturer_name', data)
            
            # Check product fields
            self.assertIn('product_code', data)
            self.assertIn('product_name', data)
            self.assertIn('product_form', data)
            self.assertIn('product_generic_name', data)
            
            # Check ingredient fields
            self.assertIn('ingredient_name', data)
            self.assertIn('ingredient_quantity', data)
            
            # Verify some specific values
            self.assertEqual(data['id'], 'test-123-456-789')
            self.assertEqual(data['effectiveTime'], '20240315')
            self.assertEqual(data['versionNumber'], '1')
            self.assertEqual(data['manufacturer_id'], '987654321')
            self.assertEqual(data['manufacturer_name'], 'Test Pharmaceutical Company')
            self.assertEqual(data['product_code'], 'TEST-123')
            self.assertEqual(data['product_name'], 'TestMed')
            self.assertEqual(data['product_form'], 'TABLET')
            self.assertEqual(data['product_generic_name'], 'TESTAMIN')

    def test_xml_specific_fields(self):
        output_file = f"{self.output_dir}/specific_fields.json"
        fields = ['id', 'title', 'effectiveTime']
        
        # Create a temporary copy of the input file with a different name
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
        
        # Clean up temporary files
        temp_input_file.unlink()
        temp_input_dir.rmdir()
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(set(data.keys()), set(fields))

    def test_xml_field_mapping(self):
        output_file = f"{self.output_dir}/field_mapping.json"
        field_map = {
            'id': './/id/@root',
            'title': './/title[1]',
            'manufacturer_id': './/author/assignedEntity/representedOrganization/id/@extension',
            'manufacturer_name': './/author/assignedEntity/representedOrganization/name'
        }
        
        # Create a temporary copy of the input file with a different name
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
        
        # Clean up temporary files
        temp_input_file.unlink()
        temp_input_dir.rmdir()
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('id', data)
            self.assertIn('title', data)
            self.assertIn('manufacturer_id', data)
            self.assertIn('manufacturer_name', data)

    def test_xml_complex_mapping(self):
        output_file = f"{self.output_dir}/complex_mapping.json"
        field_map = {
            'id': './/id/@root',
            'code_code': './/code/@code',
            'code_codeSystem': './/code/@codeSystem',
            'code_displayName': './/formCode/@displayName',
            'organization': './/author/assignedEntity/representedOrganization/name',
            'name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/name',
            'effectiveTime': './/effectiveTime/@value',
            'ingredient_name': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/ingredient/ingredientSubstance/name',
            'ingredient_code': './/component/structuredBody/component/section/subject/manufacturedProduct/manufacturedProduct/ingredient/ingredientSubstance/code/@code'
        }
        
        # Create a temporary copy of the input file with a different name
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
        
        # Clean up temporary files
        temp_input_file.unlink()
        temp_input_dir.rmdir()
        
        self.assertTrue(Path(output_file).exists(), "Output file should be created")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Define expected values
            expected_values = {
                'id': 'test-123-456-789',
                'code_code': 'TEST-123',
                'code_codeSystem': '2.16.840.1.113883.6.69',
                'code_displayName': 'TABLET',
                'organization': 'Test Pharmaceutical Company',
                'name': 'TestMed',
                'effectiveTime': '20240315'
            }
            
            # Create filtered data with only the fields we want to test
            filtered_data = {k: v for k, v in data.items() if k in expected_values}
            
            # Verify basic fields
            self.assertDictEqual(filtered_data, expected_values)
            
            # Verify ingredient_name separately
            self.assertIn('ingredient_name', data)
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

if __name__ == '__main__':
    unittest.main()
