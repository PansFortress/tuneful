import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())

    def create_entries(self):
        file = models.File(filename="test_file.mp4")
        song = models.Song(file=file)

        file_2 = models.File(filename="another_song.mp3")
        song_2 = models.Song(file=file_2)
        
        session.add_all([file, file_2])
        session.commit()

    def test_songs_get(self):
        self.create_entries()
        response = self.client.get("/api/songs", 
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode("ascii"))
        data_assertion = [{
                "id": 1,
                "file": {
                    "id": 1,
                    "name": "test_file.mp4"
                        }
            },
            {
                "id": 2,
                "file":{
                    "id": 2,
                    "name": "another_song.mp3"
                }
            }]
        self.assertEqual(data, data_assertion)

    def test_song_get(self):
        self.create_entries()
        song = session.query(models.Song).get(1)
        data_assertion = {
            "id": 1,
            "file": {
                "id": 1,
                "name": "test_file.mp4"
                    
                }
            }
        self.assertEqual(song.as_dictionary(), data_assertion)

        response = self.client.get("api/songs/1",
            headers=[("Accept", "application/json")])
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data, data_assertion)

# Is my post tests failing because the following are ints?
# Not clear on what's throwing the current errors in tests
    def test_songs_post(self):
        file = File(filename="New_File.mp4")
        session.add(file)
        session.commit()

        song = {
            "file": {
                "id": file.id
            }
        }

        response = self.client.post("/api/songs",
            data=json.dumps(song),
            content_type="application/json",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 201)
        data_back = json.loads(response.data.decode("ascii"))
        self.assertEqual(data_back, song)

        songs = session.query(models.Song).order_by(models.Song.id)
        self.assertEqual(len(songs), 1)

    def test_songs_delete(self):
        self.create_entries()
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 2)

        # Delete an entry
        response = self.client.delete("/api/songs/1",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["message"], "1 has been deleted successfully")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs),1)

        # files = session.query(models.File).all()
        # self.assertEqual(len(files),1)
