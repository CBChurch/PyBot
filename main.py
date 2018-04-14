import sys
import ConfigParser
import time
from telepot.loop import MessageLoop
import telepot
import src.bot as src_bot
import src.init as init
import datetime
import thread
import numpy as np
import requests
import urllib
import src.arb as arb

init.initialise_project()

config = ConfigParser.ConfigParser()
config.read("./config/cred.config")
token = config.get("configuration","RaspPy")
URL = "https://api.telegram.org/bot{}/".format(token)
base_chat_id = '419194191'


def main():
    last_update_id = None
    start_time = datetime.datetime.now()
    print("Listening...")
    RunBot = True
    while RunBot:
        updates = src_bot.get_updates(URL, last_update_id)
        if len(updates["result"]) > 0:
            message_text = updates["result"][0]["message"]["text"]
            chat_id = updates["result"][0]["message"]["from"]["id"]
            if message_text == '/stop':
                RunBot = False
                print("Shutting down bot...")
                pass
            if message_text == '/arb':
                arb_val = arb.get_btc_arb()
                src_bot.send_message(arb_val, chat_id, URL)
                pass
            if message_text == '/arbplot':
                arb.get_btc_arb(graph=True)
                src_bot.sendImage(chat_id, 'images/ARB_BTC.png',token)

            last_update_id = src_bot.get_last_update_id(updates) + 1
            # src_bot.echo_all(updates, URL)
        timediff = datetime.datetime.now()-start_time
        print(timediff.seconds)
        print("hello world")
        time.sleep(3)


if __name__ == '__main__':
    main()