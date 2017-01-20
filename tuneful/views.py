from flask import render_template

from tuneful import app

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api/songs", methods=["GET"])
def songs_get():
    """Return all songs"""
    songs = sessions.query(models.Songs).all().order_by(models.Songs.id)
    data = json.dumps([song.as_dictionary() for song in songs])
    
    return Response(data, 200, mimetype="application/json")