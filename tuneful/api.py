import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

@decorators.accept("application/json")
@app.route("/api/songs", methods=["GET"])
def songs_get():
    """Return all songs"""
    songs = session.query(models.Song).order_by(models.Song.id)
    data = json.dumps([song.as_dictionary() for song in songs])
    
    return Response(data, 200, mimetype="application/json")

@decorators.accept("application/json")
@app.route("/api/songs/<int:id>", methods=["GET"])
def song_get(id):
    song = session.query(models.Song).get(id)

    if not song:
        message = "{} does not existed and cannot be retrieved".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")
    
    data = json.dumps(song.as_dictionary())

    return Response(data, 200, mimetype="application/json")

# TODO: Is to validate JSON data against Schema up-top
@app.route("/api/songs", methods=["POST"])
def songs_post():
    data = request.json

    song = models.Song(file_id=data["file"]["id"])
    session.add(song)
    session.commit()

    data = json.dumps(song.as_dictionary())
    
    return Response(data, 201, mimetype="application/json")

# TODO: Setup a decorator to handle the code that's being done in 64-69
@decorators.existence()
@app.route("/api/songs/<int:id>", methods=["DELETE"])
def song_delete(id, item):
    # song = session.query(models.Song).get(id)
    
    # if not song:
    #     message = "{} does not exist and cannot be deleted".format(id)
    #     data = json.dumps({"message": message})
    #     return Response(data, 404, mimetype="application/json")

    session.delete(song)
    session.commit()

    message = "{} has been deleted successfully".format(id)
    data = json.dumps({"message": message})

    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs/<int:id>", methods=["PUT"])
def song_put(id):
    song = session.query(models.Song).get(id)
    data = request.json

    if not song:
        message = "{} does not exist".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    song.file_id = data["file"]["id"]
    session.commit()
    message = "{} has been updated".format(id)

    data = json.dumps({"message": message})

    return Response(data, 200, mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)

@app.route("/api/files", methods=["POST"])
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")


