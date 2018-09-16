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


# def allowed_file(filename):
#     if '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
#         return True
#     return False
#
#
# def enter_required(view_func):
#     @wraps(view_func)
#     def wrapped_func(*args, **kwargs):
#         if g.certification is not True:
#             return redirect(url_for('homepage'))
#         return view_func(*args, **kwargs)
#     return wrapped_func
#
#
# @app.before_request
# def check():
#     verify_sign = session.get('certification')
#     if verify_sign is True:
#         g.certification = True
#     else:
#         g.certification = False
#
#
# @app.route('/')
# def homepage():
#     x = get_db()
#     if g.certification is True:
#         return render_template('base.html')
#     else:
#         return render_template('start.html')
#
#
# @app.route('/exit')
# def exit_enter():
#     session.clear()
#     return redirect(url_for('homepage'))
#
#
# @app.route('/file/upload')
# @enter_required
# def upload_file():
#     return render_template('file/upload.html')
#
#
# @app.route('/api/verify', methods=['POST'])
# def api_verify_password():
#     password = request.form['password']
#     if password == current_app.config['PASSWORD']:
#         session['certification'] = True
#     return redirect(url_for('homepage'))
#
#
# @app.route('/api/upload', methods=['POST'])
# @enter_required
# def api_upload_file():
#     file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
#     if not os.path.exists(file_dir):
#         os.makedirs(file_dir)
#     uploaded_file = request.files['upload']  # 从表单的file字段获取文件，upload为表单的name值
#     file_name = uploaded_file.filename
#     if uploaded_file and allowed_file(file_name):
#         # ext_name = file_name.rsplit('.', 1)[1]
#         unix_time = int(time.time())
#         new_file_name = str(unix_time) + '_' + file_name  # 新的文件名，加上时间
#         uploaded_file.save(os.path.join(file_dir, new_file_name))
#         return jsonify({'errno': 0, 'errmsg': 'Successful upload'})
#     return jsonify({'errno': 100, 'errmsg': 'Upload failed'})


application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=12999)
    # create_app().run(port=12999)

