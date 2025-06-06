import json
import pandas as pd
import os

def convert_file_to_json(input_file, repeated_path, repeated_item, output_directory, fields=None, delimiter=",", skiprows=0):
    try:
        os.makedirs(output_directory, exist_ok=True)

        dumped_ids = set()
        if repeated_path and os.path.exists(repeated_path):
            with open(repeated_path, "r", encoding="utf-8") as f:
                dumped_ids = set(line.strip() for line in f if line.strip())

        df = pd.read_csv(input_file, delimiter=delimiter, skiprows=skiprows)
        
        if fields:
            df = df[fields]
        
        df.dropna(axis=1, how="all", inplace=True)
        df.dropna(how="all", inplace=True)
        df = df.where(pd.notna(df), None)
        
        data = df.to_dict(orient="records")
        
        file_count = 0
        new_ids = []
        for record in data:
            if repeated_path and repeated_item:
                unique_attr = record.get(repeated_item)
                if unique_attr is None or str(unique_attr) in new_ids or str(unique_attr) in dumped_ids:
                    continue

            output_file = os.path.join(output_directory, f"record_{file_count+1}.json")
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(record, json_file, indent=4, ensure_ascii=False)
            file_count += 1

            if repeated_path:
                new_ids.append(str(unique_attr))

        if new_ids and repeated_path:
            with open(repeated_path, "a", encoding="utf-8") as f:
                for new_id in new_ids:
                    f.write(f"{new_id}\n")
        
        return f"Conversion completed: {file_count} files created in {output_directory}"
    except Exception as e:
        raise Exception(f"Error converting {input_file}: {str(e)}")