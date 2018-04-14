import requests
import numpy as np
import datetime
import arb
import json
import furl.furl as furl

def handle_func(msg, bot, token):
    chat_id = msg['chat']['id']
    command = msg['text']
    print(chat_id)
    print 'Got command: %s' % command

    if command == '/arb':
        bot.sendMessage(chat_id, str(np.round(arb.get_btc_arb()*100,3)))
    elif command == '/arbplot':
        arb.get_btc_arb(graph=True)
        sendImage(chat_id, 'images/ARB_BTC.png', token)
    pass

def sendImage(chat_id, image_path, token):
    url = "https://api.telegram.org/bot{t}/sendPhoto".format(t = token);
    files = {'photo': open(image_path, 'rb')}
    data = {'chat_id' : chat_id}
    r= requests.post(url, files=files, data=data)
    print(r.status_code, r.reason, r.content)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(URL, offset=None, to = 60):
    url = URL + "getUpdates?timeout={}".format(to)
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def send_message(text, chat_id, URL):
    text = furl(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def echo_all(updates, URL):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat, URL)
        except Exception as e:
            print(e)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def bot_responses(updates, URL, token):
    RunBot = True
    if len(updates["result"]) > 0:
        message_text = updates["result"][0]["message"]["text"]
        chat_id = updates["result"][0]["message"]["from"]["id"]
        print 'Got command: %s' % message_text
        if message_text == '/stop':
            RunBot = False
            updates["result"][0]["message"]["text"] = "Stopped"
            send_message("Shutting down bot...", chat_id, URL)
            print("Shutting down bot...")
            pass
        if message_text == '/arb':
            arbval, zarusd = arb.get_btc_arb()
            arbval = np.round(arbval, 5) * 100
            send_message("Current arb is {a}%".format(a=arbval), chat_id, URL)
            pass
        if message_text == '/arbplot':
            arb.get_btc_arb(graph=True)
            sendImage(chat_id, 'images/ARB_BTC.png', token)
            pass
    return RunBot

def check_arb(tdiff, start_time, base_chat_id, URL, db):
    CT = datetime.datetime.now()
    if (tdiff.seconds > 60):
        arbval, zarusd = np.round(arb.get_btc_arb(), 5)
        print("Checking ARB, current val: {}%".format(arbval*100))
        if arbval*100 >= 5.00:
            print("ARB is greater than 5%")
            send_message("ARB is greater than 5%, current arb is {a}%".format(a=arbval), base_chat_id, URL)
        start_time = datetime.datetime.now()
        db.add_arb(start_time, arbval, zarusd)


    return start_time

def good_morning(morning_message, base_chat_id, URL):
    CT = datetime.datetime.now()
    MorningTime = CT.replace(hour=7, minute=30, second=0)
    if morning_message == False and CT >= MorningTime:
        arbval, zarusd = np.round(arb.get_btc_arb(), 5)
        send_message("Good morning Chris", base_chat_id, URL)
        send_message("Current arb is {a}%".format(a=arbval*100), base_chat_id, URL)
        send_message("Current ZAR/USD FX rate is {a}".format(a=zarusd), base_chat_id, URL)
        print("It is later than 7h30 and we have sent the morning message")
        morning_message = True
    if CT <= MorningTime:
        morning_message = False
    return morning_message

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)