import os
import telebot
import logging
import json
from io import BytesIO
import tensorflow as tf
from urllib.request import urlopen
from telebot import apihelper
from os.path import join, dirname
from dotenv import load_dotenv
from PIL import Image
import numpy as np

from keras.models import model_from_json


############ INITIALIZE ############
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROXY = {'http': f'http://{os.getenv("HTTP_PROXY")}'}
IMAGE_SIZE=(28, 28)
IMAGE_PREDICT_SIZE=(1, 28, 28, 1)

apihelper.proxy = PROXY

bot = telebot.TeleBot(BOT_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
############ INITIALIZE ############

############ LOAD MODEL ############
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()

model = model_from_json(loaded_model_json)

model.load_weights("model.h5")

print("Loaded model from disk")

global graph
graph = tf.get_default_graph()
############ LOAD MODEL ############

############ HELPERS ############
def get_file_path(file_id):
    response = urlopen(f'https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}')
    data = json.load(response)
    return data['result']['file_path']

def get_file(file_path):
    response = urlopen(f'https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}')
    img = np.array(Image.open(BytesIO(response.read())).resize(IMAGE_SIZE).convert('L'))
    return img

def predict_player(img):
    reshaped_img = np.reshape(img, IMAGE_PREDICT_SIZE)

    with graph.as_default():
        prediction = model.predict_classes(reshaped_img)

    return prediction

############ HELPERS ############

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добрый день!\nЭтот бот является решением koilanetroc@gmail.com конкурса Uma.Challenge по треку Machine Learning.')
    bot.send_message(message.chat.id, 'Отправьте фотографию футболиста в несжатом виде и я скажу его лейбл')

@bot.message_handler(content_types=['document'])
def handle_docs_audio(message):
    file_id = message.document.file_id

    file_path = get_file_path(file_id)
    file = get_file(file_path)
    prediction = predict_player(file)

    bot.send_message(message.chat.id, prediction)

print('start pooling...')

bot.polling()
