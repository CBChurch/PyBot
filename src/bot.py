import requests
import numpy as np
import datetime
import arb
import json
import urllib

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


def get_updates(URL, offset=None):
    url = URL + "getUpdates?timeout=20"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1

    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]

    return (text, chat_id)


def send_message(text, chat_id, URL):
    #text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def get_chat_id(token):
    url = "https://api.telegram.org/bot{}/".format(token) + "getUpdates"
    response = requests.get(url)
    content = response.content.decode("utf8")
    print(content)
    updates = json.loads(content)
    print(updates)
    num_updates = len(updates["result"])
    last_update = num_updates

    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return chat_id

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
