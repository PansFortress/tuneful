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

song_schema = {
    "definitions":{
        "file":{
            "type": "object",
            "properties": {
                "file_id": {"type": "int"}
            }
        }
    }
}

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

@app.route("/api/songs", methods=["POST"])
def songs_post():
    data = request.json

    song = models.Song(file_id=data["file"]["file_id"])
    session.add(song)
    session.commit()

    data = json.dumps(song.as_dictionary())
    
    return Response(data, 201, mimetype="application/json")

@app.route("/api/songs/<int:id>", methods=["DELETE"])
def song_delete(id):
    song = session.query(models.Song).get(id)
    
    if not song:
        message = "{} does not exist and cannot be deleted".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    session.delete(song)
    session.commit()

    message = "{} has been deleted successfully".format(id)
    data = json.dumps({"message": message})

    return Response(data, 200, mimetype="application/json")

# TODO: Need to validate data schema
@app.route("/api/songs/<int:id>", methods=["PUT"])
def song_put(id):
    song = session.query(models.Song).get(id)
    data = request.json

    if not song:
        message = "{} does not exist and cannot be updated".format(id)
        data = json.dumps({"message": message})
        return Response(data, 404, mimetype="application/json")

    song.file_id = data["file"]["file_id"]
    session.commit()
    messsage = "{} has been updated".format(id)

    return Response(data, 200, mimetype="application/json")