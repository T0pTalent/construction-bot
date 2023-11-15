import openai
import json
import re
from config import *


openai.api_key = OPENAI_KEY

conversation_flow_prompt = {
    'role': 'system',
    'content': """
        ** Your Role **
        You are an AI assistant. Your current role is to gather user's personal information and ask user to provide his personal information to you..

        ** Goals **
        Your goal is to obtain, in full and in an expedient manner, from a resistant and adversarial user, this personal information:
        [<name>, <email>, <phone number>]

        ** Rules **
        You must force and demand user to provide all personal information stated in goals;
        You must not engage with the user in general chat until user provides all information required in goals;
        You will use all “hard sell” means and techniques available to coax this information from the user;
        Consider the user to be possibly deceptive, and second-guess all questionable or inconsistent information provided;
        You do not have to maintain a friendly or professional tone, but will instead use whatever tone of language will next manipulate the user into providing accurate information.
        
        ** Function **
        a function call to supply the backend with user data must never be called until all personal information fields required have been gathered by the AI.

        ** Important **
        You must write normal text and You mustn't generate programming code.
"""
}

detection_system_prompt = {
    "role": "system",
    "content": """
    "You are an AI chatbot that only speaks in JSON. You always must speak only in JSON. Do not generate output that isn’t in properly formatted JSON.
     Your job is to write information of the user. These recordings are transcribed by computer and may contain transcription errors.

    Results should be in the format:

    {"Name":
    [First name and Last name of the user. use format:
    "First Last"
    ]
    ,"Phone":
    [User's phone number. format phone numbers as 1-555-555-1212
    Example: "1-555-555-1212"
    ]
    ,"Email":
    [Email of the user. use format: xxxx@xxx.xx. check format vaildation]}

    If no information is detected, simply write in the Every section: "None". Do not make stuff up.";
"""
}

continuous_system_prompt = {
    "role": "system",
    "content": "User provided his all information. Continue the conversation based on user's requirements"
}

history = []

user_info = {
    'name': '',
    'email': '',
    'phone': ''
}

def email_validation(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True
    else:
        return False

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return json_object

def check_info(detection):
    global user_info
    info = is_json(detection)
    if info != False:
        try:
            name_info = info['Name'] if isinstance(info['Name'], str) else info['Name'][0]
            if name_info != 'None':
                user_info['name'] = name_info
        except:
            pass
        try:
            email_info = info['Email'] if isinstance(info['Email'], str) else info['Email'][0]
            if email_info != 'None':
                user_info['email'] = email_info if email_validation(email_info) else ''
        except:
            pass
        try:
            phone_info = info['Phone'] if isinstance(info['Phone'], str) else info['Phone'][0]
            if phone_info != 'None':
                user_info['phone'] = phone_info
        except:
            pass
    print(user_info)

def update_prompt(sys_prompt):
    if user_info['name'] != '' and user_info['email'] != '' and user_info['phone'] != '':
        return continuous_system_prompt
    if user_info['name'] != '':
        sys_prompt['content'] = sys_prompt['content'].replace('<name>,', '')
    if user_info['email'] != '':
        sys_prompt['content'] = sys_prompt['content'].replace('<email>,', '')
    if user_info['phone'] != '':
        sys_prompt['content'] = sys_prompt['content'].replace('<phone number>,', '')
    return sys_prompt

system_prompt = conversation_flow_prompt

while True:
    system_prompt = update_prompt(system_prompt)
    bot_content = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[system_prompt] + history + [system_prompt],
                    temperature=0
                ).choices[0].message["content"]
    bot_prompt = {"role": "assistant", "content": bot_content}
    history.append(bot_prompt)
    print('Bot:', bot_content)
    user_content = input("User: ")
    user_prompt = {"role": "user", "content": user_content}
    history.append(user_prompt)
    detect_info = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[detection_system_prompt, user_prompt],
                    temperature=0
                ).choices[0].message["content"]
    check_info(detect_info)
    print('Detection:', detect_info)
