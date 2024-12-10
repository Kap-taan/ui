# import json

# # Define the file name containing the text
# filename = "data/analysiSummaryBepensa.txt"

# # Initialize a dictionary to store the objects
# outlet_data = {}

# # Open and read the file
# with open(filename, "r") as file:
#     # Skip the first header line
#     header = file.readline()

#     # Iterate over the rest of the lines
#     for line in file:
#         # Split the line by whitespace to extract columns
#         parts = line.split()

#         # Make sure the line has the correct number of columns
#         if len(parts) == 3:
#             outlet_code, login_id, total_new_sku_count = parts

#             # Create a key-value pair with the desired format
#             key = f"{login_id}::{outlet_code}"
#             outlet_data[key] = int(total_new_sku_count)

# # Write the dictionary to a JSON file
# json_filename = "data/analysisSummaryBepensa.json"
# with open(json_filename, "w") as json_file:
#     json.dump(outlet_data, json_file, indent=4)

# print(f"Data successfully saved to {json_filename}")


# import pandas as pd

# # File paths
# csv_file_path = "data/analysisSummaryBepensa.csv"
# json_file_path = "data/analysisSummaryBepensa.json"

# # Load the CSV file into a DataFrame
# df = pd.read_csv(csv_file_path)

# # Strip whitespace from column names and all string values in the DataFrame
# df.columns = df.columns.str.strip()  # Strip column names
# df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Strip string values

# # Convert the DataFrame to a JSON file
# df.to_json(json_file_path, orient="records", indent=4)

# print(f"Trimmed JSON file created at: {json_file_path}")




import pandas as pd
from s3 import read_file_from_s3

def read_and_trim_csv(file_key):
    """
    Reads a CSV file from S3, removes double quotes, trims each cell to remove leading/trailing spaces, 
    and returns a pandas DataFrame.
    
    Args:
    - file_key (str): The key of the CSV file in the S3 bucket.
    
    Returns:
    - pd.DataFrame: DataFrame with cleaned and trimmed values.
    """
    # Fetch the file content from S3
    file_content = read_file_from_s3(file_key)

    # Split the content into lines
    lines = file_content.splitlines()

    # Remove double quotes and trim each cell
    cleaned_data = [line.replace('"', '').strip().split(',') for line in lines]

    # Check if all rows have the same number of columns as the header
    num_columns = len(cleaned_data[0])
    
    # Remove rows that have more or fewer columns than expected
    cleaned_data = [row for row in cleaned_data if len(row) == num_columns]

    # Convert to DataFrame
    df = pd.DataFrame(cleaned_data[1:], columns=cleaned_data[0])  # First line as header

    # Final trim for column names and cell values
    df = df.rename(columns=lambda x: x.strip()).applymap(lambda x: x.strip() if isinstance(x, str) else x)

    print(df.columns)
    return df


# Example usage
# file_path = 'path/to/your/file.csv'
# df = read_and_trim_csv(file_path)

# # Show DataFrame
# print(df)


