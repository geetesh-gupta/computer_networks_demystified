"""
    This file deals with all the functions related to file IO 
"""

import os

cwd = os.getcwd()
path_to_folder = cwd + "/data/"


def get_all_filepaths(filepath):
    create_folder(path_to_folder+filepath)
    return os.scandir(path_to_folder+filepath)


def get_filepath(filename, filepath):
    return path_to_folder+filepath+"/"+filename


def convert_to_bytes(filepath=None):
    if not filepath:
        return None
    read_data = None
    # filepath = path_to_folder + filepath
    with open(filepath, 'r') as file:
        read_data = file.read()
    return read_data


def create_file(filename, filepath, data):
    data = data.decode("utf-8")
    print("Writing to file")
    new_file_path = create_folder(
        path_to_folder+str(filepath))+'/'+filename
    with open(new_file_path, 'w') as file:
        file.write(data)
    return True


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def main():
    data = convert_to_bytes()
    create_file(data, 1)


if __name__ == "__main__":
    main()
