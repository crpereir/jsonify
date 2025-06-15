import json
import pandas as pd
import os

def convert_file_to_json(input_file, repeated_path, repeated_item, output_directory, fields=None, delimiter=",", skiprows=0):
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_directory, exist_ok=True)

        # Load previously processed IDs to avoid duplicates
        dumped_ids = set()
        if repeated_path and os.path.exists(repeated_path):
            with open(repeated_path, "r", encoding="utf-8") as f:
                dumped_ids = set(line.strip() for line in f if line.strip())

        # Read CSV file using pandas for efficient data handling
        df = pd.read_csv(input_file, delimiter=delimiter, skiprows=skiprows)
        
        # Filter columns if specific fields are requested
        if fields:
            df = df[fields]
        
        # Clean data by removing empty rows and columns
        df.dropna(axis=1, how="all", inplace=True)  # Remove columns that are all empty
        df.dropna(how="all", inplace=True)  # Remove rows that are all empty
        # Convert NaN values to None for proper JSON serialization
        df = df.where(pd.notna(df), None)
        
        # Convert DataFrame to list of dictionaries for easier processing
        data = df.to_dict(orient="records")
        
        # Process each record and create individual JSON files
        file_count = 0
        new_ids = []
        for record in data:
            # Skip records that have already been processed
            if repeated_path and repeated_item:
                unique_attr = record.get(repeated_item)
                if unique_attr is None or str(unique_attr) in new_ids or str(unique_attr) in dumped_ids:
                    continue

            # Create JSON file for current record
            output_file = os.path.join(output_directory, f"record_{file_count+1}.json")
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(record, json_file, indent=4, ensure_ascii=False)
            file_count += 1

            # Track processed IDs for duplicate prevention
            if repeated_path:
                new_ids.append(str(unique_attr))

        # Update the file containing processed IDs
        if new_ids and repeated_path:
            with open(repeated_path, "a", encoding="utf-8") as f:
                for new_id in new_ids:
                    f.write(f"{new_id}\n")
        
        return f"Conversion completed: {file_count} files created in {output_directory}"
    except Exception as e:
        raise Exception(f"Error converting {input_file}: {str(e)}")