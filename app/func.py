import pytz
import traceback
from datetime import datetime
from flask import current_app


def convert_time(timestamp, timezone=None, format_='%Y-%m-%d %H:%M:%S'):
    if timezone is None:  # 不在timezone默认参数处设置，是因为 Working outside of application context.
        timezone = current_app.config['TIMEZONE']
    try:
        time_ = datetime.fromtimestamp(
            timestamp, pytz.timezone(timezone)
        ).strftime(format_)
    except Exception:
        traceback.print_exc()
        return timestamp
    else:
        return time_
