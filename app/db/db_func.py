from .db_base import get_db
from flask import current_app, g
from time import time


class Sqlite3Query:
    def get_records_info(user_id):
        sql_statement = '''
        select file_id, time, file_name, type_id from records 
        inner join user on records.user_id = ? 
        and records.user_id = user.id inner join 
        file on records.file_id = file.id 
        order by records.time desc limit 10
        '''
        db = get_db()
        records_info = db.execute(
            sql_statement, (user_id, )
        ).fetchall()
        records_info = tuple(dict(item) for item in records_info)
        return records_info

    def get_all_file_info():
        sql_statement = '''
        select file.id, author_id, upload_time, file_name, account 
        from file inner join user on file.author_id = user.id 
        order by file.upload_time desc
        '''
        db = get_db()
        files_info = db.execute(
            sql_statement
        ).fetchall()
        files_info = tuple(dict(item) for item in files_info)
        return files_info

    def get_file_info(file_id):
        sql_statement = '''
        select * from file where id = ?
        '''
        db = get_db()
        file_info = db.execute(
            sql_statement, (file_id,)
        ).fetchone()
        return file_info
