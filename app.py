import os
from flask import Flask
import telebot
import threading
import time

# --- НАСТРОЙКИ ---
TOKEN = "9159685085:AAF80_Fi5TityiuaG6yFq0uSoLE-I4yY7oE"  
ADMIN_ID = 7445549258       

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    bot.reply_to(message, "Приветствую тебя, путник!\nЭто анкета на должность администратора/помощника.\n\n1. Как вас зовут?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    if user_id not in user_data:
        bot.reply_to(message, "Пожалуйста, начните с команды /start")
        return

    data = user_data[user_id]
    step = len(data)
    text = message.text

    if step == 0:
        data['name'] = text
        bot.reply_to(message, "2. Сколько вам лет? (не меньше 13)")
    elif step == 1:
        data['age'] = text
        bot.reply_to(message, "3. Сколько времени вы готовы уделять?")
    elif step == 2:
        data['time'] = text
        bot.reply_to(message, "4. Временно зарплаты не будет. Вас это устраивает? (Да/Нет)")
    elif step == 3:
        data['salary'] = text
        bot.reply_to(message, "5. На сколько ваш часовой пояс отличается от московского?")
    elif step == 4:
        data['timezone'] = text
        bot.reply_to(message, "6. Насколько хорошо вы знаете русский язык?")
    elif step == 5:
        data['russian'] = text
        bot.reply_to(message, "7. Кто вам интересен: Корректор или Помощник?")
    elif step == 6:
        data['role'] = text
        bot.reply_to(message, "8. Знакомы ли вы с моим AU? Готовы ли изучить?")
    elif step == 7:
        data['au'] = text
        final_text = (
            f"🔔 Новая анкета!\n\n"
            f"👤 Имя: {data['name']}\n"
            f"🎂 Возраст: {data['age']}\n"
            f"⏰ Время: {data['time']}\n"
            f"💰 Зарплата: {data['salary']}\n"
            f"🌍 Часовой пояс: {data['timezone']}\n"
            f"🇷🇺 Русский: {data['russian']}\n"
            f"💼 Роль: {data['role']}\n"
            f"🎨 AU: {data['au']}\n\n"
            f"ID для ответа: `{user_id}`"
        )
        bot.send_message(ADMIN_ID, final_text, parse_mode='Markdown')
        bot.reply_to(message, "Спасибо! Ваша анкета отправлена.")
        del user_data[user_id]

# Запускаем бота в фоновом режиме (поллинг)
def run_bot():
    # Удаляем старый вебхук, если он был (чтобы не мешал)
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()

# Веб-сервер для Render
@app.route('/')
def home():
    return "Bot is alive!"

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    threading.Thread(target=run_bot, daemon=True).start()
    # Запускаем Flask для Render
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))
