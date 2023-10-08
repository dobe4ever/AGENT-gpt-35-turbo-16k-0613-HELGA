functions = [ 
    {
        "name": "read_file",
        "description": "Read the content of a file given the file path.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path of the file to be read."
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "perform_google_search",
        "description": "Performs a Google search based on a given query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "write_file",
        "description": "Writes content to a file",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Filename to write to"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to file"
                }
            },
            "required": ["filename", "content"]
        }
    },
    {
        "name": "add_bookmark",
        "description": "Add a new bookmark to the list of bookmarks",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the bookmark to add"
                },
                "name": {
                    "type": "string",
                    "description": "The name of the bookmark to add"
                },
                "folder": {
                    "type": "string",
                    "description": "The folder in which to add the bookmark"
                }
            },
            "required": ["url", "name", "folder"]
        }
    },
    {
        "name": "send_poll",
        "description": "Sends weekly poll to Helga's Telegram group. Only call this function if you are asked specifically to do so!",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question or prompt of the poll."
                },
                "options": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of poll options."
                }
            },
            "required": ["question", "options"]
        }
    }, 
    {
        "name": "manage_users_table",
        "description": "Manage users table by executing SQL commands on the 'users' table.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql_command": {
                    "type": "string",
                    "description": "Columns: user_id, username, public_name, signup_date, membership_plan, expiration_date, active. Date format: YYYY-MM-DD. Tip: use timestamp of user's message to determine the current date."
                }
            },
            "required": ["sql_command"]
        }
    },
    {
        "name": "manage_reminders_table",
        "description": "Manage reminders by executing sql commands on the 'reminders' table.",
        "parameters": { 
            "type": "object",
            "properties": {
                "sql_command": {
                    "type": "string",
                    "description": "Columns: 'id', 'datetime' (YYYY-MM-DD HH:MI), 'task'. Use timestamp of user's message to determine the current date if needed."
                }
            },
            "required": ["sql_command"]
        }
    }    
]
