import os
import pandas as pd

# AI help taken from perplexity.ai
def get_files_in_directory(path, parent_path=[]):
    """Recursively retrieve files and their full paths in the directory"""
    all_files = []

    for entry in os.scandir(path):
        if entry.is_dir():
            all_files.extend(get_files_in_directory(entry.path, parent_path + [entry.name]))
        elif entry.is_file():
            all_files.append(parent_path + [entry.name])

    return all_files


def generate_excel(path, output_file='folder_structure.xlsx'):
    files_data = get_files_in_directory(path)

    df = pd.DataFrame(files_data)

    df.to_excel(output_file, index=False, header=False)


base_path = '/Users/meet/Downloads/Clothes'
generate_excel(base_path)
