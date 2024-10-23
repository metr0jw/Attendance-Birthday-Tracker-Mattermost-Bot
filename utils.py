from datetime import datetime, timezone, date, time
from zoneinfo import ZoneInfo
from dataclasses import dataclass

from typing import Union, Optional, List, Tuple
import logging

SEOUL_TZ = ZoneInfo("Asia/Seoul")
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
BIRTHDAY_FORMAT = "%m-%d"

# Get the logger in main.py
logger = logging.getLogger('bot')

class DateTimeValidator:
    @staticmethod
    def is_future(date_str: str) -> bool:
        try:
            now = datetime.now(SEOUL_TZ)
            check_date = datetime.strptime(date_str, DATE_FORMAT).replace(
                tzinfo=SEOUL_TZ
            )
            return check_date.date() > now.date()
        except ValueError as e:
            logger.error(f"Date validation error: {e}")
            return False

    @staticmethod
    def is_past(date1: str, date2: str) -> bool:
        """Compare two dates/times and check if date1 is before date2."""
        try:
            if ':' in date1 and ':' in date2:
                # Time comparison
                return int(date1.replace(':', '')) < int(date2.replace(':', ''))
            
            # Date comparison
            date1_obj = datetime.strptime(date1, DATE_FORMAT)
            date2_obj = datetime.strptime(date2, DATE_FORMAT)
            return date1_obj < date2_obj
        except ValueError as e:
            logger.error(f"Date comparison error: {e}")
            return False

    @staticmethod
    def valid_date(date_str: str) -> bool:
        """Validate date string format."""
        try:
            datetime.strptime(date_str, DATE_FORMAT)
            return True
        except ValueError:
            return False

    @staticmethod
    def valid_time(time_str: str) -> bool:
        """Validate time string format."""
        try:
            datetime.strptime(time_str, TIME_FORMAT)
            return True
        except ValueError:
            return False

class BirthdayGreeter:
    def __init__(self, db_cursor, db_connection):
        self.cursor = db_cursor
        self.conn = db_connection

    def _format_greeting(self, members: list, is_monthly: bool) -> Optional[str]:
        """Format birthday greeting message."""
        if not members:
            return None

        period = "Monthly" if is_monthly else "Daily"
        greeting = [f"#### :birthday: {period} Birthday Greetings"]
        
        for member in members:
            user_id, name, *_ = member
            greeting.append(f"Happy birthday, {name}! :tada:")
        
        greeting.append(f"\n{len(members)} birthdays {'this month' if is_monthly else 'today'}! :confetti_ball:")
        return "\n".join(greeting)

    def get_daily_greeting(self) -> Optional[str]:
        """Get daily birthday greetings."""
        today = datetime.now(SEOUL_TZ).strftime(BIRTHDAY_FORMAT)
        self.cursor.execute(
            "SELECT * FROM members_info WHERE strftime('%m-%d', birthday) = ?", 
            (today,)
        )
        return self._format_greeting(self.cursor.fetchall(), False)

    def get_monthly_greeting(self) -> Optional[str]:
        """Get monthly birthday greetings."""
        current_month = datetime.now(SEOUL_TZ).strftime("%m")
        self.cursor.execute(
            "SELECT * FROM members_info WHERE strftime('%m', birthday) = ?", 
            (current_month,)
        )
        return self._format_greeting(self.cursor.fetchall(), True)


@dataclass
class BirthdayState:
    printed: bool = False
    last_date: Optional[date] = None

@dataclass
class AutoCheckoutState:
    responded: bool = False
    last_date: Optional[date] = None


def auto_checkout(bot, c, conn) -> List[Tuple[str, str]]:
    """
    Automatically check out users who haven't checked out for the day.
    Returns a list of tuples containing (user_id, response_message).
    """
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_midnight = time(23, 59).strftime("%H:%M")
    
    # Get all users who haven't checked out today
    c.execute("""
        SELECT user_id, location 
        FROM attendance 
        WHERE date = ? AND time_out IS NULL
    """, (date,))
    
    unchecked_users = c.fetchall()
    if not unchecked_users:
        return []

    # Batch update all records
    c.execute("""
        UPDATE attendance 
        SET time_out = ? 
        WHERE date = ? AND time_out IS NULL
    """, (time_midnight, date))
    
    conn.commit()

    # Generate response messages for each user
    responses = []
    for user_id, location in unchecked_users:
        message = (
            f"## 자동 퇴근 기록 (Auto Check-out)\n"
            f"- **행동 (Action):** Out\n"
            f"- **날짜 (Date):** {date}\n"
            f"- **시간 (Time):** {time_midnight}\n"
            f"- **위치 (Location):** {location}\n"
            f"- **상태 (Status):** 성공적으로 기록됨 (Successfully recorded)\n"
            f"- **자동 (Auto):** 23:59에 자동 퇴근됨 (Auto check-out at 23:59)\n"
        )
        responses.append((user_id, message))
    if responses:
        logger.info(f"Auto-checked out {len(responses)} users")
        return responses