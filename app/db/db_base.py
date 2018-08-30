import sqlite3
import logging
from flask import current_app, g


def get_db():
    if not hasattr(g, 'db'):
        try:
            g.db = sqlite3.connect(current_app.config['DATABASE'])
        except Exception:
            raise
        else:
            g.db.row_factory = sqlite3.Row
            return g.db
    else:
        return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        logging.debug('Patchouli Knowledge...')


def init_db(app):
    app.teardown_appcontext(close_db)
