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

    def test_songs_post(self):
        file = models.File(filename="New_File.mp4")
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

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        data_back = json.loads(response.data.decode("ascii"))
        self.assertEqual(data_back, songs[0].as_dictionary())

    def test_songs_delete(self):
        self.create_entries()
        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 2)

        response = self.client.delete("/api/songs/1",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["message"], "1 has been deleted successfully")

        song = session.query(models.Song).get(1)
        self.assertEqual(song, None)

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

    def test_songs_put_no_entry(self):
        file_id = 1

        song_update = {
            "file":{
                "id": file_id
            }
        }

        response = self.client.put("/api/songs/{}".format(file_id),
                                   data=json.dumps(song_update),
                                   content_type="application/json",
                                   headers=[("Accept", "application/json")])

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["message"], "1 does not exist and cannot be updated")

    def test_songs_put(self):
        self.create_entries()
        song = session.query(models.Song).first()
        self.assertEqual(song.id, 1)
        self.assertEqual(song.file_id, 1)

        file = session.query(models.File).get(9)
        self.assertEqual(None, file)

        new_file_id = 9

        file = models.File(id=new_file_id, filename="test_file.mp4")
        session.add(file)
        session.commit()

        song_update = {
            "file":{
                "id": new_file_id
            }
        }

        response = self.client.put("/api/songs/{}".format(song.id),
                                   data=json.dumps(song_update),
                                   content_type="application/json",
                                   headers=[("Accept", "application/json")])
        data = response.data.decode("ascii")
        data = json.loads(data)
        self.assertEqual(response.status_code, 200)

    # def test_get_uploaded_file(self):
    #     path = upload.path("test.txt")
    #     with open(path, "wb") as f:
    #         f.write(b"File contents")

    #     response = self.client.get("/uploads/test.txt")

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.mimetype, "text/plain")
    #     self.assertEqual(response.data, b"File contents")
