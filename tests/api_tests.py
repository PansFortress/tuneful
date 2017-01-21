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
        session.add(file)
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
        }]
        self.assertEqual(data, data_assertion)

