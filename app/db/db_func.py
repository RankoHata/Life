from .db_base import get_db


class Sqlite3Query:
    def get_records_info(user_id):
        sql_statement = '''
        select file_id, time, file_name, type_id from records 
        inner join user on records.user_id == ? 
        and records.user_id == user.id inner join 
        file on records.file_id == file.id 
        order by records.time desc limit 10
        '''
        db = get_db()
        records_info = db.execute(
            sql_statement, (user_id, )
        ).fetchall()
        records_info = tuple(dict(item) for item in records_info)
        return records_info
