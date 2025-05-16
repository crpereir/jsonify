import os
import json
from pathlib import Path
from jsonify import run_conversion

def test_run_conversion_end_to_end():
    base_path = Path(__file__).parent

    input_dir = base_path / "input"
    output_dir = base_path / "output"
    log_dir = base_path / "logs"

    for folder in ["csv_results", "xml_results", "txt_results"]:
        output_subdir = output_dir / folder
        if output_subdir.exists():
            for f in output_subdir.glob("*.json"):
                f.unlink()

    summary = run_conversion(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        file_types=["csv", "xml", "txt"],
        conversion_method="python",
        log_dir=str(log_dir)
    )

    assert summary["Total converted files"] >= 3

    csv_output = output_dir / "csv_results"
    assert any(f.suffix == ".json" for f in csv_output.glob("*")), "No CSV JSON output found"

    xml_output = output_dir / "xml_results" / "test.json"
    assert xml_output.exists(), "XML output file not created"
    with open(xml_output, encoding="utf-8") as f:
        data = json.load(f)
        assert data.get("name") == "TestDrugName"

    txt_output = output_dir / "txt_results"
    txt_files = list(txt_output.glob("*.json"))
    assert len(txt_files) == 2, "Expected 2 TXT JSON files"

    for log_file in [
        "missing_fields_log.txt",
        "unconverted_files.txt",
        "summary.txt",
        "names.txt"
    ]:
        log_path = log_dir / log_file
        assert log_path.exists(), f"Missing log file: {log_file}"
