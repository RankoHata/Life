import os
import logging

logging.basicConfig(level=logging.DEBUG)
basedir = os.path.abspath(os.path.dirname(__file__))
sqlite3_db = 'DMYX.sqlite3'
UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'mp3', 'mp4', 'pdf', '7z', 'rar'}
SECRET_KEY = os.urandom(24)
TIMEZONE = 'Asia/Shanghai'

try:
    PASSWORD = os.environ['Life_password']
except KeyError:
    raise EnvironmentError('Please set environ: Life_password')

SQL_SCRIPT = 'schema.sql'


# Records
BROWSE_SIGN_CODE = 0
DOWNLOAD_SIGN_CODE = 1


class EnvironError(Exception):
    pass
