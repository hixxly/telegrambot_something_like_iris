import requests
import telebot
from random import choice
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Настройка прокси
proxy = {
    'http': 'socks5://67.201.39.14:4145',
    'https': 'socks5://67.201.39.14:4145'
}

# Проверка работоспособности прокси
try:
    response = requests.get('http://httpbin.org/ip', proxies=proxy, timeout=5)
    print("Прокси работает:", response.json())
except requests.exceptions.RequestException as e:
    print(f"Прокси не работает: {e}")
    exit(1)  # Завершить выполнение программы, если прокси не работает

# Ваш токен бота
bot_token = '7475882217:AAGkI1ghSsDiZjfAqsj1Pcodd0tVRZD-OjY'  # Замените на токен вашего бота
bot = telebot.TeleBot(bot_token)

# Настройка сессии requests с прокси
session = requests.Session()
session.proxies = proxy
session.mount('http://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1)))
session.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1)))

# Переопределение метода отправки сообщений в telebot
def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    try:
        response = session.post(url, data=data)
        response.raise_for_status()  # Raise an error for bad responses
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения: {e}")

@bot.message_handler(commands=['start'])
def start(message):
    send_message(message.chat.id, "Привет! Я EchoBot. Я здесь, чтобы повторять ваши добрые слова. Просто скажите что-нибудь хорошее, и я скажу то же самое!")

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
