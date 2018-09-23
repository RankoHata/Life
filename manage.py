import sqlite3
from flask import Flask

from config import *


def create_app():
    app = Flask(__name__)
    # app = Flask(__name__, static_folder='', static_url_path='')  # static_url_path 默认前缀是 /static
    # static_url_path='', 并不会将资源目录转为根目录，只是修改了映射，实际文件还是在static文件夹里

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['PASSWORD'] = PASSWORD
    app.config['BASE_DIR'] = basedir
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 后期分类型细化
    app.config['DATABASE'] = sqlite3_db
    app.config['ABSOLUTE_UPLOAD_FOLDER'] = os.path.join(basedir, UPLOAD_FOLDER)
    app.config['ABSOLUTE_DATABASE'] = os.path.join(basedir, sqlite3_db)
    app.config['SQL_SCRIPT'] = SQL_SCRIPT
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

    app.config['SIGN_CODE'] = {
        'BROWSE': BROWSE_SIGN_CODE,
        'DOWNLOAD': DOWNLOAD_SIGN_CODE,
    }

    if not os.path.exists(app.config['ABSOLUTE_DATABASE']):
        db = sqlite3.connect(app.config['ABSOLUTE_DATABASE'])
        with open(app.config['SQL_SCRIPT'], 'rb') as f:
            db.executescript(f.read().decode('utf-8'))
        db.close()

    from app import db
    db.init_db(app)  # register close_db

    from app import main
    app.register_blueprint(main.main)

    from app import auth
    app.register_blueprint(auth.auth)

    from app import api_v1_0
    app.register_blueprint(api_v1_0.api)

    return app


application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=12999)
    # application.run(port=12999)

