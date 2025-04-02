# Import Libraries
import re
import numpy as np
import pandas as pd
from emoji import demojize,emojize

# Define Helper Functions
def separate_chat(chat):
    chat = chat.split("[")
    return [f"[{message}" for message in chat if message]

def get_date(message):
    date_match = re.findall(r'\[\d{2}/\d{2}/\d{4}', message)
    return date_match[0][1:] if date_match else ""

def get_sender(message):
    sender_match = re.findall(r'\](.*?)\:',message)
    return sender_match[0].strip() if sender_match else ""

def get_message(message):
    message = re.sub(r'\[.*?\]','',message)
    return demojize(message[message.index(":")+1:].strip()) if ":" in message else ""

def prepare_dict(chat):
    chat = separate_chat(chat)
    dates , senders , messages = [] , [] , []
    for message in chat:
        dates.append(get_date(message))
        senders.append(get_sender(message))
        messages.append(get_message(message))
    return {"date":dates, "sender":senders, "message":messages}

def prepare_message(message):
    message = message.replace("\u200e","")
    message = message.replace("\n","")
    return emojize(message)

def filter_message(message):
    filters = [ "omitted","<attached:","added", "This message was deleted.",
    "pinned a message","You deleted this message.", "left", 
    "Missed group", "Missed voice call", "Missed video call", 
    "Messages and calls are end-to-end encrypted.","changed their phone number",
    "an admin","changed the group name","the group description","changed the settings","this group's"]
    return not any(filter in message for filter in filters)

def filter_senders(senders):
    filters = ["You"]
    return not any(filter in senders for filter in filters)

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


# Define Main Game
def game(chat_file):

    chat = chat_file.read().decode("utf-8")
    chat = pd.DataFrame(prepare_dict(chat))

    chat.replace("", np.nan, inplace=True)
    chat = chat[(chat["message"].notnull()) & (chat["date"].notnull()) & (chat["sender"].notnull())].reset_index(drop=True)

    chat["message"] = chat["message"].apply(prepare_message)

    chat = chat[chat["sender"].apply(filter_senders)]
    chat = chat[chat["message"].apply(filter_message)]

    chat["message"] = chat["message"].apply(handle_edits)
    chat["message"] = chat["message"].apply(handle_mentions)

    chat = chat[(chat["message"].notnull())].reset_index(drop=True)

    questions = get_questions(chat)
    options = list(chat["sender"].unique())

    return questions,options