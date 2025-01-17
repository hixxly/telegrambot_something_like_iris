import requests
import telebot
from telebot import types
from random import choice
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
TOKEN = 'YOUR_BOT_TOKEN'  # Замените на токен вашего бота
bot = telebot.TeleBot(TOKEN)

# Создание сессии для отправки сообщений
session = requests.Session()

# Переопределение метода отправки сообщений в telebot
def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    try:
        response = session.post(url, data=data)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")

# Хэндлер для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    send_message(message.chat.id, "Привет! Я бот, который может банить пользователей и повторять ваши добрые слова. Просто скажите что-нибудь хорошее!")

# Хэндлер для команды /ban
@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message:  # Проверяем, что команда отправлена в ответ на сообщение
        chat_id = message.chat.id
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status  # Получаем статус пользователя

        if user_status in ['administrator', 'creator']:
            send_message(message.chat.id, "Невозможно забанить администратора.")
        else:
            try:
                bot.ban_chat_member(chat_id, user_id)  # Баним пользователя
                username = message.reply_to_message.from_user.username or "неизвестный пользователь"
                send_message(message.chat.id, f"Пользователь @{username} забанен.")
                logging.info(f"Пользователь @{username} был забанен.")
            except Exception as e:
                logging.error(f"Ошибка при бане пользователя: {e}")
    else:
        send_message(message.chat.id, "Пожалуйста, используйте команду в ответ на сообщение пользователя.")

@bot.message_handler(commands=['info'])
def info(message):
    send_message(message.chat.id, "Этот бот создан другим ботом, бла бла...")

@bot.message_handler(commands=['coin'])
def coin(message):
    coin_result = choice(["ОРЕЛ", "РЕШКА"])
    send_message(message.chat.id, coin_result)

@bot.message_handler(func=lambda message: True)
def echo(message):
    send_message(message.chat.id, message.text)

@bot.message_handler(func=lambda message: "http://" in message.text or "https://" in message.text)
def link_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Получаем статус пользователя
    user_status = bot.get_chat_member(chat_id, user_id).status

    if user_status not in ['administrator', 'creator']:
        try:
            bot.ban_chat_member(chat_id, user_id)  # Бан пользователя
            username = message.from_user.username or "неизвестный пользователь"  # Защита от отсутствия username
            bot.send_message(chat_id, f"Пользователь @{username} нарушил правила группы и был забанен.")
            logging.info(f"Пользователь @{username} был забанен за отправку ссылки.")
        except Exception as e:
            logging.error(f"Ошибка при бане пользователя: {e}")
    else:
        bot.send_message(chat_id, "Ссылки отправил администратор. Бан не применён.")

@bot.message_handler(content_types=['new_chat_members'])
def make_some(message):
    new_user = message.new_chat_member
    chat_id = message.chat.id
    user_id = new_user.id

    bot.send_message(chat_id, 'Я принял нового пользователя!')
    bot.approve_chat_join_request(chat_id, user_id)

    # Получаем статус пользователя
    user_status = bot.get_chat_member(chat_id, user_id).status
