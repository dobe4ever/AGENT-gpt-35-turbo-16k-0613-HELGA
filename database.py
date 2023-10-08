#python3 database.py

from sqlalchemy import create_engine, text
import pytz
import datetime
import time
import os
from telegram import Bot

# Define the Telegram bot token from the environment variable
bot_token = os.environ['BOT_TOKEN']
user_id = os.environ['USER_ID']
# Initialize the Telegram bot
bot = Bot(token=bot_token)

# create connexion to remote database
remote_db = os.environ['DB_CONNECTION_STRING']
engine = create_engine(remote_db,
                       connect_args={"ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem"
                       }})


# 'reminders' table - columns: id, datetime, task
def fetch_and_send_reminders():
    while True:
        with engine.connect() as conn:
            query = text("SELECT * FROM reminders ORDER BY datetime DESC LIMIT 1")
            result = conn.execute(query)
            row = result.fetchone()
    
            if row:
                id, datetime, task = row
                
                local_time_now = datetime.now(pytz.timezone('Asia/Bangkok'))
                
                if datetime.strftime('%Y-%m-%d %H:%M') == local_time_now.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M'):   
                
                    bot.send_message(chat_id=int(user_id), text=task, parse_mode="Markdown")

        time.sleep(60)



def manage_reminders_table(sql_command):
    with engine.connect() as conn:
        result = conn.execute(text(sql_command))
        
        if 'SELECT' in sql_command:
            rows = result.fetchall()
            rows = str(rows)
            print(rows)
            return rows
        else:
            return "Executed successfully!"


def manage_users_table(sql_command):
    sure = input("Do you want to execute " + sql_command + "? (y/n) ")
    if sure == "y":
        with engine.connect() as conn:
            result = conn.execute(text(sql_command))
            
            if 'SELECT' in sql_command:
                rows = result.fetchall()
                rows = str(rows)
                print(rows)
                return rows
            else:
                return "Executed successfully!"


def add_winners_to_db(participants):

    with engine.connect() as conn:

        for participant in participants:

            user_id = participant['user id']
            first_name = participant['first name']

            print("Winner id & name: ")
            print(user_id, first_name)

            # Check if user exists
            result = conn.execute(
                text("SELECT * FROM users WHERE user_id = :user_id"),
                {'user_id': user_id})
            row = result.fetchone()

            if row:
                # User exists, update info
                conn.execute(
                    text(
                        "UPDATE users SET public_name = :public_name, active = 1, signup_date = :signup_date, expiration_date = :expiration_date WHERE user_id = :user_id"
                    ), {
                        'public_name':
                        first_name,
                        'signup_date':
                        datetime.date.today(),
                        'expiration_date':
                        datetime.date.today() + datetime.timedelta(days=30),
                        'user_id':
                        user_id
                    })

            else:
                # Add new user
                conn.execute(
                    text(
                        "INSERT INTO users (user_id, public_name, signup_date, expiration_date, active) VALUES (:user_id, :public_name, :signup_date, :expiration_date, 1)"
                    ), {
                        'user_id':
                        user_id,
                        'public_name':
                        first_name,
                        'signup_date':
                        datetime.date.today(),
                        'expiration_date':
                        datetime.date.today() + datetime.timedelta(days=30)
                    })

