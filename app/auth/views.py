from functools import wraps
from datetime import datetime
import pytz
from flask import flash, g, render_template, request, session, url_for, redirect, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import get_db, Sqlite3Query
from app.main.views import enter_required
from . import auth


@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


def login_required(view_func):
    @wraps(view_func)
    def wrapped_func(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapped_func


@auth.route('/login', methods=('POST', 'GET'))
@enter_required
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        db = get_db()
        error_msg = None
        user = db.execute(
            'SELECT * FROM user WHERE account = ?', (account,)
        ).fetchone()
        if user is None:
            error_msg = 'Incorrect DMYX account.'
        elif not check_password_hash(user['password'], password):
            error_msg = 'Incorrect EMYX password.'
        if error_msg is None:
            session.clear()
            session['certification'] = True
            session['user_id'] = user['id']
            return redirect(url_for('main.homepage'))
        else:
            flash(error_msg)
    return render_template('login.html')


@auth.route('/logout')
@enter_required
@login_required
def logout():
    session.clear()
    session['certification'] = True
    flash('You have successfully logged out.')
    return redirect(url_for('main.homepage'))


@auth.route('/register', methods=('POST', 'GET'))
@enter_required
def register():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        db = get_db()
        error_msg = None
        user = db.execute(
            'SELECT * FROM user WHERE account = ?', (account,)
        ).fetchone()
        if not account or not password:
            error_msg = 'Account and password is required.'
        elif user is not None:
            error_msg = 'Account is already registered.'
        else:
            hash_password = generate_password_hash(password)
            db.execute(
                'INSERT INTO user (account, password) VALUES (?, ?)',
                (account, hash_password)
            )
            db.commit()
            return redirect(url_for('main.homepage'))
        flash(error_msg)
    return render_template('register.html')


@auth.route('/file/upload')
@enter_required
@login_required
def upload_file():
    return render_template('file/upload.html')


@auth.route('/history')
@enter_required
@login_required
def display_history():
    records_info = Sqlite3Query.get_records_info(g.user['id'])
    for record in records_info:
        record['time'] = datetime.fromtimestamp(
            record['time'], pytz.timezone('Asia/Shanghai')
        ).strftime("%Y-%m-%d %H:%M:%S")
    return render_template(
        'history.html', 
        records_info=records_info, 
        sign=current_app.config['SIGN_CODE']
    )
