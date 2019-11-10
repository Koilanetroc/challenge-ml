import telebot

bot = telebot.TeleBot('840902315:AAG5TfF4N-ObmfZ4KlNCYJem3dbzN329L6g')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Лол, ты написал мне /start')

bot.polling()
