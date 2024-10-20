import requests
import json
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import schedule
import time
from datetime import datetime
import os

# Токен бота
TOKEN = os.getenv("TELEGRAM_TOKEN")

# URL для получения курса валют от ЦБРФ
CURRENCY_API_URL = 'https://www.cbr-xml-daily.ru/daily_json.js'

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Функция для получения курса доллара
def get_usd_rate():
    try:
        response = requests.get(CURRENCY_API_URL)
        data = response.json()
        usd_rate = data['Valute']['USD']['Value']
        return usd_rate
    except Exception as e:
        logging.error(f"Error getting USD rate: {e}")
        return None

# Функция для отправки курса в чат
def send_daily_rate(context: CallbackContext):
    usd_rate = get_usd_rate()
    if usd_rate:
        message = f"Курс доллара на {datetime.now().strftime('%d.%m.%Y')}: {usd_rate:.2f} ₽"
        context.bot.send_message(chat_id=context.job.context, text=message)

# Команда /start
def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.job_queue.run_daily(send_daily_rate, time=datetime.time(9, 0, 0), context=chat_id)  # Отправляем сообщение каждый день в 9:00
    update.message.reply_text('Я буду присылать курс доллара каждый день в 9:00.')

# Основная функция для запуска бота
def main():
    # Создаем объект Updater и передаем ему токен
    updater = Updater(TOKEN, use_context=True)
    
    # Получаем диспетчера для регистрации хендлеров
    dp = updater.dispatcher
    
    # Регистрируем команду /start
    dp.add_handler(CommandHandler("start", start))
    
    # Запускаем бота
    updater.start_polling()

    # Бесконечная работа
    updater.idle()

if __name__ == '__main__':
    main()
