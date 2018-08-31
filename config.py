import os
import logging

logging.basicConfig(level=logging.DEBUG)
basedir = os.path.abspath(os.path.dirname(__file__))
sqlite3_db = 'DMYX.sqlite3'
UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'mp3', 'mp4'}
SECRET_KEY = os.urandom(24)
PASSWORD = 'baccano'
SQL_SCRIPT = 'schema.sql'
