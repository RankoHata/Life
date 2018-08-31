import os
import pytz
import base64
import datetime
from flask import current_app, render_template, redirect, url_for, g, session, abort, \
    flash, send_from_directory, make_response
from functools import wraps

from . import main
from app.db import get_db


def enter_required(view_func):
    @wraps(view_func)
    def wrapped_func(*args, **kwargs):
        if g.certification is not True:
            return abort(404)
        return view_func(*args, **kwargs)
    return wrapped_func


@main.before_app_request
def check():
    verify_sign = session.get('certification')
    if verify_sign is True:
        g.certification = True
    else:
        g.certification = False


@main.route('/')
def homepage():
    if g.certification is True:
        db = get_db()
        files_info = db.execute(
            'SELECT file_name, account, upload_time FROM file INNER join '
            'user ON file.author_id = user.id order by file.upload_time desc'
        ).fetchall()
        print(files_info)
        files_info = [dict(item) for item in files_info]
        for file_info in files_info:
            file_info['new_file_name'] = file_info['account'] + '_' + str(file_info['upload_time'])\
                                         + '_' + file_info['file_name']
            file_info['upload_time'] = datetime.datetime.fromtimestamp(  # 设定时区，默认中国
                file_info['upload_time'], pytz.timezone('Asia/Shanghai')
            ).strftime('%Y-%m-%d %H:%M:%S')
        return render_template('base.html', files=files_info)
    else:
        return render_template('start.html')


@main.route('/file/<path:file_name>')
@enter_required
def show_file(file_name):
    file_absolute_path = os.path.join(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], file_name)
    if file_name.endswith('txt'):
        try:
            with open(file_absolute_path, 'rt', encoding='utf-8') as f:
                return '<pre style="white-space: pre-wrap; font-family: sans-serif;">' + f.read() + '</pre>'
        except FileNotFoundError:
            pass
    elif file_name.endswith('jpg') or file_name.endswith('png'):
        try:
            with open(file_absolute_path, 'rb') as f:
                image_data = f.read()
        except FileNotFoundError:
            abort(404)
        else:
            response = make_response(image_data)
            if file_name.endswith('jpg'):
                response.headers['Content-Type'] = 'image/jpg'
            elif file_name.endswith('png'):
                response.headers['Content-Type'] = 'image/png'
            return response
    elif file_name.endswith('mp4'):
        if os.path.exists(file_absolute_path):
            file_relative_path = current_app.config['UPLOAD_FOLDER'] + '/' + file_name
            # 这里不使用os.path.join()，web前端使用'/'作分隔符
            print(file_relative_path)
            return render_template('/file/video.html', file_path=file_relative_path)
        else:
            abort(404)
    abort(404)


@main.route('/download/<path:file_name>')
@enter_required
def downloader(file_name):
    return send_from_directory(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], file_name, as_attachment=True)


@main.route('/exit')
@enter_required
def exit_web():
    session.clear()
    flash('You have successfully exited.')
    return redirect(url_for('main.homepage'))
