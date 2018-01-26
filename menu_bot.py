#!/usr/bin/python2
from datetime import datetime
import logging
import os

from bs4 import BeautifulSoup
import requests
from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

bot_token = os.environ['BOT_TOKEN']
updater = Updater(token=bot_token)

week_menu_url = 'http://www.nordiccatering.dk/frokostordning/ugens-frokostmenu.aspx'
week_days = ['mandag', 'tirsdag', 'onsdag', 'torsdag', 'fredag']


def find_menu_in_text(text):
    current_day = ""
    menu_lines = []
    menus = {}
    for line in text.splitlines():
        found_day = False
        if "Der tages forbehold" in line:
            menus[current_day] = menu_lines
            return menus
        elif ":" in line:
            for day in week_days:
                if day in line.lower() or "Der tages forbehold" in line:
                    if current_day:
                        menus[current_day] = menu_lines
                    current_day = day
                    menu_lines = []
                    found_day = True
        if found_day:
            continue
        if current_day:
            if len(line) > 2:
                menu_lines.append(line.rstrip())
    return menus


def get_menus():
    menu_response = requests.get(week_menu_url)
    if menu_response.status_code == 200:
        menu_html = menu_response.text
        soup = BeautifulSoup(menu_html, 'html.parser')
        return find_menu_in_text(soup.get_text())
    log.error("Failed to get menu. HTTP errorcode {}".format(menu_response.status_code))


def today_menu(weekday):
    menus = get_menus()
    if weekday < len(week_days):
        day_name = week_days[weekday]
        if day_name in menus:
            return menus[day_name]

    return [u"Desvaerre, ingen menu fundet"]


def bot_menu(bot, update):
    header = "Dagens menu"
    weekday = datetime.today().weekday()
    if datetime.today().hour >= 13:
        weekday += 1
        header = "Morgendagens menu"
    menu = today_menu(weekday)
    bot.send_message(chat_id=update.message.chat_id, text=u"{}:\t\n{}".format(header, "\t\n".join(menu)))


def error_handler(bot, update, telegram_error):
    print "An error occured: {}".format(telegram_error)


def start(bot, update):
    user = update.message.from_user.username
    bot.send_message(chat_id=update.message.chat_id,
                     text="Hej @{0}, Jeg er Nordic Catering Bot\nBrug /menu kommandoen for at se dagens menu".format(user))

updater.dispatcher.add_handler(CommandHandler('menu', bot_menu))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_error_handler(error_handler)

updater.start_polling()
updater.idle()
