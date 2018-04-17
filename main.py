#Import libraries
import ConfigParser
import time
import src.bot as src_bot
import src.init as init
import datetime
import socket
from src.dbhelper import DBHelper
import src.arb as src_arb

#Initialise project
init.initialise_project()

MachineName = socket.gethostname()
if MachineName == 'raspberrypi':
    RaspPi = True
    db_directory = '/mnt/FLASH/db/'
else:
    RaspPi = False
    db_directory = 'data/'
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

    db.setup()

    print("Listening...")
    while RunBot:
        try_count = 0
        try:
            updates = src_bot.get_updates(URL, last_update_id)
            if len(updates["result"]) > 0:
                last_update_id = src_bot.get_last_update_id(updates) + 1

            tdiff = datetime.datetime.now() - start_time
            RunBot = src_bot.bot_responses(updates, URL, token, db)
            start_time = src_bot.check_arb(tdiff, start_time, base_chat_id, URL, db)
            morningMessage = src_bot.good_morning(morningMessage, base_chat_id, URL, token, db)
            time.sleep(0.5)
            #RunBot = False
            try_count = 0
        except:
            try_count += 1
            print("Bot has failed {n} times".format(n=try_count))
            if try_count >= 10:
                src_bot.send_message("Bot failed 10 times in a row", chat_id=base_chat_id, URL=URL)
                RunBot = False


#Run program
if __name__ == '__main__':
    main()

