from click import FileError
from flask import jsonify, send_file
from werkzeug.datastructures import FileStorage
from app.kenzie import FILES_DIRECTORY
import os


def file_already_exist(filename: str, extension: str):

    extension_path = os.path.join(FILES_DIRECTORY, extension)

    return filename in os.listdir(extension_path)


def extension_already_exist(extension: str):

    return extension in os.listdir(FILES_DIRECTORY)


def listing_all_files():

    list_extension = os.listdir(FILES_DIRECTORY)
    new_list = {}

    for ext in list_extension:
        path = os.path.join(FILES_DIRECTORY, ext)
        new_list[ext] = os.listdir(path)

    return new_list


def listing_files(extension: str):

    if not extension_already_exist(extension): 
        raise FileNotFoundError

    list_path = os.path.join(FILES_DIRECTORY, extension)

    return jsonify(os.listdir(list_path))    


def upload_image(file: FileStorage) -> None:
   
    filename: str = file.filename

    _, extension = os.path.splitext(filename)
    extension = extension.replace(".", "")

    if file_already_exist(filename, extension):
        raise FileExistsError

    saving_path = os.path.join(FILES_DIRECTORY, extension, filename) 
    
    file.save(saving_path)


def download_image(filename: str):

    _, extension = os.path.splitext(filename)
    extension = extension.replace(".", "")

    if not file_already_exist(filename, extension):
        raise FileError(filename)

    if not extension_already_exist(extension):
        raise FileNotFoundError    

    download_path = os.path.join(f".{FILES_DIRECTORY}", extension, filename)

    return send_file(download_path, as_attachment=True)


def download_zip(file_type: str, compression_ratio: str):
    
    output_file = f"{file_type}.zip"
    input_path = os.path.join(FILES_DIRECTORY, file_type)
    output_path_file = os.path.join("/tmp", output_file)

    if os.path.isfile(output_path_file):
        os.remove(output_path_file)

    if not extension_already_exist(file_type):
        raise FileNotFoundError   

    command = f"zip -r -j -{compression_ratio} {output_path_file} {input_path}"

    os.system(command)

    return send_file(output_path_file, as_attachment=True)