import requests
import numpy as np
import datetime
import arb as src_arb
import json
import furl.furl as furl
import dateutil.parser as dt_parser
import gc
import contextlib
import urllib3

def handle_func(msg, bot, token):
    chat_id = msg['chat']['id']
    command = msg['text']
    print("Got command '{c}' from chat '{ch}'".format(c = command, ch = chat_id))

    if command == '/arb':
        bot.sendMessage(chat_id, str(np.round(src_arb.get_btc_arb()*100,3)))
    elif command == '/arbplot':
        src_arb.get_btc_arb(graph=True)
        sendImage(chat_id, 'images/ARB_BTC.png', token)
    pass

def sendImage(chat_id, image_path, token, s):
    url = "https://api.telegram.org/bot{t}/sendPhoto".format(t = token);
    files = {'photo': open(image_path, 'rb')}
    data = {'chat_id' : chat_id}
    with contextlib.closing(s) as sesh:
        sesh.post(url, files=files, data=data)
        sesh.close()
    pass

def get_url(url, s):
    with contextlib.closing(s) as sesh:
        with contextlib.closing(sesh.get(url, stream=False)) as r:
            content = str(r.content.decode("utf8"))
    gc.collect()
    return content

def get_json_from_url(url, s):
    content = get_url(url, s)
    js = json.loads(content)
    return js

def get_updates(URL, s, offset=None, to = 100):
    url = URL + "getUpdates?timeout={t}".format(t=to)
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url, s)
    return js

def send_message(text, chat_id, URL, s, reply_markup = None):
    text = furl(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url, s)
    pass

def echo_all(updates, URL, s):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat, URL, s)
        except Exception as e:
            print(e)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def bot_responses(updates, URL, token, db, s, triggerFlag):
    RunBot = True
    if len(updates["result"]) > 0:
        message_text = updates["result"][0]["message"]["text"]
        chat_id = updates["result"][0]["message"]["from"]["id"]
        print("Got command '{c}' from chat '{ch}'".format(c=message_text, ch=chat_id))
        if message_text == '/stop':
            RunBot = False
            updates["result"][0]["message"]["text"] = "Stopped"
            send_message("Shutting down bot...", chat_id, URL, s)
            print("Shutting down bot...")
            pass
        if message_text == '/resetTrigger':
            triggerFlag = True
            pass
        if message_text == '/arbplot':
            #arb.get_btc_arb(graph=True)
            sendImage(chat_id, 'images/ARB.png', token, s)
            pass
        if message_text == '/rarbplot':
            #arb.get_btc_arb(graph=True)
            sendImage(chat_id, 'images/REV_ARB.png', token, s)
            pass

        if message_text == '/plot24':
            src_arb.plt_last_24_hours(db)
            sendImage(chat_id, 'images/LAST_24.png', token, s)
            pass

        if message_text == '/checkdb':
            schema, db_vals = db.get_latest_arb()
            db_vals = db_vals[0]
            t = dt_parser.parse(db_vals[0])
            zarusd = db_vals[1]
            arb = np.max(db_vals[2:5]).round(5)*100
            revarb = np.max(db_vals[5:]).round(5)*100
            arbpos = np.argmax(db_vals[2:5])+2
            arb_prod = schema[arbpos][1]
            revarbpos = np.argmax(db_vals[5:]) + 5
            revarb_prod = schema[revarbpos][1]
            send_message("Current ARB opportunity is {a}% for {p}, with a rev arb opportunity of {r}% for {rp}. The current ZAR/USD exchange "
                  "is {e}. The data was recorded at {t} on {dt}.".format(a = arb, p = arb_prod, rp = revarb_prod, r = revarb, \
                                                                      e = zarusd, t = t.time().strftime('%H:%M'), dt = t.date()),\
                         chat_id, URL, s)
            pass
    return RunBot, triggerFlag

def check_arb(tdiff, start_time, base_chat_id, URL, db, s, bitstamp, luno, ice3x, triggerFlag = True, runNow = False):
    CT = datetime.datetime.now()
    if (tdiff.seconds > 60 or runNow):
        #arbval, zarusd, revarb = np.round(arb.get_btc_arb(), 5)
        vals = src_arb.get_crypto_arb(bitstamp, luno, ice3x, plt_rev_arb=True, plt_results=True)

        luno_btc_arb = vals[0]
        ice3x_btc_arb = vals[1]
        ice3x_ltc_arb= vals[2]
        luno_btc_revarb = vals[3]
        ice3x_btc_revarb = vals[4]
        ice3x_ltc_revarb = vals[5]
        zarusd = vals[6]
        arbval = np.max([luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb])
        revarb = np.max([luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb])
        print("{t} - Checking ARB, current val: {a}%. Reverse arb: {r}%".format(t = CT.strftime('%Y-%m-%d %H:%M'), a = arbval*100, r = revarb*100))
        if arbval*100 >= 5.00 and triggerFlag:
            print("ARB is greater than 5%")
            send_message("ARB is greater than 5%, current arb is {a}%".format(a=arbval), base_chat_id, URL, s)
            triggerFlag = False
        if revarb*100 >= 5.00  and triggerFlag:
            print("Reverse ARB is greater than 5%")
            send_message("Reverse ARB is greater than 5%, current arb is {a}%".format(a=revarb), base_chat_id, URL, s)
            triggerFlag = False
        start_time = datetime.datetime.now()
        db.add_arb(start_time, zarusd, luno_btc_arb, ice3x_btc_arb, ice3x_ltc_arb, luno_btc_revarb, ice3x_btc_revarb, ice3x_ltc_revarb)

    return start_time, triggerFlag

def good_morning(morning_message, base_chat_id, URL, token, db, s):
    CT = datetime.datetime.now()
    MorningTime = CT.replace(hour=7, minute=30, second=0)
    if morning_message == False and CT >= MorningTime:

        schema, db_vals = db.get_latest_arb()
        db_vals = db_vals[0]
        t = dt_parser.parse(db_vals[0])
        zarusd = db_vals[1]
        arb = np.max(db_vals[2:5]).round(5) * 100
        revarb = np.max(db_vals[5:]).round(5) * 100
        arbpos = np.argmax(db_vals[2:5]) + 2
        arb_prod = schema[arbpos][1]
        revarbpos = np.argmax(db_vals[5:]) + 5
        revarb_prod = schema[revarbpos][1]

        send_message("Good morning Chris, the current arb is: {a}% for {p}. The reverse arb is: {r}% for {rp}."
                     "The current ZAR/USD FX rate is {fx}. The data was stored into the DB at {t} on {dt}."
                     .format(a=arb, p = arb_prod, r = revarb, rp = revarb_prod, fx=zarusd,
                             t=t.time().strftime('%H:%M'), dt=t.date()), base_chat_id, URL, s)
        if arb > 0:
            sendImage(base_chat_id, 'images/ARB.png', token, s)
        if revarb > 0:
            sendImage(base_chat_id, 'images/REV_ARB.png', token, s)
        print("It is later than {mt} and we have sent the morning message.".format(mt=MorningTime.strftime("%Hh%M")))
        morning_message = True
    if CT <= MorningTime and morning_message == True:
        morning_message = False
        print('Reset morning message flag')
    return morning_message

def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)