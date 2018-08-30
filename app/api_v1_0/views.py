import os
import time
from flask import request, current_app, url_for, redirect, session, jsonify, g

from . import api
from app.main.views import enter_required
from app.auth.views import login_required
from app.db import get_db


@api.route('/verify', methods=['POST'])
def api_verify_password():
    password = request.form['password']
    if password == current_app.config['PASSWORD']:
        session['certification'] = True
    return redirect(url_for('main.homepage'))


def allowed_file(filename):
    if '.' in filename and filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']:
        return True
    return False


@api.route('/upload', methods=['POST'])
@enter_required
@login_required
def api_upload_file():
    uploaded_file = request.files['upload']  # 从表单的file字段获取文件，upload为表单的name值
    file_name = uploaded_file.filename

    file_dir = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    if uploaded_file and allowed_file(file_name):
        # ext_name = file_name.rsplit('.', 1)[1]
        unix_time = int(time.time())
        user_name = g.user['account']
        user_id = g.user['id']
        new_file_name = user_name + '_' + str(unix_time) + '_' + file_name  # 新的文件名，加上时间

        uploaded_file.save(os.path.join(file_dir, new_file_name))

        db = get_db()
        db.execute(
            'INSERT INTO file (author_id, upload_time, file_name) VALUES (?, ?, ?)',
            (user_id, unix_time, file_name)
        )
        db.commit()
        return jsonify({'errno': 0, 'errmsg': 'Successful upload'})
    return jsonify({'errno': 100, 'errmsg': 'Upload failed'})
