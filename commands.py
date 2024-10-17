from datetime import date
from statistics import mean, stdev
import datetime

from configs import get_datetime, cal, channel_id_attendance
from utils import is_future, is_past


def help_command():
    help_message = (
        f"## Attendance Bot version 241018\n"
        f"# Bot Commands\n"
        f"All commands must start with a '!' character.\n"
        f"모든 명령어는 '!' 문자로 시작해야 합니다.\n"
        f"\n"
        f"Response will be sent to Direct Message.\n"
        f"응답은 DM으로 전송됩니다.\n"
        f"\n"
        f"## Available commands:\n"
        f"\n"
        f"### Help\n"
        f"- `!도움`, `!h`, `!help`\n"
        f"- 도움말 보기 Show this help message\n"
        f"- **Example:** `!도움` or `!h`\n"
        f"\n"
        f"### Attendance Commands\n"
        f"\n"
        f"#### Check-in\n"
        f"- `!출근`, `!in`\n"
        f"- 출근 Attend work\n"
        f"- **Example:** `!출근` or `!in`\n"
        f"\n"
        f"#### Check-out\n"
        f"- `!퇴근`, `!out`\n"
        f"- 퇴근 Leave work\n"
        f"- **Example:** `!퇴근` or `!out`\n"
        f"\n"
        f"#### Missing Attendance\n"
        f"- `!출퇴근누락 <일자> <출근시간> <퇴근시간>`, `!missing <date> <time_in> <time_out>`\n"
        f"- 누락된 출퇴근 기록 입력 Enter missing attendance\n"
        f"- **Example:** `!출퇴근누락 2024-12-31 09:00:00 18:00:00` or `!missing 2024-12-31 09:00:00 18:00:00`\n"
        f"\n"
        f"#### Look up recent records\n"
        f"- `!recentrecord`, `!최근기록`\n"
        f"- 최근 7일 출퇴근 기록 조회 Look up recent 7 days' attendance records\n"
        f"- **Example:** `!recentrecord` or `!최근기록`\n"
        f"\n"
        f"### Edit a Record\n"
        f"- `!수정 <인덱스> <날짜> <출근시간> <퇴근시간:선택> <위치:선택>`, `!edit <index> <date> <time_in> <time_out:optional> <location:optional>`\n"
        f"- 최근 7일 출퇴근 기록 수정 Edit a record within recent 7 days\n"
        f"- **Example:** `!수정 0 2024-12-31 09:00:00 18:00:00` or `!edit 0 2024-12-31 09:00:00 18:00:00`\n"
        f"- **Note:** Index는 최근 7일 출퇴근 기록에서 선택한 인덱스입니다. Index is selected from recent 7 days' attendance records.\n"
        f"\n"
        f"### Delete a Record\n"
        f"- `!삭제 <인덱스>`, `!delete <index>`\n"
        f"- 최근 7일 특정 출퇴근 기록 삭제 Delete a record within recent 7 days\n"
        f"- **Example:** `!삭제 0` or `!delete 0`\n"
        f"- **Note:** Index는 최근 7일 출퇴근 기록에서 선택한 인덱스입니다. Index is selected from recent 7 days' attendance records.\n"
        f"#### Vacation\n"
        f"- `!휴가 <휴가시작일> <휴가마감일> <사유>`, `!vacation <start_date> <end_date> <reason>`\n"
        f"- 휴가 기록 Record vacation\n"
        f"- **Example:** `!휴가 2024-12-31 2025-01-02 가족여행` or `!vacation 2024-12-31 2025-01-02 Family_trip`\n"
        f"\n"
        f"#### Team Status\n"
        f"- `!상태 <일자:선택>`, `!teamstatus <date:optional>`\n"
        f"- 출퇴근 상태 출력 Print all team members' statuses\n"
        f"- 일자를 지정하지 않으면 오늘의 상태 출력 Print all team members' statuses for the current date\n"
        f"- **Example:** `!상태` or `!상태 2024-12-31` or `!teamstatus` or `!teamstatus 2024-12-31`\n"
        f"\n"
        f"#### Monthly Report\n"
        f"- `!월간보고 <연도-월:선택>`, `!monthlyreport <year-month:optional>`\n"
        f"- 이번 달 출퇴근 보고서 출력 (자신의 보고서만) Print the monthly attendance report for the current month (your report only)\n"
        f"- 연도와 월을 지정하지 않으면 현재 달의 보고서 출력 Print the monthly attendance report for the specified year and month (your report only)\n"
        f"- **Example:** `!월간보고` or `!월간보고 2024-12` or `!monthlyreport` or `!monthlyreport 2024-12`\n"
        f"\n"
        f"### Member Management Commands\n"
        f"\n"
        f"#### Add Member\n"
        f"- `!멤버추가 <@아이디> <이름> <과정> <전화번호> <이메일> <생일>`, `!addmember <@user_id> <name> <position> <phone> <email> <birthday>`\n"
        f"- 멤버 추가 Add a member\n"
        f"- **Example:** `!멤버추가 @gdhong 홍길동 PhD 010-1234-5678 1970-01-01` or `!addmember @gdhong Gildong-Hong PhD 010-1234-5678 gdhong@kw.ac.kr 1970-01-01`\n"
        f"\n"
        f"#### Delete Member\n"
        f"- `!멤버삭제 <@아이디>`, `!deletemember <@user_id>`\n"
        f"- 멤버 삭제 Delete a member\n"
        f"- **Example:** `!멤버삭제 @gdhong` or `!deletemember @gdhong`\n"
        f"\n"
        f"#### Update Member\n"
        f"- `!멤버업데이트 <@아이디> <과정:선택> <전화번호:선택> <이메일:선택> <생일:선택>`, `!updatemember <@user_id> <position:optional> <phone:optional> <email:optional> <birthday:optional>`\n"
        f"- 멤버 정보 업데이트 Update member info (optional)\n"
        f"- **Example:** `!멤버업데이트 @gdhong PhD 010-1234-5678 gdhong@kw.ac.kr 1970-01-01` or `!updatemember @gdhong PhD 010-1234-5678`\n"
        f"\n"
        f"#### Member Info\n"
        f"- `!멤버조회 <@아이디>`, `!memberinfo <@user_id>`\n"
        f"- 멤버 정보 조회 Get member info\n"
        f"- **Example:** `!멤버조회 @gdhong` or `!memberinfo @gdhong`\n"
        f"\n"
        f"## Developer Information\n"
        f"\n"
        f"- **Developer:** Jiwoon Lee 이지운\n"
        f"- **GitHub:** [metr0jw](https://github.com/metr0jw)\n"
        f"\n"
        f"Contact me if you have any questions or suggestions.\n"
        f"질문이나 제안이 있으면 연락주세요.\n"
    )
    return help_message

def record_attendance(bot, c, conn, user_id, action, location):
    now = get_datetime()
    date = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")
    
    if action == 'in':
        # Check if there's an existing 'in' record without an 'out' for the same day
        c.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ? AND time_out IS NULL", (user_id, date))
        existing_record = c.fetchone()
        
        if existing_record:
            return f"Error: You are already checked in for {date}. Please check out first."
        else:
            c.execute("INSERT INTO attendance VALUES (?, ?, ?, ?, ?)", 
                    (user_id, date, time_now, None, location))
    elif action == 'out':
        c.execute("UPDATE attendance SET time_out = ?, location = ? WHERE user_id = ? AND date = ? AND time_out IS NULL", 
                (time_now, location, user_id, date))
        if c.rowcount == 0:
            return f"Error: No active check-in found for {date}. Please check in first."

    conn.commit()
    return (
        f"## 출퇴근 기록 (Attendance Record)\n"
        f"- **행동 (Action):** {action.capitalize()}\n"
        f"- **날짜 (Date):** {date}\n"
        f"- **시간 (Time):** {time_now}\n"
        f"- **위치 (Location):** {location}\n"
        f"- **상태 (Status):** 성공적으로 기록됨 (Successfully recorded)\n"
    )

def record_missing(bot, c, conn, user_id, date, time_in, time_out=None):
    # Check if future date, which is not allowed
    if is_future(date):
        return (
            f"## 누락된 출퇴근 기록 (Missing Attendance Recorded)\n"
            f"- **날짜 (Date):** {date}\n"
            f"- **상태 (Status):** 미래 날짜는 기록할 수 없습니다 (Cannot record future dates)\n"
        )
    
    if time_out:
        if is_past(time_out, time_in):
            return (
                f"## 누락된 출퇴근 기록 (Missing Attendance Recorded)\n"
                f"- **날짜 (Date):** {date}\n"
                f"- **상태 (Status):** 퇴근 시간이 출근 시간보다 빠를 수 없습니다 (Check-out time cannot be earlier than check-in time)\n"
            )
        c.execute("INSERT INTO attendance VALUES (?, ?, ?, ?, ?)", 
                  (user_id, date, time_in, time_out, "Manual Entry"))
    else:
        c.execute("UPDATE attendance SET time_out = ? WHERE user_id = ? AND date = ?", 
                  (time_in, user_id, date))
    conn.commit()
    return (
        f"## 누락된 출퇴근 기록 (Missing Attendance Recorded)\n"
        f"- **날짜 (Date):** {date}\n"
        f"- **상태 (Status):** 성공적으로 기록됨 (Successfully recorded)\n"
    )

def recent_records(bot, c, conn, user_id):
    # Print recent 7 days' attendance records
    c.execute("SELECT * FROM attendance WHERE user_id = ? ORDER BY date DESC LIMIT 7", (user_id,))
    records = reversed(c.fetchall())

    if not records:
        return "No recent attendance records found."
    
    recent_records = []
    for idx, record in enumerate(records):
        user_id, date, time_in, time_out, location = record
        recent_records.append(f"{idx}. **{date}**: {time_in} - {time_out if time_out else 'Not checked out'}")
    
    return (
        f"## 최근 출퇴근 기록 (Recent Attendance Records)\n"
        + "\n".join(recent_records)
    )

def edit_record(bot, c, conn, user_id, index, date, time_in, time_out=None, location=None):
    # Edit a record within recent 7 days (0-indexed)
    # Index is described in the recent_records function
    # Check if future date, which is not allowed
    if is_future(date):
        return (
            f"## 출퇴근 기록 수정 (Attendance Record Edited)\n"
            f"- **날짜 (Date):** {date}\n"
            f"- **상태 (Status):** 미래 날짜는 수정할 수 없습니다 (Cannot edit future dates)\n"
        )
    
    c.execute("SELECT * FROM attendance WHERE user_id = ? ORDER BY date DESC LIMIT 7", (user_id,))
    records = list(reversed(c.fetchall()))

    if not records:
        return "No recent attendance records found."
    
    try:
        # Select the record corresponding to the index
        record = records[int(index)]
        user_id, date_old, time_in_old, time_out_old, location_old = record
        
    except IndexError:
        return "Error: Invalid record index."
    if time_out:
        if is_past(time_out, time_in):
            return (
                f"## 출퇴근 기록 수정 (Attendance Record Edited)\n"
                f"- **날짜 (Date):** {date}\n"
                f"- **상태 (Status):** 퇴근 시간이 출근 시간보다 빠를 수 없습니다 (Check-out time cannot be earlier than check-in time)\n"
            )
        c.execute("UPDATE attendance SET date = ?, time_in = ?, time_out = ?, location = ? WHERE user_id = ? AND date = ? AND time_in = ?", 
                    (date, time_in, time_out, location if location else location_old, user_id, date_old, time_in_old))
    else:
        c.execute("UPDATE attendance SET date = ?, time_in = ?, location = ? WHERE user_id = ? AND date = ? AND time_in = ?",
                    (date, time_in, location if location else location_old, user_id, date_old, time_in_old))
    conn.commit()
    return (
        f"## 출퇴근 기록 수정 (Attendance Record Edited)\n"
        f"- **날짜 (Date):** {date}\n"
        f"- **시간 (Time):** {time_in} - {time_out if time_out else 'Not checked out'}\n"
        f"- **위치 (Location):** {location}\n"
        f"- **상태 (Status):** 성공적으로 수정됨 (Successfully edited)\n"
    )

def delete_record(bot, c, conn, user_id, index):
    # Delete a record within recent 7 days (0-indexed)
    # Index is described in the recent_records function
    c.execute("SELECT * FROM attendance WHERE user_id = ? ORDER BY date DESC LIMIT 7", (user_id,))
    records = list(reversed(c.fetchall()))

    if not records:
        return "No recent attendance records found."
    
    try:
        record = records[int(index)]
    except IndexError:
        return "Error: Invalid record index."
    
    user_id, date, time_in, time_out, location = record
    c.execute("DELETE FROM attendance WHERE user_id = ? AND date = ?", (user_id, date))
    conn.commit()
    return (
        f"## 출퇴근 기록 삭제 (Attendance Record Deleted)\n"
        f"- **날짜 (Date):** {date}\n"
        f"- **시간 (Time):** {time_in} - {time_out if time_out else 'Not checked out'}\n"
        f"- **위치 (Location):** {location}\n"
        f"- **상태 (Status):** 성공적으로 삭제됨 (Successfully deleted)\n"
    )

def record_vacation(bot, c, conn, user_id, start_date, end_date, reason):
    c.execute("INSERT INTO vacations VALUES (?, ?, ?, ?)", 
              (user_id, start_date, end_date, reason))
    conn.commit()
    return (
        f"## 휴가 기록 (Vacation Record)\n"
        f"- **시작일 (Start Date):** {start_date}\n"
        f"- **종료일 (End Date):** {end_date}\n"
        f"- **상태 (Status):** 성공적으로 기록됨 (Successfully recorded)\n"
    )

def get_team_status(bot, c, conn, day=None):
    # Get the attendance status of all team members for the current date if date is not specified    
    if day is None:
        # Get the current date in the team's timezone
        now = get_datetime()
        day = now.strftime("%Y-%m-%d")
    
    # Check if the day is a holiday
    y, m, d = map(int, day.split('-'))
    if cal.is_holiday(date(y, m, d)):
        return "#### :calendar: Team Status\n**The date is not a working day.**"
    
    status_messages = []
    
    # Get team members
    # Get channel info to retrieve team_id
    channel_info = bot.channels.get_channel(channel_id_attendance)
    team_id = channel_info['team_id']
    team_members = bot.teams.get_team_members(team_id)

    for member in team_members:
        user_id = member['user_id']
        user = bot.users.get_user(user_id)
        
        # Skip bots and deactivated users
        if user.get('is_bot') or user.get('delete_at') != 0:
            continue

        username = user['username']  # You can choose 'first_name', 'last_name', 'nickname' as preferred
        
        # Get attendance status
        c.execute("SELECT * FROM attendance WHERE user_id = ? AND date = ?", (user_id, day))
        attendance = c.fetchone()
        
        # Check for vacation
        c.execute("SELECT * FROM vacations WHERE user_id = ? AND ? BETWEEN start_date AND end_date", (user_id, day))
        vacation = c.fetchone()
        
        if vacation:
            status = ":palm_tree: On vacation"
        elif attendance:
            if attendance[3]:  # time_out
                status = ":door: Left work"
            else:
                status = ":computer: At work"
        else:
            status = ":warning: No attendance record"
        
        status_messages.append(f"- **{username}**: {status}")
    
    if status_messages:
        return f"#### :busts_in_silhouette: Team Status for {day}\n" + "\n".join(status_messages)
    else:
        return "#### :warning: Team Status\n**No team members with attendance records found.**"

def get_monthly_report(bot, c, conn, requested_user, year=None, month=None):
    if year is None or month is None:
        now = get_datetime()
        year = now.strftime("%Y")
        month = now.strftime("%m")
    
    c.execute("SELECT * FROM attendance WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?", (year, month))
    records = c.fetchall()
    
    report = {}
    
    for record in records:
        user_id, date, time_in, time_out, location = record
        
        if user_id not in report:
            report[user_id] = {}
        if date not in report[user_id]:
            report[user_id][date] = []
        if time_out is None:
            # Ignore records without a check-out time
            continue
        
        report[user_id][date].append((time_in, time_out, location))

    # Calculate statistics
    requested_user_hours = []
    all_users_hours = []
    all_users_attended_days = set()
    requested_user_attended_days = set()

    for user_id, user_records in report.items():
        for date, day_records in user_records.items():
            daily_hours = 0
            for time_in, time_out, location in day_records:
                time_in_dt = datetime.datetime.strptime(time_in, "%H:%M:%S")
                time_out_dt = datetime.datetime.strptime(time_out, "%H:%M:%S")
                hours_worked = (time_out_dt - time_in_dt).total_seconds() / 3600
                daily_hours += hours_worked
            
            all_users_hours.append(daily_hours)
            all_users_attended_days.add(date)
            
            if user_id == requested_user:
                requested_user_hours.append(daily_hours)
                requested_user_attended_days.add(date)

    # Calculate requested user's stats
    if requested_user_hours:
        requested_user_avg_hours = mean(requested_user_hours)
        requested_user_stdev_hours = stdev(requested_user_hours) if len(requested_user_hours) > 1 else 0
        requested_user_stats = f"#### Requested User Stats\n" \
                               f"- **Avg hours**: {requested_user_avg_hours:.2f}\n" \
                               f"- **Stdev**: {requested_user_stdev_hours:.2f}\n" \
                               f"- **Attended days**: {len(requested_user_attended_days)}"
    else:
        requested_user_stats = "#### Requested User Stats\n**No attendance records**"

    # Calculate all users' average hours
    if all_users_hours:
        all_users_avg_hours = mean(all_users_hours)
        all_users_avg_attended_days = len(all_users_attended_days) / len(report)
        all_users_stats = f"#### All Users Stats\n" \
                          f"- **Avg hours**: {all_users_avg_hours:.2f}\n" \
                          f"- **Avg attended days**: {all_users_avg_attended_days:.2f}"
    else:
        all_users_stats = "#### All Users Stats\n**No attendance records**"

    return f"{requested_user_stats}\n\n{all_users_stats}"


################################
### Member Management System ###
################################
def add_member(bot, c, conn, user_id, username, position, phone, email, birthday):
    # table name: members_info
    # columns: user_id, name, phone, email, birthday
    c.execute("INSERT INTO members_info VALUES (?, ?, ?, ?, ?, ?)", 
              (user_id, username, position, phone, email, birthday))
    conn.commit()
    return f"Member added: {username}"

def delete_member(bot, c, conn, user_id):
    c.execute("DELETE FROM members_info WHERE user_id = ?", (user_id,))
    conn.commit()
    return "Member deleted"

def get_member(bot, c, conn, user_id):
    c.execute("SELECT * FROM members_info WHERE user_id = ?", (user_id,))
    member_info = c.fetchone()
    if member_info:
        user_id, name, position, phone, email, birthday = member_info

        # Birthday: format as 'YYYY-MM-DD'
        # Change to 'MM-DD' for privacy
        birthday = birthday[5:]     # '1970-01-01' -> '01-01'
        return f"#### Member Info\n" \
               f"- **Name**: {name}\n" \
               f"- **Position**: {position}\n" \
               f"- **Phone**: {phone}\n" \
               f"- **Email**: {email}\n" \
               f"- **Birthday**: {birthday}"
    else:
        return "#### Member Info\n**Member not found**"
    
def update_member(bot, c, conn, user_id, position=None, phone=None, email=None, birthday=None):
    # table name: members_info
    # columns: user_id, name, phone, email, birthday
    if position:
        c.execute("UPDATE members_info SET position = ? WHERE user_id = ?", (position, user_id))
    if phone:
        c.execute("UPDATE members_info SET phone = ? WHERE user_id = ?", (phone, user_id))
    if email:
        c.execute("UPDATE members_info SET email = ? WHERE user_id = ?", (email, user_id))
    if birthday:
        c.execute("UPDATE members_info SET birthday = ? WHERE user_id = ?", (birthday, user_id))
    conn.commit()
    return "Member info updated"
