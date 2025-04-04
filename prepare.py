# Import Libraries
import re
import numpy as np
import pandas as pd
from emoji import demojize,emojize

# Helper Functions
def separate_chat(chat):
    matches = list(re.finditer(r'\[?\s*\d{2}/\d{2}/\d{4},\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)\s*\]?', chat))
    messages = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(chat)
        message = chat[start:end].strip()
        messages.append(message)
    return messages
    
def get_datetime(message):
    datetime_match = re.findall(r'(\d{2}/\d{2}/\d{4}),\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)', message)
    return datetime_match[0] if datetime_match else ""

def get_sender(message):
    datetime_sub = re.sub(r'\[?\s*\d{2}/\d{2}/\d{4},\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)\s*\]?',"",message)
    get_name = re.sub(r"^[^a-zA-Z0-9]*", "", datetime_sub)
    sender_match = re.findall(r'(.*?)\:',get_name)
    return sender_match[0].strip() if sender_match else ""

def get_message(message):
    datetime_sub = re.sub(r'\[?\s*\d{2}/\d{2}/\d{4},\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)\s*\]?', "", message)
    return demojize(datetime_sub[datetime_sub.index(":")+1:].strip()) if ":" in datetime_sub else ""

def prepare_dict(chat):
    chat = separate_chat(chat)
    dates , senders , messages = [] , [] , []
    for message in chat:
        dates.append(get_datetime(message))
        senders.append(get_sender(message))
        messages.append(get_message(message))
    return {"date":dates, "sender":senders, "message":messages}

def prepare_message(message):
    message = message.replace("\u200e","")
    message = message.replace("\n","")
    return emojize(message)

def filter_message(message):
    filters = ["omitted","<attached:","added", "This message was deleted",
    "pinned a message","You deleted this message", 
    "Missed group", "Missed voice call", "Missed video call", 
    "Messages and calls are end-to-end encrypted.","changed their phone number",
    "an admin","changed the group name","the group description","changed the settings","this group's","null",
    "You added"]
    return not any(filter in message for filter in filters)

def handle_mentions(message):
    message = re.sub(r'@\d+', "@mention", message)
    if not re.match(r"^(@mention\s*)+$", message.strip()):
        return message

def handle_edits(message):
    return message.replace("<This message was edited>","")

def get_questions(chat):
    questions = []
    for _,message in chat.iterrows():
        questions.append([message["date"],message["sender"],emojize(message["message"])])
    return questions

# Main Game
def game(chat_file):
    chat = chat_file.read().decode("utf-8")
    chat = pd.DataFrame(prepare_dict(chat))

    chat.replace("", np.nan, inplace=True)
    chat = chat[(chat["message"].notnull()) & (chat["date"].notnull()) & (chat["sender"].notnull())].reset_index(drop=True)

    chat["message"] = chat["message"].apply(prepare_message)

    chat = chat[chat["message"].apply(filter_message)]
    chat["message"] = chat["message"].apply(handle_edits)
    chat["message"] = chat["message"].apply(handle_mentions)

    chat = chat[(chat["message"].notnull())].reset_index(drop=True)

    questions = get_questions(chat)
    options = list(chat["sender"].unique())

    return questions,options