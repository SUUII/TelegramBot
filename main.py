from telegram.ext.updater import Updater
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.filters import Filters
from telegram import ReplyKeyboardMarkup, bot, KeyboardButton, ReplyKeyboardRemove
import requests
import json
import pandas as pd
import datetime
from config import URL, BOT_TOKEN

updater = Updater(BOT_TOKEN, use_context=True)

def start(update: Update, context: CallbackContext):
    print("asdsadass")
    reply_markup = ReplyKeyboardMarkup(
        [
            [
                KeyboardButton('/register'),
                KeyboardButton('/cek_saldo'),
                KeyboardButton('/topup'),
                KeyboardButton('/roll')
            ]
        ]
    )
    # update.message.bot.send_document(update.message.chat.id, open("./position.json", "rb"))
    update.message.reply_text("Silahkan pilih menu", reply_markup=reply_markup)

def get_history(update: Update, context: CallbackContext):
    query = {
        "URL": URL,
        "client_id": update.message.text.split(' ')[1],
        "db": update.message.text.split(' ')[2]
    }
    queryResponse = requests.get("{URL}get_history/{client_id}/{db}".format(**query))
    result = queryResponse.json()
    print(result)
    if result["status_code"] == "0000":
        query_history = result.get("history", [])
        df = pd.DataFrame(query_history)
        current_time = datetime.datetime.now()
        filename = 'output_{client_id}_{db}_{time}.xlsx'.format(client_id=update.message.text.split(' ')[1], db=update.message.text.split(' ')[2], time=current_time.strftime("%d_%m_%Y_%H_%M_%S"), date=current_time.strftime("%d_%m_%Y"))
        file_path = 'reporting/{db}/{client_id}/{date}/'.format(client_id=update.message.text.split(' ')[1], db=update.message.text.split(' ')[2], date=current_time.strftime("%d_%m_%Y"))
        import os
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        writer = pd.ExcelWriter(file_path+filename)
        # write dataframe to excel sheet named 'marks'
        df.to_excel(writer, 'marks')
        # save the excel file
        writer.save()
        update.message.bot.send_document(update.message.chat.id, open("./"+file_path+filename, "rb"))
    else:
        update.message.reply_text(result["reason"], reply_markup=ReplyKeyboardRemove())

def contact_callback(update: Update, context: CallbackContext):
    print(update)

updater.dispatcher.add_handler(CommandHandler(['start', 'help'], start))
updater.dispatcher.add_handler(CommandHandler('get_history', get_history))
updater.dispatcher.add_handler(MessageHandler(Filters.contact, contact_callback))
updater.dispatcher.add_handler(MessageHandler(Filters.text, start))

updater.start_polling()
