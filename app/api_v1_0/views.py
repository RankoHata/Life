import os
import re
import time
from flask import request, current_app, url_for, redirect, session, jsonify, g, abort, flash

from . import api
from app import get_new_filename
from app.main.views import enter_required
from app.auth.views import login_required
from app.db import get_db, Sqlite3Query

# re_str = re.compile(r'(.+)_(\d+)_(.+)')


@api.route('/verify', methods=['POST'])
def api_verify_password():
    password = request.form['password']
    if password == current_app.config['PASSWORD']:
        session['certification'] = True
        return jsonify({'Accessible': True})
    else:
        return jsonify({'Accessible': False})


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

    file_dir = current_app.config['ABSOLUTE_UPLOAD_FOLDER']
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    if uploaded_file and allowed_file(file_name):
        # ext_name = file_name.rsplit('.', 1)[1]
        unix_time = int(time.time())
        user_name = g.user['account']
        user_id = g.user['id']
        new_file_name = str(user_id) + '_' + str(unix_time) + '_' + file_name  # 新的文件名，加上时间

        uploaded_file.save(os.path.join(file_dir, new_file_name))

        db = get_db()
        db.execute(
            'INSERT INTO file (author_id, upload_time, file_name) VALUES (?, ?, ?)',
            (user_id, unix_time, file_name)
        )
        db.commit()
        flash('Successful upload.')
        return redirect(url_for('main.homepage'))
        # return jsonify({'errno': 0, 'errmsg': 'Successful upload'})
    flash('Upload failed.')
    return redirect(url_for('main.homepage'))
    # return jsonify({'errno': 100, 'errmsg': 'Upload failed'})


# @api.route('/delete', methods=['GET'])
# @enter_required
# @login_required
# def api_delete_file():
#     account, upload_time, file_name = request.args['account'], request.args['upload_time'], request.args['file_name']
#     user_id, user_name = g.user['id'], g.user['account']
#     if user_name != account:
#         return jsonify({'errno': 101, 'errmsg': '验证信息不符'})
#         # 该用户想删除其他用户的文件
#     else:
#         new_file_name = account + '_' + upload_time + '_' + file_name
#         db = get_db()
#         db.execute(  # 不管文件存不存在都要删掉这条记录
#             'DELETE FROM file WHERE author_id = ? and upload_time = ? and file_name = ?',
#             (user_id, upload_time, file_name)
#         )
#         db.commit()
#         if db.total_changes == 1:
#             if os.path.exists(os.path.join(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], new_file_name)):
#                 try:
#                     os.remove(os.path.join(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], new_file_name))
#                 except OSError:
#                     flash('删除文件时出错')
#                     return redirect(url_for('main.homepage'))
#                     # return jsonify({'errno': 103, 'errmsg': '删除文件时出错'})
#                 else:
#                     flash('Successful delete')
#                     return redirect(url_for('main.homepage'))
#                     # return jsonify({'errno': 0, 'errmsg': 'Successful delete'})
#             else:
#                 flash('本地不存在文件')
#                 return redirect(url_for('main.homepage'))
#                 # return jsonify({'errno': 102, 'errmsg': '本地不存在文件'})
#         elif db.total_changes == 0:  # 数据库中没有数据
#             flash('文件信息错误')
#             return redirect(url_for('main.homepage'))
#             # return jsonify({'errno': 104, 'errmsg': '文件信息错误'})
#         else:  # db.total_changes 不为1或0
#             flash('未知错误')
#             return redirect(url_for('main.homepage'))
#             # return jsonify({'errno': 105, 'errmsg': '未知错误'})


@api.route('/delete', methods=['POST'])
@enter_required  # Bug? 当使用AJAX请求api时，不满足权限会造成重定向，但是ajax会将其忽略，以后再改。
@login_required
def api_delete_file():
    try:
        file_id = int(request.form['file_id'])
    except (TypeError, ValueError):  # TypeError: int(None)
        return jsonify({'errno': 100, 'errmsg': '参数错误'})
    else:
        user_id, user_name = g.user['id'], g.user['account']
        file_info = Sqlite3Query.get_file_info(file_id)
        if file_info is None:
            return jsonify({'errno': 106, 'errmsg': '文件不存在'})
        upload_time, file_name = file_info['upload_time'], file_info['file_name']
        if user_id != file_info['author_id']:
            return jsonify({'errno': 101, 'errmsg': '验证信息不符'})
            # 该用户想删除其他用户的文件
        new_file_name = get_new_filename(user_id, upload_time, file_name)

        db = get_db()
        db.execute(
            'DELETE FROM file WHERE id = ?', (file_id,)
        )
        db.commit()

        if db.total_changes == 1:  # 正常情况
            if os.path.exists(os.path.join(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], new_file_name)):
                try:
                    os.remove(os.path.join(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], new_file_name))
                except OSError:
                    return jsonify({'errno': 103, 'errmsg': '删除文件时出错'})
                else:
                    return jsonify({'errno': 0, 'errmsg': 'Successful delete'})
            else:
                return jsonify({'errno': 102, 'errmsg': '本地不存在文件'})
        elif db.total_changes == 0:  # 数据库中没有数据，按照道理来说，不可能执行到这里
            return jsonify({'errno': 104, 'errmsg': '删除时出现谜之错误，未删除成功'})
        else:  # db.total_changes 不为1或0
            return jsonify({'errno': 105, 'errmsg': '未知错误'})