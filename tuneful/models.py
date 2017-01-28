import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine, session

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'))

    def as_dictionary(self):
        song = {
            "id": self.id,
            "file": self.file.as_dictionary()
        }
        return song

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    filename = Column(String(150))
    song = relationship("Song", uselist=False, backref="file")

    def as_dictionary(self):
        file ={
            "id": self.id,
            "name": self.filename,
            "path": url_for("uploaded_file", filename=self.filename)
        }
        return file