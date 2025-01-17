import requests
import telebot
from telebot import types
from random import choice

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
TOKEN = '7475882217:AAGkI1ghSsDiZjfAqsj1Pcodd0tVRZD-OjY'  # Замените на токен вашего бота
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
        print(f"Ошибка при отправке сообщения: {e}")

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
            bot.ban_chat_member(chat_id, user_id)  # Баним пользователя
            username = message.reply_to_message.from_user.username or "неизвестный пользователь"
            send_message(message.chat.id, f"Пользователь @{username} забанен.")
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

@bot.message_handler(func=lambda message: "https://" in message.text)
def link_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Получаем статус пользователя
    user_status = bot.get_chat_member(chat_id, user_id).status

    if user_status not in ['administrator', 'creator']:
        bot.ban_chat_member(chat_id, user_id)  # Бан пользователя
        username = message.from_user.username or "неизвестный пользователь"  # Защита от отсутствия username
        send_message(message.chat.id, f"Пользователь @{username} нарушил правила группы и был забанен.")
    else:
        send_message(message.chat.id, "Ссылки отправил администратор. Бан не применён.")

# Запуск бота
bot.infinity_polling(none_stop=True)
