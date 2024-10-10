from configs import get_datetime


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
