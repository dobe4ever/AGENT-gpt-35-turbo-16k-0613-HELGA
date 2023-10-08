import os
import threading
from telegram.ext import Updater, MessageHandler, Filters, PollAnswerHandler
from keep_alive import keep_alive_ping, keep_alive
from gpt_utils import handle_message
from functions_utils import handle_poll_answer
from database import fetch_and_send_reminders
from threading import Thread


keep_alive_ping()

# Define the Telegram bot token from the environment variable
bot_token = os.environ['BOT_TOKEN']

# Create an instance of the Updater class using the bot token
updater = Updater(token=bot_token, use_context=True)
dp = updater.dispatcher

# Register the message handlers with the dispatcher
dp.add_handler(MessageHandler(Filters.text | Filters.entity, handle_message))

# Add the PollAnswerHandler for poll answers
dp.add_handler(PollAnswerHandler(handle_poll_answer))

# Start the bot
updater.start_polling()

# Create a separate thread for executing keep_alive
keep_alive_thread = threading.Thread(target=keep_alive)
keep_alive_thread.daemon = True
keep_alive_thread.start()

# Create a separate thread for checking for reminders
t = Thread(target=fetch_and_send_reminders)
t.daemon = True
t.start()

updater.idle()
updater.stop()