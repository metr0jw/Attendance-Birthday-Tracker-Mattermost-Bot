import os

import mattermostdriver
import datetime
import sqlite3
import time

from configs import DB_PATH, mattermost_url, bot_token, channel_id_attendance, channel_id_birthday, channel_id_admin, channels_to_monitor
from commands import help_command, record_attendance, record_missing, record_vacation, get_team_status, get_monthly_report, \
    add_member, update_member, delete_member, get_member
from utils import birthday_greeting_daily, birthday_greeting_monthly


bot = mattermostdriver.Driver({
    'url': mattermost_url,
    'token': bot_token,
    'scheme': 'https',
    'port': 8443
})
bot.login()

# Get the bot's user ID
bot_user = bot.users.get_user(user_id='me')
bot_user_id = bot_user['id']

# Connect to the database
# Use DB_PATH when initializing your database connection
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS attendance
             (user_id TEXT, date TEXT, time_in TEXT, time_out TEXT, location TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS vacations
             (user_id TEXT, start_date TEXT, end_date TEXT, reason TEXT)''')

# Integrity check for user_id in members_info
# user_id is a unique key in members_info
c.execute('''CREATE TABLE IF NOT EXISTS members_info
                (user_id TEXT PRIMARY KEY, name TEXT, position TEXT, phone TEXT, email TEXT, birthday TEXT)''')

conn.commit()

def handle_message(post):
    try:
        user_id = post['user_id']
        message = post['message'].strip()
        
        # Check if the message starts with a slash command
        if not message.startswith('!'):
            return None  # Ignore messages that aren't commands
        
        text = message.split()
        command = text[0].lower()

        if command == '!도움' or command == '!h' or command == '!help' :
            return help_command()
        elif command == '!출근' or command == '!in':
            location = None
            return record_attendance(bot, c, conn, user_id, 'in', location if location is not None else 'Not specified')
        elif command == '!퇴근' or command == '!out':
            location = None
            return record_attendance(bot, c, conn, user_id, 'out', location if location is not None else 'Not specified')
        elif command == '!출퇴근누락' or command == '!missing':
            if len(text) < 4:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!missing YYYY-MM-DD <time_in> <time_out>`\n"
                    f"예시: `!missing 2024-08-01 09:00:00 18:00:00`\n"
                    f"\n"
                    f"Use: `!missing YYYY-MM-DD <time_in> <time_out>`\n"
                    f"Example: `!missing 2024-08-01 09:00:00 18:00:00`\n"
                )
            return record_missing(bot, c, conn, user_id, text[1], text[2], text[3])
        elif command == '!퇴근누락' or command == '!missingout':
            if len(text) < 3:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!missingout YYYY-MM-DD <time_out>`\n"
                    f"예시: `!missingout 2024-08-01 18:00:00`\n"
                    f"\n"
                    f"Use: `!missingout YYYY-MM-DD <time_out>`\n"
                    f"Example: `!missingout 2024-08-01 18:00:00`\n"
                )
            return record_missing(bot, c, conn, user_id, text[1], text[2])
        elif command == '!휴가' or command == '!vacation':
            if len(text) < 4:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!vacation YYYY-MM-DD(시작일) YYYY-MM-DD(종료일) <사유>`\n"
                    f"예시: `!vacation 2024-08-01 2024-08-05 가족여행`\n"
                    f"\n"
                    f"Use: `!vacation YYYY-MM-DD(start) YYYY-MM-DD(end) <reason>`\n"
                    f"Example: `!vacation 2024-08-01 2024-08-05 Family_vacation`\n"
                )
            return record_vacation(bot, c, conn, user_id, text[1], text[2], ' '.join(text[3:]))
        elif command == '!상태' or command == '!teamstatus':
            if len(text) > 1:
                # Check if the user provided a date
                try:
                    date = datetime.datetime.strptime(text[1], "%Y-%m-%d").strftime("%Y-%m-%d")
                    return get_team_status(bot, c, conn, date)
                except ValueError:
                    return (
                        f"## 오류: 잘못된 날짜 형식 (Error: Invalid date format)\n"
                        f"YYYY-MM-DD 형식을 사용하세요.\n"
                        f"예시: `!teamstatus 2024-08-01`\n"
                        f"\n"
                        f"Use YYYY-MM-DD format.\n"
                        f"Example: `!teamstatus 2024-08-01`\n"
                    )
            # Get the team status for the current date
            return get_team_status(bot, c, conn)
        elif command == '!월간보고' or command == '!monthlyreport':
            if len(text) > 1:
                # Check if the user provided a date
                try:
                    datetime.datetime.strptime(text[1], "%Y-%m")
                    requested_user = bot.users.get_user(user_id)['id']
                    return get_monthly_report(bot, c, conn, requested_user, text[1].split('-')[0], text[1].split('-')[1])
                except ValueError:
                    return (
                        f"## 오류: 잘못된 날짜 형식 (Error: Invalid date format)\n"
                        f"YYYY-MM 형식을 사용하세요.\n"
                        f"예시: `!monthlyreport 2024-08`\n"
                        f"\n"
                        f"Use YYYY-MM format.\n"
                        f"Example: `!monthlyreport 2024-08`\n"
                    )
            # Get the monthly report for the current month
            return get_monthly_report(bot, c, conn, user_id)
        elif command == '!멤버추가' or command == "!addmember":
            if len(text) < 7:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!addmember <사용자ID> <이름> <직위> <전화번호> <이메일> <생년월일>`\n"
                    f"예시: `!addmember @gdhong 홍길동 석사 010-1234-5678 gdhong@kw.ac.kr 1970-01-01`\n"
                    f"\n"
                    f"Use: `!addmember <user_id> <name> <position> <phone> <email> <birthday>`\n"
                    f"Example: `!addmember @gdhong Gildong_Hong MS 010-1234-5678 gdhong@kw.ac.kr 1970-01-01`\n"
                )
            try:
                return add_member(bot, c, conn, text[1], text[2], text[3], text[4], text[5], text[6])
            except sqlite3.IntegrityError:
                return (
                    f"## 오류: 멤버가 이미 존재함 (Error: Member already exists)\n"
                    f"멤버 {text[1]}가 이미 존재합니다.\n"
                    f"정보를 업데이트하려면 `!updatemember`를, 삭제하려면 `!deletemember`를 사용하세요.\n"
                    f"\n"
                    f"Member {text[1]} already exists.\n"
                    f"Use `!updatemember` to update the information or `!deletemember` to delete the member.\n"
                )
        elif command == '!멤버업데이트' or command == "!updatemember":
            if len(text) < 7:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!updatemember <사용자ID> <이름> <전화번호> <이메일> <생년월일>`\n"
                    f"예시: `!updatemember @gdhong 홍길동 박사 010-1234-5678 gdhong@kw.ac.kr 1970-01-01`\n"
                    f"\n"
                    f"Use: `!updatemember <user_id> <name> <phone> <email> <birthday>`\n"
                    f"Example: `!updatemember @gdhong Gildong_Hong PhD 010-1234-5678 gdhong@kw.ac.kr 1970-01-01`\n"
                )
            try:
                return update_member(bot, c, conn, text[1], text[2], text[3], text[4], text[5], text[6])
            except sqlite3.IntegrityError:
                return (
                    f"## 오류: 멤버가 존재하지 않음 (Error: Member does not exist)\n"
                    f"멤버 {text[1]}가 존재하지 않습니다.\n"
                    f"멤버를 추가하려면 `!addmember`를 사용하세요.\n"
                    f"\n"
                    f"Member {text[1]} does not exist.\n"
                    f"Use `!addmember` to add the member.\n"
                )
        elif command == '!멤버삭제' or command == "!deletemember":
            if len(text) < 2:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!deletemember <사용자ID>`\n"
                    f"예시: `!deletemember @gdhong`\n"
                    f"\n"
                    f"Use: `!deletemember <user_id>`\n"
                    f"Example: `!deletemember @gdhong`\n"
                )
            try:
                return delete_member(bot, c, conn, text[1])
            except sqlite3.IntegrityError:
                return f"Error: Member {text[1]} does not exist."
        elif command == '!멤버조회' or command == "!memberinfo":
            if len(text) < 2:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!memberinfo <사용자ID>`\n"
                    f"예시: `!memberinfo @gdhong`\n"
                    f"\n"
                    f"Use: `!memberinfo <user_id>`\n"
                    f"Example: `!memberinfo @gdhong`\n"
                )
            try:
                return get_member(bot, c, conn, text[1])
            except sqlite3.IntegrityError:
                return (
                    f"## 오류: 멤버를 찾을 수 없음 (Error: Member not found)\n"
                    f"멤버 {text[1]}를 찾을 수 없습니다.\n"
                    f"\n"
                    f"Member {text[1]} does not exist.\n"
                )
        else:
            return (
                f"## 알 수 없는 명령어 (Unknown command)\n"
                f"도움말을 보려면 `!h`를 사용하세요.\n"
                f"\n"
                f"Use `!h` for help.\n"
            )
    except KeyError as e:
        return (
            f"## 오류: 필수 필드 누락 (Error: Missing required field)\n"
            f"메시지에서 필수 필드가 누락되었습니다: {str(e)}\n"
            f"\n"
            f"Missing required field in message: {str(e)}\n"
        )
    except IndexError:
        return (
            f"## 오류: 잘못된 명령어 형식 (Error: Invalid command format)\n"
            f"도움말을 보려면 `!h`를 사용하세요.\n"
            f"\n"
            f"Use `!h` for help.\n"
        )
    except Exception as e:
        return (
            f"## 예기치 않은 오류 발생 (An unexpected error occurred)\n"
            f"오류 내용: {str(e)}\n"
            f"\n"
            f"Error details: {str(e)}\n"
        )
    
def main():
    # Initialize last_processed to the current time in milliseconds
    last_processed = int(datetime.datetime.now().timestamp() * 1000)

    # Initialize the daily birthday greeting variables
    birthday_printed_monthly = False
    last_birthday_date_monthly = None
    birthday_printed_daily = False
    last_birthday_date_daily = None

    while True:
        ### Post birthday greetings every day at 12:00 PM ###
        now = datetime.datetime.now()

        # Reset birthday_printed at the start of a new month
        if last_birthday_date_monthly is None or now.month != last_birthday_date_monthly:
            birthday_printed_monthly = False
        
        # Reset birthday_printed at the start of a new day
        if last_birthday_date_daily is None or now.date() != last_birthday_date_daily:
            birthday_printed_daily = False

        # Post birthday greetings at 12:00 PM on the first day of the month
        if now.day == 1 and now.hour == 12 and not birthday_printed_monthly:
            bday_response = birthday_greeting_monthly(bot, c, conn)
            if bday_response:
                bot.posts.create_post({
                    'channel_id': channel_id_birthday,
                    'message': bday_response
                })
            # Mark the birthday greeting as printed and update the date
            birthday_printed_monthly = True
            last_birthday_date_monthly = now.month

        # Post birthday greetings at 12:00 PM
        if now.hour == 12 and not birthday_printed_daily:
            bday_response = birthday_greeting_daily(bot, c, conn)
            if bday_response:
                bot.posts.create_post({
                    'channel_id': channel_id_birthday,
                    'message': bday_response
                })
            # Mark the birthday greeting as printed and update the date
            birthday_printed_daily = True
            last_birthday_date_daily = now.date()

        # Fetch messages since the last processed timestamp
        # Process messages from multiple channels
        for channel_id in channels_to_monitor:
            messages = bot.posts.get_posts_for_channel(channel_id, params={'since': last_processed})
            posts = messages.get('posts', {})
            if not posts:
                continue
            # Process messages in the order they were posted
            ordered_post_ids = sorted(posts, key=lambda x: posts[x]['create_at'])
            for post_id in ordered_post_ids:
                post = posts[post_id]

                # Skip messages from the bot itself
                if post['user_id'] == bot_user_id:
                    continue
                # Skip replies
                if post.get('root_id'):
                    continue
                # Skip processed messages
                if post['create_at'] <= last_processed:
                    continue
                
                response = handle_message(post)
                if response:
                    # Send the response to individual users in a direct message
                    dm_channel = bot.channels.create_direct_message_channel([bot_user_id, post['user_id']])
                    bot.posts.create_post({
                        'channel_id': dm_channel['id'],
                        'message': response
                    })
                # Update last_processed to the latest timestamp
                timestamp = post['create_at']
                if timestamp > last_processed:
                    last_processed = timestamp

        time.sleep(1)

if __name__ == "__main__":
    main()
