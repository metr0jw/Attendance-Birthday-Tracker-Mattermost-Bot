import os
import json
import datetime
import pytz
from workalendar.asia import SouthKorea

def get_datetime(day=None):
    return datetime.datetime.now(pytz.utc).astimezone(tz)

def load_config():
    with open('configs.json') as f:
        return json.load(f)

tz = pytz.timezone('Asia/Seoul')
cal = SouthKorea()

configs = load_config()
DEBUG = configs['DEBUG']
mattermost_url = configs['mattermost_url']
bot_token = configs['bot_token']
if DEBUG:
    channel_id_attendance = channel_id_birthday = configs['channel_id_debug']
    DB_PATH = configs['db_path_debug']
else:
    channel_id_attendance = configs['channel_id_attendance']   # attendance channel
    channel_id_birthday = configs['channel_id_birthday']       # birthday channel
    # Use an environment variable with a default fallback
    DB_PATH = os.environ.get('DB_PATH', configs['db_path'])

channel_id_admin = configs['channel_id_admin']  # admin channel

channels_to_monitor = [channel_id_attendance, channel_id_admin]
