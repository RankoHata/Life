import os
import logging

logging.basicConfig(level=logging.DEBUG)
basedir = os.path.abspath(os.path.dirname(__file__))
sqlite3_db = os.path.join(basedir, 'DMYX.sqlite3')
UPLOAD_FOLDER = os.path.join(basedir, 'upload')
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'mp3'}
SECRET_KEY = os.urandom(24)
PASSWORD = 'baccano'
SQL_SCRIPT = 'schema.sql'
