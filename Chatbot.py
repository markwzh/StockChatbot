# Import necessary modules
import re
import random
from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer
from rasa_nlu import config
from iexfinance.stocks import Stock
from iexfinance.stocks import get_historical_data
from iexfinance.stocks import get_historical_intraday
from datetime import datetime
from wxpy import *

# Create a trainer that uses this config
trainer = Trainer(config.load("config_spacy.yml"))

# Load the training data
training_data = load_data('demo-rasa.json')

# Create an interpreter by training the model
interpreter = trainer.train(training_data)

INIT=0
CHOOSE_COMPANY=1
CHOOSE_FUNCTION = 2

policy_rules = {
	(INIT, "greet"): (INIT, "Hello! I am a robot to get information about stock price. What do you want to know?"),
    (INIT, "goodbye"): (INIT, "Byebye, have a nice one!"),
    (INIT, "others"): (INIT, "Sorry, I don't understand what you jsut said."),
    (INIT, "ask_function"): (INIT, "I have three functions now:\n 1. Check the current stock price of a company.\n 2. Check the stock price of a company within a priod of time.\n 3. Check the open stock price of a company."),
    (INIT, "choose_company"): (CHOOSE_COMPANY, "Ok, which stock price do you want to know?"),
    (INIT, "get_historical_price"): (CHOOSE_FUNCTION, "Wait a second..."),
    (INIT, "get_open_price"): (CHOOSE_FUNCTION, "The data is loading..."),
    (INIT, "get_price"): (CHOOSE_FUNCTION, "Hold on for a second..."),
    (CHOOSE_COMPANY, "others"): (CHOOSE_COMPANY, "Sorry, I don't understand what you just said."),
    (CHOOSE_COMPANY, "get_price"): (CHOOSE_FUNCTION, "Please wait! The data is loading..."),
    (CHOOSE_COMPANY, "get_historical_price"): (CHOOSE_FUNCTION, "Wait a second..."),
    (CHOOSE_COMPANY, "get_open_price"): (CHOOSE_FUNCTION, "The data is loading..."),
    (CHOOSE_COMPANY, "ask_function"): (CHOOSE_COMPANY, "I have three functions now:\n 1. Check the current stock price of a company.\n 2. Check the stock price of a company within a priod of time.\n 3. Check the open stock price of a company."),
    (CHOOSE_COMPANY, "greet"): (CHOOSE_COMPANY, "Hello! I am a robot helping you to check the stock price! What do you want to know?"),
    (CHOOSE_COMPANY, "goodbye"): (INIT, "Byebye!"),
    (CHOOSE_FUNCTION, "choose_company"): (CHOOSE_COMPANY, "Ok, which stock price do you want to check?"),
    (CHOOSE_FUNCTION, "others"): (CHOOSE_FUNCTION, "Sorry, I don't understand what you just said."),
    (CHOOSE_FUNCTION, "goodbye"): (INIT, "See you next time!"),
    (CHOOSE_FUNCTION, "get_historical_price"): (INIT, "The data is loading..."),
    (CHOOSE_FUNCTION, "get_open_price"): (CHOOSE_FUNCTION, "Hold on for a second."),
    (CHOOSE_FUNCTION, "get_price"): (CHOOSE_FUNCTION, "One second."),
    (CHOOSE_FUNCTION, "greet"): (INIT, "Hello! I am a robot to help you know the stock price! What do you want to know")
}



def match_rule(rules, message):
    for pattern, responses in rules.items():
        match = re.search(pattern, message)
        if match is not None:
            response = random.choice(responses)
            var = match.group(1) if '{0}' in response else None
            return response, var
    return "default", None

# Define chitchat_response()
def chitchat_response(message):
    # Call match_rule()
    response, phrase = match_rule(rules, message)
    # Return none is response is "default"
    if response == "default":
        return None
    if '{0}' in response:
        # Replace the pronouns of phrase
        phrase = replace_pronouns(phrase)
        # Calculate the response
        response = response.format(phrase)
    return response

rules = {'if (.*)': ["Do you really think it's likely that {0}",
		'Do you wish that {0}', 'What do you think about {0}', 'Really--if {0}'],
		'do you think (.*)': ['if {0}? Absolutely.', 'No chance'],
		'I want (.*)': ['What would it mean if you got {0}', 'Why do you want {0}', "What's stopping you from getting {0}"],
		'do you remember (.*)': ['Did you think I would forget {0}',
		"Why haven't you been able to forget {0}", 'What about {0}', 'Yes .. and?']}

def replace_pronouns(message):

    message = message.lower()
    if 'me' in message:
        return re.sub('me', 'you', message)
    if 'i' in message:
        return re.sub('i', 'you', message)
    elif 'my' in message:
        return re.sub('my', 'your', message)
    elif 'your' in message:
        return re.sub('your', 'my', message)
    elif 'you' in message:
        return re.sub('you', 'me', message)

    return message

# Define send_message()
def send_message(state, pending, message):
    print("USER : {}".format(message))
    response = chitchat_response(message)
    if response is not None:
        print("BOT : {}".format(response))
        myfriend.send(response)
        return state, None

    # Calculate the new_state, response, and pending_state
    new_state, response, pending_state = policy_rules[(state, interpret(message))]
    print("BOT : {}".format(response))
    if pending is not None:
        new_state, response, pending_state = policy_rules[pending]
        print("BOT : {}".format(response))
    if pending_state is not None:
        pending = (pending_state, interpret(message))
    myfriend.send(response)
    return new_state, pending

# Define respond()
def respond(message, params, suggestions, excluded):
    # Interpret the message
    parse_data = interpret(message)
    # Extract the intent
    intent = parse_data["intent"]["name"]
    # Extract the entities
    entities = parse_data["entities"]
    # Fill the dictionary with entities
    for ent in entities:
        params[ent["entity"]] = str(ent["value"])
    # Find matching response
    (re_state, response) = policy_rules(state, intent)
    if new_state == 1:
        for ent in params:
            if ent == "company":
                company = str(params[ent])
    if new_state == 2:
        if intent == "get_price":
            for ent in params:
                if ent == "company":
                    company = str(params[ent])
            stock = Stock(company)
            response = "The current stock price of "+ company +" is " + str(stock.get_price())
        if intent == "get_historical_price":
            for ent in params:
                if ent == "company":
                    company = str(params[ent])
                if ent == "start_date":
                    startdate = str(params[ent])
                    startd = startdate.split('.')
                    start = datetime(int(startd[0]), int(startd[1]), int(startd[2]))
                if ent == "end_date":
                    enddate = str(params[ent])
                    endd = enddate.split('.')
                    end = datetime(int(endd[0]), int(endd[1]), int(endd[2]))
        if intent == "get_open_price":
            for ent in params:
                if ent == "company":
                    company = str(params[ent])
            stock = Stock(company)
            response = "The open price of " + company + " is " + str(stock.get_open())

    return re_state, response, params

# Initialize the empty dictionary and lists
params, suggestions, excluded = {}, [], []

# Define send_messages()
def send_messages(messages):
    state = INIT
    pending = None
    for msg in messages:
        state, pending = send_message(state, pending, msg)


bot = Bot()
myfriend = bot.friends().search('Mono', sex = MALE)[0]
myfriend.send('Hi! How are you?')
@bot.register(myfriend)

def reply_myfriend(msg):
    global state, params
    state, params = send_message(state, msg.text, params)
    return None
