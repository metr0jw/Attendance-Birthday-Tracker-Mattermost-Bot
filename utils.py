import datetime

from configs import get_datetime

def is_future(date):    # Timezone - Asia/Seoul
    now = get_datetime().replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    return date > now

def is_past(date1, date2):
    # if date1 and date 2 contains colon, :"HH:MM"
    # else, date1 and date2 contains only date, "YYYY-MM-DD"
    if ':' in date1 and ':' in date2:
        # Remove the colon and convert to int
        date1 = int(date1.replace(':', ''))
        date2 = int(date2.replace(':', ''))
    else:
        date1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    return date1 < date2    # True if date1 is in the past

def valid_date(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
def valid_time(time):
    try:
        datetime.datetime.strptime(time, "%H:%M")
        return True
    except ValueError:
        return False

def birthday_greeting_daily(bot, c, conn):
    now = get_datetime()
    today = now.strftime("%m-%d")
    
    c.execute("SELECT * FROM members_info WHERE strftime('%m-%d', birthday) = ?", (today,))
    members = c.fetchall()
    
    if members:
        greeting = "#### :birthday: Daily Birthday Greetings\n"
        num_birthdays = len(members)
        for member in members:
            user_id, name, position, phone, email, birthday = member
            greeting += f"Happy birthday, {name}! :tada:\n"
        greeting += f"\n{num_birthdays} birthdays today! :confetti_ball:"
        return greeting

def birthday_greeting_monthly(bot, c, conn):
    now = get_datetime()
    month = now.strftime("%m")
    
    c.execute("SELECT * FROM members_info WHERE strftime('%m', birthday) = ?", (month,))
    members = c.fetchall()
    
    if members:
        greeting = "#### :birthday: Monthly Birthday Greetings\n"
        num_birthdays = len(members)
        for member in members:
            user_id, name, position, phone, email, birthday = member
            greeting += f"Happy birthday, {name}! :tada:\n"
        greeting += f"\n{num_birthdays} birthdays this month! :confetti_ball:"
        return greeting

def auto_checkout_daily(bot, c, conn, user_id, action, location):
    now = get_datetime()
    date = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")
    
    # Auto check-out for users who haven't checked out yet, it will be called by a scheduled task
    c.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ? AND time_out IS NULL", (user_id, date))
    c.execute("UPDATE attendance SET time_out = ?, location = ? WHERE user_id = ? AND date = ? AND time_out IS NULL", 
            (time_now, location, user_id, date))

    conn.commit()
    return (
        f"## 자동 퇴근 기록 (Auto Check-out)\n" 
        f"- **행동 (Action):** {action.capitalize()}\n"
        f"- **날짜 (Date):** {date}\n"
        f"- **시간 (Time):** {time_now}\n"
        f"- **위치 (Location):** {location}\n"
        f"- **상태 (Status):** 성공적으로 기록됨 (Successfully recorded)\n"
        f"- **자동 (Auto):** 23:59:59에 자동 퇴근됨 (Auto check-out at 23:59:59)\n"
    )

def auto_checkout(bot, c, conn):
    # Get all users who have checked in but not checked out
    c.execute("SELECT * FROM attendance WHERE time_out IS NULL")
    records = c.fetchall()
    responses = []
    if records:
        for record in records:
            user_id, date, time_in, time_out, location = record
            responses.append([user_id, auto_checkout_daily(bot, c, conn, user_id, 'out', location)])
        return responses