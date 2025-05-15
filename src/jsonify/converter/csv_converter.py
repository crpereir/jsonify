import json
import pandas as pd
import os

def convert_file_to_json(input_file, output_directory, delimiter=",", skiprows=0):
    try:
        os.makedirs(output_directory, exist_ok=True)
        
        df = pd.read_csv(input_file, delimiter=delimiter, skiprows=skiprows)
        
        if 'Ingredient' in df.columns:
            df.rename(columns={'Ingredient': 'Proper Name'}, inplace=True)
        
        df.dropna(axis=1, how="all", inplace=True)
        df.dropna(how="all", inplace=True)
        df = df.where(pd.notna(df), None)
        
        data = df.to_dict(orient="records")
        
        file_count = 0
        for i, record in enumerate(data):
            output_file = os.path.join(output_directory, f"record_{i+1}.json")
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(record, json_file, indent=4, ensure_ascii=False)
            file_count += 1
        
        return f"Conversion completed: {file_count} files created in {output_directory}"
    except Exception as e:
        raise Exception(f"Error converting {input_file}: {str(e)}")