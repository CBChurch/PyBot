#Import libraries
import ConfigParser
import time
import src.bot as src_bot
import src.init as init
import datetime
import socket
import logging
from src.dbhelper import DBHelper
import src.arb as src_arb
import datetime
import gc
import requests

#Initialise project
init.initialise_project()


MachineName = socket.gethostname()
if MachineName == 'raspberrypi':
    RaspPi = True
    db_directory = '/mnt/FLASH/db/'
    logging.basicConfig(filename='/mnt/FLASH/logs/PyBot_Internal.log', level=logging.DEBUG)
else:
    RaspPi = False
    db_directory = 'data/'
    logging.basicConfig(filename='PyBot.log', level=logging.DEBUG)
db = DBHelper("PyBot_DB.sqlite",db_directory)

#Collect configuration items
config = ConfigParser.ConfigParser()
config.read("./config/cred.config")
token = config.get("configuration","RaspPy")
base_chat_id = config.get("configuration","base_chat_id")

URL = "https://api.telegram.org/bot{}/".format(token)


#Define main program
def main():
    last_update_id = None
    start_time = datetime.datetime.now()
    RunBot = True
    morningMessage = False
    bot_session = requests.session()

    src_bot.check_arb(start_time-start_time, start_time, base_chat_id, URL, db, runNow=True, s = bot_session)

    db.setup()

    print("Listening...")
    try_count = 0
    triggerFlag = True
    while RunBot:
        try:
            updates = src_bot.get_updates(URL, s= bot_session, offset=last_update_id)
            if len(updates["result"]) > 0:
                last_update_id = src_bot.get_last_update_id(updates) + 1

            tdiff = datetime.datetime.now() - start_time
            RunBot, triggerFlag = src_bot.bot_responses(updates, URL, token, db, s = bot_session, triggerFlag = triggerFlag)
            start_time, triggerFlag = src_bot.check_arb(tdiff, start_time, base_chat_id, URL, db, s = bot_session, triggerFlag = triggerFlag)
            morningMessage = src_bot.good_morning(morningMessage, base_chat_id, URL, token, db, s = bot_session)
            gc.collect()
            try_count = 0
        except Exception as e:
            CT = datetime.datetime.now()
            logging.debug(str(CT)+ ' ' + str(e))
            try_count += 1
            #print updates
            print("Bot has failed {n} times".format(n=try_count))
            gc.collect()
            if try_count >= 100:
                src_bot.send_message("Bot failed 100 times in a row", chat_id=base_chat_id, URL=URL, s = bot_session)
                RunBot = False
            else:
                time.sleep(3*60)
        time.sleep(5)


#Run program
if __name__ == '__main__':
    main()

