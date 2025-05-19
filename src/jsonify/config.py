import os
from pathlib import Path
from typing import Dict, List

class DirectoryManager:
    """
    Gerencia a estrutura de diretórios do projeto.
    Define e mantém a organização padrão dos diretórios de entrada e saída.
    """
    
    # Tipos de arquivos suportados e seus diretórios correspondentes
    SUPPORTED_TYPES = {
        'csv': 'csv_files',
        'xml': 'xml_files',
        'txt': 'text_files'
    }
    
    def __init__(self, base_dir: str):
        """
        Inicializa o gerenciador de diretórios.
        
        Args:
            base_dir: Diretório base onde input e output serão criados
        """
        self.base_dir = Path(base_dir)
        self.input_dir = self.base_dir / 'input'
        self.output_dir = self.base_dir / 'output'
        
        # Criar estrutura de diretórios
        self._create_directory_structure()
    
    def _create_directory_structure(self):
        """Cria a estrutura de diretórios padrão."""
        # Criar diretórios de input para cada tipo
        for dir_name in self.SUPPORTED_TYPES.values():
            os.makedirs(self.input_dir / dir_name, exist_ok=True)
        
        # Criar diretórios de output para cada tipo
        for dir_name in self.SUPPORTED_TYPES.values():
            os.makedirs(self.output_dir / dir_name, exist_ok=True)
    
    def get_input_dir(self, file_type: str) -> Path:
        """
        Obtém o diretório de input para um tipo específico de arquivo.
        
        Args:
            file_type: Tipo do arquivo (csv, xml, txt)
            
        Returns:
            Path do diretório de input
        """
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")
        return self.input_dir / self.SUPPORTED_TYPES[file_type]
    
    def get_output_dir(self, file_type: str) -> Path:
        """
        Obtém o diretório de output para um tipo específico de arquivo.
        
        Args:
            file_type: Tipo do arquivo (csv, xml, txt)
            
        Returns:
            Path do diretório de output
        """
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")
        return self.output_dir / self.SUPPORTED_TYPES[file_type]
    
    def validate_input_file(self, file_path: str) -> bool:
        """
        Verifica se um arquivo está no diretório correto baseado em sua extensão.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            True se o arquivo está no diretório correto
        """
        file_path = Path(file_path)
        file_type = file_path.suffix.lower().lstrip('.')
        
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")
            
        expected_dir = self.get_input_dir(file_type)
        return expected_dir in file_path.parents
    
    def get_default_output_path(self, input_file: str) -> Path:
        """
        Gera o caminho de output padrão para um arquivo de input.
        
        Args:
            input_file: Caminho do arquivo de input
            
        Returns:
            Caminho padrão para o arquivo de output
        """
        input_path = Path(input_file)
        file_type = input_path.suffix.lower().lstrip('.')
        
        if file_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"Tipo de arquivo não suportado: {file_type}")
            
        output_dir = self.get_output_dir(file_type)
        return output_dir / f"{input_path.stem}.json"

# Instância global do gerenciador de diretórios
directory_manager = None

def init_directory_manager(base_dir: str):
    """
    Inicializa o gerenciador de diretórios global.
    
    Args:
        base_dir: Diretório base onde input e output serão criados
    """
    global directory_manager
    directory_manager = DirectoryManager(base_dir)
    return directory_manager

def get_directory_manager() -> DirectoryManager:
    """
    Obtém a instância global do gerenciador de diretórios.
    
    Returns:
        Instância do DirectoryManager
    """
    if directory_manager is None:
        raise RuntimeError("DirectoryManager não foi inicializado. Chame init_directory_manager primeiro.")
    return directory_manager 