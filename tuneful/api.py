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

@app.route("/api/songs", methods=["POST"])
def songs_post():
    data = request.json

    song = models.Song(id=data["id"], file=data["file"])
    sesion.add(song)
    session.commit()

    data = json.dumps(song.as_dictionary())
    
    return Response(data, 201, mimetype="application/json")