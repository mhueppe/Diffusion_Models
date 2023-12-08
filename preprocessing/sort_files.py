import os
import shutil
import json

if __name__ == '__main__':

    name_folder_dict = json.load(open(r"pokemon_to_body.json"))

    # Specify the source directory
    source_directory = r"data\raw"

    # Iterate through the files in the source directory
    for filename in os.listdir(source_directory):
        file_path = os.path.join(source_directory, filename)

        # Check which name is in the file path
        matching_name = next((name for name in name_folder_dict.keys() if name in filename), None)

        if matching_name:
            # Get the corresponding folder name from the dictionary
            folder_name = name_folder_dict[matching_name]

            # Create the folder if it doesn't exist
            if not folder_name:
                folder_name = "Body20"
            folder_path = os.path.join(source_directory, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # Move the file to the folder
            destination_path = os.path.join(folder_path, filename)
            shutil.move(file_path, destination_path)
            print(f"Moved {filename} to {folder_name} folder.")
        else:
            print(f"No matching name found for {filename}. Skipping.")

    print("File movement completed.")
