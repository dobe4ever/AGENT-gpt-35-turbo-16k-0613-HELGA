import os
import openai
import json
from telegram import Bot
from functions import functions
from database import manage_users_table, manage_reminders_table
from functions_utils import perform_google_search, write_file, read_file, get_timestamp, add_bookmark, send_poll


# Define the OpenAI API key from the environment variable
openai.api_key = os.environ['OPENAI_API_KEY']

# Define the Telegram bot token from the environment variable
bot_token = os.environ['BOT_TOKEN']
user_id = os.environ['USER_ID']
free_group = os.environ['FREE_GROUP']
test_group = os.environ['TEST_GROUP']

# Initialize the Telegram bot
bot = Bot(token=bot_token)

def handle_message(update, context):
    # Get timestamp
    timestamp = get_timestamp()
    # Get the user's message
    user_message = update.message.text
    # user_message
    user_message = timestamp + user_message

    # Check if the message was sent from your user ID
    if update.message.from_user.id == int(user_id):    
        # Load existing messages from the file
        with open("messages.json", "r") as f:
            messages = json.load(f)
            
        # Append the new user message to the messages list
        messages.append({
            "role": "user",
            "content": user_message
        })  
        
        # Save the updated messages list back to the file
        with open("messages.json", "w") as f:
            f.write(json.dumps(messages, indent=4))
            
        # Use only system message & 10 most recent messages
        messages = [messages[0]] + messages[-10:]
        # Step 1: send the conversation and available functions to GPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # "gpt-4"
            messages=messages,
            functions=functions,
            function_call="auto"  # auto is default, but we'll be explicit      
        )
        response_message = response['choices'][0]['message']
        
        # Step 2: check if GPT wanted to call a function
        if response_message.get("function_call"):
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "perform_google_search": perform_google_search,
                "write_file": write_file,
                "read_file": read_file,
                "add_bookmark": add_bookmark,
                "send_poll": send_poll,
                "manage_users_table": manage_users_table,
                "manage_reminders_table": manage_reminders_table,
            }  
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])

            if function_name == "perform_google_search":
                function_response = function_to_call(
                    query=function_args.get("query")
                )
            elif function_name == "manage_reminders_table":
                function_response = function_to_call(
                    sql_command=function_args.get("sql_command")
                )                
            elif function_name == "write_file":
                function_response = function_to_call(
                    filename=function_args.get("filename"),
                    content=function_args.get("content")
                )              
            elif function_name == "read_file":
                function_response = function_to_call(
                    file_path=function_args.get("file_path") 
                )
               
            elif function_name == "add_bookmark":
                function_response = function_to_call(
                    url=function_args.get("url"), 
                    name=function_args.get("name"),
                    folder=function_args.get("folder") 
                )
            elif function_name == "send_poll":
                function_response = function_to_call(
                    question=function_args.get("question"),
                    options=function_args.get("options")
                )
                return  # Poll & message are already sent, no need GPT to respond
                
            elif function_name == "manage_users_table":
                # sure = input("Do you want to execute the SQL command above? (y/n) ")
                # if sure == "y":   
                function_response = function_to_call(
                    sql_command=function_args.get("sql_command")  
                )                
                
            # Step 4: send the info on the function call and function response to GPT
            messages.append(response_message)  # extend conversation with assistant's reply
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response
                })
            
            # Extend conversation with function response
            second_response = openai.ChatCompletion.create(
                temperature=0.0,
                model="gpt-3.5-turbo-16k-0613",
                messages=messages
            )  # Get a new response from GPT where it can see the function response
            
            # Load existing messages from the file
            with open("messages.json", "r") as f:
                messages = json.load(f)
            
            # Append the new assistant message to the messages list
            assistant_response = {
                "role": "assistant",
                "content": second_response["choices"][0]["message"]["content"]
            }       
            messages.append(assistant_response)
            
            # Save the updated messages list back to the file
            with open("messages.json", "w") as f:
                f.write(json.dumps(messages, indent=4))
            
            # Send the response back to the user
            context.bot.send_message(chat_id=user_id, text=second_response["choices"][0]["message"]["content"], parse_mode="Markdown")

        # No function was called
        else:
            # Save the regular message to the messages.json
            response_message = {
                "role": "assistant",
                "content": response_message["content"]
            }
            
            # Load existing messages from the file
            with open("messages.json", "r") as f:
                messages = json.load(f)
        
            # Append the new assistant message to the messages list
            messages.append(response_message)
            
            # Save the updated messages list back to the file
            with open("messages.json", "w") as f:
                f.write(json.dumps(messages, indent=4))

            # Send the response back to the user
            context.bot.send_message(chat_id=user_id, text=response_message["content"], parse_mode="Markdown")
