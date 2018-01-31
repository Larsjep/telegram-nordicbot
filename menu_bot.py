#!/usr/bin/python2
# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime

import requests

from bs4 import BeautifulSoup
from googletrans import Translator
from telegram.ext import CommandHandler, Updater

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

WEEK_MENU_URL = ("http://www.nordiccatering.dk/frokostordning/ugens-frokostmenu.aspx")
WEEK_DAYS = ["mandag", "tirsdag", "onsdag", "torsdag", "fredag"]


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
            for day in WEEK_DAYS:
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
    menu_response = requests.get(WEEK_MENU_URL)
    if menu_response.status_code == 200:
        menu_html = menu_response.text
        soup = BeautifulSoup(menu_html, "html.parser")
        return find_menu_in_text(soup.get_text())
    log.error("Failed to get menu. HTTP errorcode {}".format(menu_response.status_code))


def today_menu(weekday):
    menus = get_menus()
    if weekday < len(WEEK_DAYS):
        day_name = WEEK_DAYS[weekday]
        if day_name in menus:
            return menus[day_name]

    return [u"Desværre, ingen menu fundet"]


def translate(header, menu, language):
    translator = Translator()
    indentations = [len(s) - len(s.lstrip("\t")) for s in menu]
    translated_header, translated_menu = translator.translate([header, menu], src="da", dest=language)
    header = translated_header.text
    menu = ["\t" * x[0] + x[1].text for x in zip(indentations, translated_menu)]
    return header, menu


def allergies_to_emoji(menu_items):
    def do_replace(text):
        return text.replace(u"(L)", u"🥛")  \
                   .replace(u"(G)", u"🍞")  \
                   .replace(u"(N)", u"🥜")
    return [do_replace(t) for t in menu_items]


def bot_menu(bot, update):
    arguments = update.message.text.split(" ")
    if len(arguments) > 2:
        bot.send_message(chat_id=update.message.chat_id, text=u"Invalid kommando")
        return
    translate_to = None
    if len(arguments) > 1:
        translate_to = arguments[1]

    header = "Dagens menu"
    weekday = datetime.today().weekday()
    if datetime.today().hour >= 13:
        weekday += 1
        header = "Morgendagens menu"
    menu = today_menu(weekday)
    if translate_to:
        try:
            header, menu = translate(header, menu, translate_to)
        except ValueError:
            bot.send_message(chat_id=update.message.chat_id, text=u"Ukendt sprog. Brug ISO639-1 landekode")
            return
    bot.send_message(chat_id=update.message.chat_id, text=u"{}:\t\n{}".format(header, "\t\n".join(allergies_to_emoji(menu))))


def error_handler(bot, update, telegram_error):
    print("An error occured: {}".format(telegram_error))


def start(bot, update):
    user = update.message.from_user.username
    bot.send_message(chat_id=update.message.chat_id,
                     text="Hej @{0}, Jeg er Nordic Catering Bot\n"
                          "Brug /menu kommandoen for at se dagens menu\n"
                          "Brug /menu <lang> for dages menu på sproget <lang>".format(user))


if __name__ == "__main__":
    bot_token = os.environ['BOT_TOKEN']
    updater = Updater(token=bot_token)

    updater.dispatcher.add_handler(CommandHandler("menu", bot_menu))
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()
