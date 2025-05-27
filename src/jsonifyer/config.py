import os
from pathlib import Path
from typing import Dict, List

class DirectoryManager:
    SUPPORTED_TYPES = {
        'csv': 'csv_files',
        'xml': 'xml_files',
        'txt': 'text_files'
    }
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / 'input'
        self.output_dir = self.base_dir / 'output'
    
    
    def get_input_dir(self, file_type: str) -> Path:
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Type file not supported: {file_type}")
        return self.input_dir / self.SUPPORTED_TYPES[file_type]
    
    def get_output_dir(self, file_type: str) -> Path:
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Type file not supported: {file_type}")
        return self.output_dir / self.SUPPORTED_TYPES[file_type]
    
    def validate_input_file(self, file_path: str) -> bool:
        file_path = Path(file_path)
        file_type = file_path.suffix.lower().lstrip('.')
        
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Type file not supported: {file_type}")
            
        expected_dir = self.get_input_dir(file_type)
        return expected_dir in file_path.parents
    
    def get_default_output_path(self, input_file: str) -> Path:
        input_path = Path(input_file)
        file_type = input_path.suffix.lower().lstrip('.')
        
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Type file not supported: {file_type}")
            
        output_dir = self.get_output_dir(file_type)
        return output_dir / f"{input_path.stem}.json"

directory_manager = None

def init_directory_manager(base_dir: str):
    global directory_manager
    directory_manager = DirectoryManager(base_dir)
    return directory_manager

def get_directory_manager() -> DirectoryManager:
    if directory_manager is None:
        raise RuntimeError("DirectoryManager not initialized. Call init_directory_manager() first.")
    return directory_manager 