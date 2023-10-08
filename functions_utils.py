import yfinance as yf
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import random
from telegram import Bot
from replit import db
from database import add_winners_to_db
import os
import re

# Define the Telegram bot token from the environment variable
bot_token = os.environ['BOT_TOKEN']
user_id = os.environ['USER_ID']
free_group = os.environ['FREE_GROUP']
test_group = os.environ['TEST_GROUP']
# Initialize the Telegram bot
bot = Bot(token=bot_token)


def send_poll(question, options):
    # Get the participants list from the database:
    participants = db['participants']
    #Shuffle the list randomly:
    random.shuffle(participants)
    #Get the first 3 elements as the winners:
    participants = participants[:3]
    print("Winning Participants:")
    print(participants)

    # Add winners to the remote db
    add_winners_to_db(participants=participants) 

    # Build the message string using the first_name and user_id from each winner dict:
    message = "Congratulations "
    
    for participant in participants:
      first_name = participant['first name'] 
      user_id = participant['user id']

      message += f"[{first_name}](tg://user?id={user_id}), "
    
    message = message.strip(", ") + ", 🎉 You each won last week's poll giveaway! Enjoy one month of free access to our Premium areas! Check your account now with our [@MembershipManager](https://t.me/Dobe_Members_Bot). Thanks everyone for participating! You can start voting on the new poll for a chance to win another free month of premium membership! Good luck! 🍀"
    
    # Send message to telegram group
    bot.send_message(chat_id=free_group, text=message, parse_mode="Markdown")
    print(message)

    # Send public poll effectlively starting a new weekly cycle with clean db
    poll_id_db = Bot(token=bot_token).send_poll(
        chat_id=free_group,
        question=question,
        options=options,
        is_anonymous=False,
    ).poll.id

    # Reset participants list
    participants = []
    # Save participants to the database
    db["participants"] = participants
    
    # Store the poll_id in the database
    db["poll_id_db"] = poll_id_db
    
    # ChatGPT gets this & answers accordingly
    return "Poll Sent Successfully!"


def handle_poll_answer(update, context):
    # If poll id's dont match, exit
    if db["poll_id_db"] != update.poll_answer.poll_id:
        return
    
    # Extract user id & public name
    user_id = update.poll_answer.user.id
    first_name = update.poll_answer.user.first_name

    # Save user's info to the list of participants in the db
    db["participants"].append({
      "user id": user_id, 
      "first name": first_name
    })
    

def get_timestamp():
    # Obtain the Bangkok timezone
    bangkok_timezone = pytz.timezone('Asia/Bangkok')
    # Obtain the current date and time in Bangkok
    now = datetime.now(bangkok_timezone)
    timestamp = now.strftime("%A, %d-%m-%Y %H:%M ")
    return timestamp


def get_yfinance(ticker, period):
    # Fetch historical data using yfinance
    data = yf.download(tickers=ticker, period=period)
    # Print the optimized data
    print("Original data:")
    print(data)
  
    # Reset the index
    data.reset_index(inplace=True)
    
    # Select only the necessary columns
    data = data[['Date', 'Close']]
    
    # Remove decimals from the Close prices
    data.loc[:, 'Close'] = data['Close'].astype(int).astype(str)

    # Print the optimized data
    print("Optimized data:")
    print(data)

    # Convert optimized data to json
    optimized_data = data.to_json()

    # Print the optimized data in json
    print("Optimized data json:")
    print(optimized_data)

    # Return the optimized data
    return json.dumps(optimized_data)


def perform_google_search(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    url = f"https://www.google.com/search?q={query}&num=5"
    html = requests.get(url, headers=headers)
    soup = BeautifulSoup(html.text, 'html.parser')
    allData = soup.find_all("div", {"class": "tF2Cxc"})
    
    g = 0
    Data = []
    
    for i in range(0, len(allData)):
        link_element = allData[i].find('a')
        title_element = allData[i].find('h3')
        
        if link_element and title_element:
            link = link_element.get('href')
            if link.startswith("/url?q="):
                link = link.split("/url?q=")[1].split("&")[0]  # Extract actual link
    
            title = title_element.text.strip()
            
            # Extracting the description using the class name "Z26q7c UK95Uc"
            description_element = allData[i].find("div", {"class": "Z26q7c UK95Uc"})
            description = description_element.text.strip() if description_element else None
            
            # Check if the description is not a date; if not, add the entry to Data
            if description and not re.match(r"^[A-Z][a-z]{2,8}\s\d{1,2},\s\d{4}$", description):
                g += 1
                data_entry = {
                    "link": link,
                    "title": title,
                    "description": description,
                    #"position": g
                }
                Data.append(data_entry)
    
    #print(json.dumps(data_entry, indent=4))
    print(json.dumps(Data, indent=4))
    # Move the return statement outside the loop
    return "\nSearch results:\n" + json.dumps(Data, indent=4)

# def handle_user_confirmation(update, context):
#     from telegram.ext import InlineKeyboardButton, InlineKeyboardMarkup

#     text = "Confirm with 'y' or 'n' if you want to write to " + "'" + filename + "'"
    
#     bot.send_message(chat_id=user_id, text=text)
    
#     query = update.callback_query
#     query.answer() 
#     # Create inline keyboard markup using the constant COIN_BUTTONS
#     reply_markup = InlineKeyboardMarkup(CONFIRMATION_BUTTONS)
#     query.message.edit_text('Now select a payment method:', reply_markup=reply_markup)
#     context.user_data['confirm or cancel write file'] = query.data



# def write_file(update, context, filename="test.txt", content="dummy text"):
#     from telegram.ext import InlineKeyboardButton, InlineKeyboardMarkup
    
#     query = update.callback_query
#     query.answer() 
    
#     CONFIRMATION_BUTTONS = [
#         InlineKeyboardButton("Confirm", callback_data='confirm'),
#         InlineKeyboardButton("Cancel", callback_data='cancel')
#     ]
#     reply_markup = InlineKeyboardMarkup(CONFIRMATION_BUTTONS)
#     query.send_message(chat_id=user_id, reply_markup=reply_markup)
    
#     # Create inline keyboard markup using the constant COIN_BUTTONS
#     reply_markup = InlineKeyboardMarkup(CONFIRMATION_BUTTONS)
#     query.message.edit_text("Confirm if you want to write to " + filename, reply_markup=reply_markup)
#     context.user_data['user confirmation'] = query.data
    
#     if 'user confirmation' == "confirm":
#         with open(filename, "w") as f:
#             f.write(content)
#         return "Successfully written file. Filename: " + filename + " . Content: " + content
#     else:
#         return "ERROR: Cancelled by the user."



def write_file(filename, content):
    sure = input("Do you want to write to " + filename + "? (y/n) ")
    if sure == "y":
        with open(filename, "w") as f:
            f.write(content)
        return "Successfully written file " + filename
    else:
        return "ERROR: Cancelled by the user."



def edit_messages(clear_conversation, content=None):
    # Read the content of the messages.json file
    with open('messages.json', 'r') as file:
        messages = json.load(file)

    if clear_conversation:
        # Clear conversation history by keeping only the first message
        messages = messages[:1]
    elif content is not None:
        # Update the content of the system message
        messages[0]['content'] = content

    # Write the updated messages back to the file
    with open('messages.json', 'w') as file:
        file.write(json.dumps(messages, indent=4))

    return "Successfully executed."


def add_bookmark(url, name, folder):   
    with open('bookmarks.json', 'r') as f:
        bookmarks = json.load(f)
    bookmark_id = len(bookmarks)
    new_bookmark = {
        "id": bookmark_id,
        "url": url,
        "name": name,
        "folder": folder
    }
    bookmarks.append(new_bookmark)
    with open('bookmarks.json', 'w') as f:
        json.dump(bookmarks, f, indent=4)

    return "Successfully executed."



def read_file(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
    return json.dumps(data)



