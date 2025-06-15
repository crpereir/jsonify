import unittest
import json
from pathlib import Path
from src.jsonifyer.api import convert_txt

class TestTXTConversion(unittest.TestCase):
    def setUp(self):
        self.txt_path = 'test/input/sample_data.txt'
        self.output_dir = 'test/output/txt_results'
        self.expected_data = [
            {
                "Name": "John Doe",
                "Age": 30,
                "City": "Lisbon",
                "Occupation": "Developer",
                "Skills": "Python, JavaScript, SQL"
            },
            {
                "Name": "Maria Silva",
                "Age": 28,
                "City": "Porto",
                "Occupation": "Designer",
                "Skills": "UI/UX, Photoshop, Illustrator"
            },
            {
                "Name": "Pedro Santos",
                "Age": 35,
                "City": "Braga",
                "Occupation": "Project Manager",
                "Skills": "Agile, Scrum, Leadership"
            }
        ]

    def test_txt_file_exists(self):
        self.assertTrue(Path(self.txt_path).exists(), "TXT file should exist")

    def test_txt_conversion(self):
        result = convert_txt(
            file_path=self.txt_path,
            output_path=self.output_dir,
            delimiter="~"
        )
        self.assertIn("Conversion completed", result["message"])
        output_files = list(Path(self.output_dir).glob('*.json'))
        self.assertEqual(len(output_files), 3, "There should be 3 JSON files created")
        loaded_data = []
        for f in sorted(output_files):
            with open(f, 'r', encoding='utf-8') as file:
                loaded_data.append(json.load(file))
        loaded_data_sorted = sorted(loaded_data, key=lambda x: x['Name'])
        expected_sorted = sorted(self.expected_data, key=lambda x: x['Name'])
        for loaded, expected in zip(loaded_data_sorted, expected_sorted):
            for key in expected:
                if isinstance(expected[key], str):
                    self.assertEqual(loaded[key].strip(), expected[key].strip())
                else:
                    self.assertEqual(loaded[key], expected[key])

    def test_txt_conversion_with_fields(self):
        result = convert_txt(
            file_path=self.txt_path,
            output_path=self.output_dir,
            fields=["Name", "Age"],
            delimiter="~"
        )
        self.assertIn("Conversion completed", result["message"])
        output_files = list(Path(self.output_dir).glob('*.json'))
        self.assertEqual(len(output_files), 3, "There should be 3 JSON files created")
        for f in output_files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.assertEqual(set(data.keys()), {"Name", "Age"})

    def test_txt_conversion_with_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            convert_txt(
                file_path="nonexistent.txt",
                output_path=self.output_dir
            )

if __name__ == '__main__':
    unittest.main()
