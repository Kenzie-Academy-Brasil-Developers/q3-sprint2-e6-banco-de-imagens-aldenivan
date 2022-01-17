from click import FileError
from flask import Flask, jsonify, request
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from app.kenzie import image
from os import getenv


MAX_CONTENT_LENGTH = int(getenv("MAX_CONTENT_LENGTH"))


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH * 1024 * 1024


@app.get("/files")
def all_files():

    return jsonify(image.listing_all_files()), 200


@app.get("/files/<extension>")
def list_files(extension: str):
    
    try:
        return image.listing_files(extension), 200

    except FileNotFoundError:
        return {"msg": "Formato de extensão inválido!"}, 404


@app.post("/upload")
def upload():
    
    files: ImmutableMultiDict[str, FileStorage] = request.files

    for file in files.values():
        
        try:
            image.upload_image(file)

        except FileExistsError:
            return {"msg": "Arquivo já existe!"}, 409

        except FileNotFoundError:
            return {"msg": "Extensão não suportada!"}, 415

    return {"msg": "Arquivo criado com sucesso!"}, 201


@app.get("/download/<filename>")
def download_file(filename: str):
    
    try:
        return image.download_image(filename)

    except FileError:
        return {"msg": "Arquivo não encontrado!"}, 404

    except FileNotFoundError:
        return {"msg": "Formato de arquivo inválido!"}, 404


@app.get("/download-zip")
def download_dir_as_zip():

    file_type = request.args.get("file_extension")
    compression_ratio = request.args.get("compression_ratio", 6)

    if not file_type:
        return {"msg": "Query param `file_type` é obrigatório"}, 400     

    try:
        return image.download_zip(file_type, compression_ratio), 200

    except FileNotFoundError:
        return {"msg": "Extensão inválida ou pasta a está vazia!"}, 404


@app.errorhandler(413)
def new_error(error):
    
    return {"msg": f"Arquivo ultrapassa o limite permitido de {MAX_CONTENT_LENGTH}MB!"}, 413
