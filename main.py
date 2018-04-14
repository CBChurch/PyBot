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
import src.arb as arb
import socket
from src.dbhelper import DBHelper

init.initialise_project()

global updates, chat_id

config = ConfigParser.ConfigParser()
config.read("./config/cred.config")
token = config.get("configuration","RaspPy")
base_chat_id = config.get("configuration","base_chat_id")

URL = "https://api.telegram.org/bot{}/".format(token)

MachineName = socket.gethostname()
if MachineName == 'raspberrypi':
    RaspPi = True
    db_directory = '~/mnt/FLASH/db/'
else:
    RaspPi = False
    db_directory = 'data/'

db = DBHelper("PyBot_DB.sqlite",db_directory)

def main():
    last_update_id = None
    start_time = datetime.datetime.now()
    RunBot = True
    morningMessage = False

    db.setup()

    print("Listening...")
    while RunBot:
        updates = src_bot.get_updates(URL, last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = src_bot.get_last_update_id(updates) + 1

        tdiff = datetime.datetime.now() - start_time
        RunBot = src_bot.bot_responses(updates, URL, token)
        start_time = src_bot.check_arb(tdiff, start_time, base_chat_id, URL, db)
        morningMessage = src_bot.good_morning(morningMessage, base_chat_id, URL)

        time.sleep(3)


if __name__ == '__main__':
    main()

