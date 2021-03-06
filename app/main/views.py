import os
import pytz
import base64
import datetime
import time
from flask import current_app, render_template, redirect, url_for, g, session, abort, \
    flash, send_from_directory, make_response, request, send_file
from functools import wraps

from . import main
from app.db import get_db, Sqlite3Query
from app.func import convert_time


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
        file_info = Sqlite3Query.get_all_file_info()
        return render_template('base.html', files=file_info)
    else:
        return render_template('start.html')


@main.route('/file/<int:file_id>')
@enter_required
def show_file(file_id):
    file_info = Sqlite3Query.get_file_info(file_id)
    if file_info is not None:
        if g.user is not None:  # Add records about user.  未来将以装饰器实现
            db = get_db()
            db.execute(
                'INSERT INTO records (type_id, user_id, file_id, time) VALUES (?, ?, ?, ?)',
                (current_app.config['SIGN_CODE']['BROWSE'], g.user['id'], file_info['id'], int(time.time()))
            )
            db.commit()

        file_name = str(file_info['author_id']) + '_' + str(file_info['upload_time']) + '_' + file_info['file_name']
        file_absolute_path = os.path.join(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], file_name)
        upload_folder = current_app.config['UPLOAD_FOLDER']

        if os.path.exists(file_absolute_path):
            try:
                file_type = file_name.split('.')[-1]
            except IndexError:
                return '<p>不支持的文件类型</p>'
            else:
                if file_type in FileClassification.text_type:
                    fo = TextFile(file_name, file_absolute_path, upload_folder, file_type)
                    html_tag = fo.html_tag()
                    if html_tag is not None:
                        return html_tag
                elif file_type in FileClassification.image_type:
                    fo = ImageFile(file_name, file_absolute_path, upload_folder, file_type)
                    try:
                        return fo.make_response()
                    except ResponseError:
                        abort(404)
                elif file_type in FileClassification.video_type:
                    fo = VideoFile(file_name, file_absolute_path, upload_folder, file_type)
                    return render_template('/file/video.html', file_path=fo.relative_path)
                elif file_type in FileClassification.pdf_type:
                    fo = PdfFile(file_name, file_absolute_path, upload_folder, file_type)
                    return render_template('/file/pdf.html', file_path=fo.relative_path)
                elif file_type in FileClassification.audio_type:
                    fo = AudioFile(file_name, file_absolute_path, upload_folder, file_type)
                    return render_template('/file/audio.html', file_path=fo.relative_path)
    abort(404)


class FileClassification:
    text_type = {'txt'}
    image_type = {'jpg', 'png'}
    video_type = {'mp4'}
    pdf_type = {'pdf'}  # 并不对等，pdf文件应该是更下一层的，这里的设计完全不合理。
    audio_type = {'mp3', 'wav'}


@main.route('/download/<int:file_id>')  # 与show_file view func 重复度太高...
@enter_required
def downloader(file_id):
    file_info = Sqlite3Query.get_file_info(file_id)
    if file_info is not None:
        if g.user is not None:  # Note: 这里只能统计到通过该url下载的记录，其他途径记录不到!!!
            db = get_db()
            db.execute(
                'INSERT INTO records (type_id, user_id, file_id, time) VALUES (?, ?, ?, ?)',
                (current_app.config['SIGN_CODE']['DOWNLOAD'], g.user['id'], file_info['id'], int(time.time()))
            )
            db.commit()
        file_name = str(file_info['author_id']) + '_' + str(file_info['upload_time']) + '_' + str(file_info['file_name'])
        file_absolute_path = os.path.join(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], file_name)
        if os.path.exists(file_absolute_path):
            return send_from_directory(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], file_name, as_attachment=True)
            # 下载必须加 as_attachment 这个参数
        else:
            abort(404)  # 本地不存在文件
    else:
        abort(404)  # 数据库无信息


@main.route('/upload/<path:file_name>')
@enter_required
def view_file(file_name):
    response = make_response(send_from_directory(current_app.config['ABSOLUTE_UPLOAD_FOLDER'], file_name))
    return response


@main.route('/exit')
@enter_required
def exit_web():
    session.clear()
    flash('You have successfully exited.')
    return redirect(url_for('main.homepage'))


class ResponseError(Exception):
    pass


class File:  # 未来修改该类，使能够直接使用数据库取出的数据，进行构建
    def __init__(self, file_name, file_absolute_path, upload_folder):
        self.file_name = file_name
        self.absolute_path = file_absolute_path
        self.upload_folder = upload_folder
        self.relative_path = os.path.join(self.upload_folder, self.file_name)

    def __str__(self):
        return self.absolute_path

    @property
    def file_content(self):
        try:
            with open(self.absolute_path, 'rb') as f:
                data = f.read()
            return data
        except FileNotFoundError:
            return None

    def make_response(self):
        if self.file_content is not None:
            response = make_response(self.file_content)
            return response
        raise ResponseError


class ImageFile(File):
    def __init__(self, file_name, file_absolute_path, upload_folder, file_type):
        super(ImageFile, self).__init__(file_name, file_absolute_path, upload_folder)
        self.file_type = file_type

    def html_tag(self):
        return None

    def make_response(self):
        try:
            response = super(ImageFile, self).make_response()
        except ResponseError:
            raise
        else:
            if self.file_type == 'jpg':
                response.headers['Content-Type'] = 'image/jpg'
            elif self.file_type == 'png':
                response.headers['Content-Type'] = 'image/png'
            return response


class TextFile(File):
    def __init__(self, file_name, file_absolute_path, upload_folder, file_type):
        super(TextFile, self).__init__(file_name, file_absolute_path, upload_folder)
        self.file_type = file_type
        self.html_model = '<pre style="white-space: pre-wrap; font-family: sans-serif;">{content}</pre>'

    def html_tag(self):
        if self.file_type == 'txt':
            try:
                with open(self.absolute_path, 'rt', encoding='utf-8') as f:
                    return self.html_model.format(content=f.read())
            except FileNotFoundError:
                return None
            except:  # Should have log file.
                return None
        else:
            return None


class VideoFile(File):
    def __init__(self, file_name, file_absolute_path, upload_folder, file_type):
        super(VideoFile, self).__init__(file_name, file_absolute_path, upload_folder)
        self.file_type = file_type


class PdfFile(File):
    def __init__(self, file_name, file_absolute_path, upload_folder, file_type):
        super(PdfFile, self).__init__(file_name, file_absolute_path, upload_folder)
        self.file_type = file_type


class AudioFile(File):
    def __init__(self, file_name, file_absolute_path, upload_folder, file_type):
        super(AudioFile, self).__init__(file_name, file_absolute_path, upload_folder)
        self.file_type = file_type
