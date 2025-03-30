import os
import pandas as pd


def get_files_in_directory(path, parent_path=[]):
    """Recursively retrieve files and their full paths in the directory"""
    all_files = []

    # Loop through each item in the directory
    for entry in os.scandir(path):
        if entry.is_dir():
            # Recursively scan subdirectories
            all_files.extend(get_files_in_directory(entry.path, parent_path + [entry.name]))
        elif entry.is_file():
            # For files, combine the path with the current folder structure
            all_files.append(parent_path + [entry.name])

    return all_files


def generate_excel(path, output_file='folder_structure.xlsx'):
    """Generate Excel file with files and their folder structure"""
    # Get all files and their folder paths
    files_data = get_files_in_directory(path)

    # Convert to pandas DataFrame
    df = pd.DataFrame(files_data)

    # Write to Excel
    df.to_excel(output_file, index=False, header=False)


# Provide the base path where you want to extract folder structure
base_path = '/Users/meet/Downloads/Clothes'  # Update this path to the desired folder
generate_excel(base_path)
