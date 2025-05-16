from .config_loader import ConfigLoader
from .main import process_file_types

def run_conversion(
    input_dir: str,
    output_dir: str,
    file_types: list,
    conversion_method: str = "python",
    log_dir: str = None
):
    config_loader = ConfigLoader()

    config_loader.base_input_folder = input_dir
    config_loader.base_output_folder = output_dir
    config_loader.file_types = file_types
    config_loader.conversion_method = conversion_method

    if log_dir:
        config_loader.override_log_paths(log_dir)

    return process_file_types(config_loader)
