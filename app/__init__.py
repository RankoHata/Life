def get_new_filename(user_id, upload_time, file_name):
    try:
        new_filename = '_'.join((str(user_id), str(upload_time), file_name))
    except Exception:
        raise  # Should have a log.
    else:
        return new_filename
