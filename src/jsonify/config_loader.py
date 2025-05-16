import os
from typing import List, Dict

class ConfigLoader:
    def __init__(self):
        self.base_input_folder = ""
        self.base_output_folder = ""
        self.file_types = ["xml"]
        self.conversion_method = "python"
        self._log_paths = {
            'log_file': "missing_fields_log.txt",
            'unconverted_file': "unconverted_files.txt",
            'processed_names_file': "names.txt",
            'processing_summary_file': "summary.txt"
        }

    def override_log_paths(self, base_log_dir: str):
        os.makedirs(base_log_dir, exist_ok=True)
        self._log_paths = {
            key: os.path.join(base_log_dir, filename)
            for key, filename in {
                'log_file': "missing_fields_log.txt",
                'unconverted_file': "unconverted_files.txt",
                'processed_names_file': "names.txt",
                'processing_summary_file': "summary.txt"
            }.items()
        }

    def get_file_types(self) -> List[str]:
        return self.file_types

    def get_conversion_method(self) -> str:
        return self.conversion_method

    def get_base_input_folder(self) -> str:
        return os.path.abspath(self.base_input_folder)

    def get_base_output_folder(self) -> str:
        return os.path.abspath(self.base_output_folder)

    def get_log_file_path(self) -> str:
        return os.path.abspath(self._log_paths['log_file'])

    def get_unconverted_file_path(self) -> str:
        return os.path.abspath(self._log_paths['unconverted_file'])

    def get_processed_names_file_path(self) -> str:
        return os.path.abspath(self._log_paths['processed_names_file'])

    def get_summary_file_path(self) -> str:
        return os.path.abspath(self._log_paths['processing_summary_file'])

    def get_input_folder_for_type(self, file_type: str) -> str:
        return os.path.join(self.get_base_input_folder(), f"{file_type}_files")

    def get_output_folder_for_type(self, file_type: str) -> str:
        return os.path.join(self.get_base_output_folder(), f"{file_type}_results")

    def get_all_folders(self) -> Dict[str, Dict[str, str]]:
        return {
            file_type: {
                'input': self.get_input_folder_for_type(file_type),
                'output': self.get_output_folder_for_type(file_type)
            }
            for file_type in self.get_file_types()
        }
