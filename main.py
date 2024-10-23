# Standard library imports
import os
import logging
import sqlite3
import time as time_module
from datetime import datetime, date, time
from zoneinfo import ZoneInfo

# Third-party imports
import mattermostdriver

# Local application imports
from configs import (
    DB_PATH, 
    mattermost_url, 
    bot_token, 
    channel_id_attendance, 
    channel_id_birthday, 
    channel_id_admin, 
    channels_to_monitor,
    DEBUG
)
from commands import (
    help_command,
    record_attendance,
    record_missing,
    recent_records,
    edit_record,
    delete_record,
    record_vacation,
    get_team_status,
    get_monthly_report,
    add_member,
    update_member,
    delete_member,
    get_member,
    fix_database
)
from utils import (
    DateTimeValidator,
    BirthdayGreeter,
    BirthdayState,
    AutoCheckoutState,
    auto_checkout
)


def setup_logger():
    """Configure and return logger instance"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Create handlers
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('bot.log')

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Setup logger
logger = setup_logger()

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
        ######################################
        ### Attendance management commands ###
        ######################################
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
                    f"예시: `!missing 2024-08-01 09:00 18:00`\n"
                    f"\n"
                    f"Use: `!missing YYYY-MM-DD <time_in> <time_out>`\n"
                    f"Example: `!missing 2024-08-01 09:00 18:00`\n"
                )
            return record_missing(bot, c, conn, user_id, text[1], text[2], text[3])
        elif command == '!최근기록' or command == '!recentrecord':
            return recent_records(bot, c, conn, user_id)
        elif command == '!수정' or command == '!edit':
            if len(text) < 4:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!edit <인덱스> <날짜> <출근시간> <퇴근시간:선택> <위치:선택>`\n"
                    f"인덱스는 최근 7일 출퇴근 기록에서 선택한 인덱스입니다. '!최근기록'을 사용해 확인하세요.\n"
                    f"예시: `!edit 0 2024-08-01 09:00 18:00 집`\n"
                    f"\n"
                    f"Use: `!edit <index> <date> <time_in> <time_out:optional> <location:optional>`\n"
                    f"Index is selected from recent 7 days' attendance records. Use `!recentrecord` to check.\n"
                    f"Example: `!edit 0 2024-08-01 09:00 18:00 Home`\n"
                )
            return edit_record(bot, c, conn, user_id, text[1], text[2], text[3], text[4] if len(text) > 4 else None, text[5] if len(text) > 5 else None)
        elif command == '!삭제' or command == '!delete':
            if len(text) < 2:
                return (
                    f"## 잘못된 형식 (Invalid Format)\n"
                    f"올바른 사용법: `!delete <인덱스>`\n"
                    f"인덱스는 최근 7일 출퇴근 기록에서 선택한 인덱스입니다. '!최근기록'을 사용해 확인하세요.\n"
                    f"예시: `!delete 0`\n"
                    f"\n"
                    f"Use: `!delete <index>`\n"
                    f"Index is selected from recent 7 days' attendance records. Use `!recentrecord` to check.\n"
                    f"Example: `!delete 0`\n"
                )
            return delete_record(bot, c, conn, user_id, text[1])
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
                    date = datetime.strptime(text[1], "%Y-%m-%d").strftime("%Y-%m-%d")
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
                    datetime.strptime(text[1], "%Y-%m")
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

        ##################################
        ### Member management commands ###
        ##################################
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
        elif command == '!fixdatabase':
            try:
                return fix_database(bot, c, conn)
            except sqlite3.IntegrityError:
                return (
                    f"## 오류: 데이터베이스 오류 (Database Error)\n"
                    f"데이터베이스 오류가 발생했습니다.\n"
                    f"\n"
                    f"An error occurred in the database.\n"
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
    try:
        # Initialize timezone
        tz = ZoneInfo("Asia/Seoul")
        logger.debug("Timezone set to Asia/Seoul")
        
        # Initialize states using dataclasses
        monthly_birthday_state = BirthdayState()
        daily_birthday_state = BirthdayState()
        auto_checkout_state = AutoCheckoutState()

        # Date/Time validation
        validator = DateTimeValidator()

        # Birthday greetings
        greeter = BirthdayGreeter(c, conn)
        
        # Track message processing
        last_processed = int(datetime.now(tz).timestamp() * 1000)
        logger.info("Initial state initialized")

        # Time constants
        NOON = time(12, 0)
        MIDNIGHT = time(23, 59) if not DEBUG else time(0, 0)

        def process_messages(channel_id: str, last_processed: int) -> int:
            try:
                messages = bot.posts.get_posts_for_channel(
                    channel_id, 
                    params={'since': last_processed}
                )
                
                if not (posts := messages.get('posts')):
                    return last_processed

                logger.debug(f"Processing {len(posts)} messages from channel {channel_id}")
                
                for post in sorted(posts.values(), key=lambda x: x['create_at']):
                    if (post['user_id'] == bot_user_id or 
                        post.get('root_id') or 
                        post['create_at'] <= last_processed):
                        continue

                    if response := handle_message(post):
                        dm_channel = bot.channels.create_direct_message_channel(
                            [bot_user_id, post['user_id']]
                        )
                        bot.posts.create_post({
                            'channel_id': dm_channel['id'] if not DEBUG else channel_id_attendance,
                            'message': response
                        })
                        logger.info(f"Sent response to user {post['user_id']}")
                    
                    last_processed = max(last_processed, post['create_at'])
                
                return last_processed
            
            except Exception as e:
                logger.error(f"Error processing messages for channel {channel_id}: {e}")
                return last_processed

        while True:
            try:
                current_time = datetime.now(tz)
                current_date = current_time.date()

                # Handle birthday resets and checks
                if (monthly_birthday_state.last_date is None or 
                    current_time.month != monthly_birthday_state.last_date.month):
                    monthly_birthday_state.printed = False
                    monthly_birthday_state.last_date = current_date
                    logger.debug("Monthly birthday state reset")

                if (daily_birthday_state.last_date is None or 
                    current_date != daily_birthday_state.last_date):
                    daily_birthday_state.printed = False
                    daily_birthday_state.last_date = current_date
                    logger.debug("Daily birthday state reset")

                # Handle monthly birthday greetings
                if (current_time.day == 1 and 
                    current_time.hour == NOON.hour and
                    current_time.minute == NOON.minute and
                    not monthly_birthday_state.printed):
                    logger.info("Sending monthly birthday greetings")
                    if bday_response := greeter.get_monthly_greeting():
                        bot.posts.create_post({
                            'channel_id': channel_id_birthday,
                            'message': bday_response
                        })
                    monthly_birthday_state.printed = True

                # Handle daily birthday greetings
                if (current_time.hour == NOON.hour and
                    current_time.minute == NOON.minute and
                    not daily_birthday_state.printed):
                    logger.info("Sending daily birthday greetings")
                    if bday_response := greeter.get_daily_greeting():
                        bot.posts.create_post({
                            'channel_id': channel_id_birthday,
                            'message': bday_response
                        })
                    daily_birthday_state.printed = True
                
                # Handle auto-checkout and fix_database
                if (current_time.hour == MIDNIGHT.hour and
                    current_time.minute == MIDNIGHT.minute and
                    not auto_checkout_state.responded):
                    logger.info("Processing auto-checkout")
                    checkout_response = auto_checkout(bot, c, conn)
                    if checkout_response:
                        for user_id, response in checkout_response:
                            # Send a direct message to the user
                            dm_channel = bot.channels.create_direct_message_channel(
                                [bot_user_id, user_id]
                            )
                            bot.posts.create_post({
                                'channel_id': dm_channel['id'] if not DEBUG else channel_id_attendance,
                                'message': response
                            })
                    auto_checkout_state.responded = True

                    try:
                        fix_database(bot, c, conn)
                    except sqlite3.IntegrityError:
                        logger.error("Error fixing database")              

                # Process messages from all channels
                for channel_id in channels_to_monitor:
                    last_processed = process_messages(channel_id, last_processed)

                time_module.sleep(1)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time_module.sleep(5)  # Back off on error

    except Exception as e:
        logger.critical(f"Fatal error in main function: {e}")
        raise

if __name__ == "__main__":
    main()
