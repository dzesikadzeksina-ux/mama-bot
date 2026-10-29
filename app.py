import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- НАСТРОЙКИ ---
TOKEN = "9159685085:AAF80_Fi5TityiuaG6yFq0uSoLE-I4yY7oE"
ADMIN_ID = 7445549258       

app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {}
    await update.message.reply_text(
        "Приветствую тебя, путник!\n"
        "Это анкета на должность администратора/помощника.\n\n"
        "1. Как вас зовут?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if user_id not in user_data:
        await update.message.reply_text("Пожалуйста, начните с команды /start")
        return

    data = user_data[user_id]
    step = len(data)

    if step == 0:
        data['name'] = text
        await update.message.reply_text("2. Сколько вам лет? (не меньше 13)")
    elif step == 1:
        data['age'] = text
        await update.message.reply_text("3. Сколько времени вы готовы уделять?")
    elif step == 2:
        data['time'] = text
        await update.message.reply_text("4. Временно зарплаты не будет. Вас это устраивает? (Да/Нет)")
    elif step == 3:
        data['salary'] = text
        await update.message.reply_text("5. На сколько ваш часовой пояс отличается от московского?")
    elif step == 4:
        data['timezone'] = text
        await update.message.reply_text("6. Насколько хорошо вы знаете русский язык?")
    elif step == 5:
        data['russian'] = text
        await update.message.reply_text("7. Кто вам интересен: Корректор или Помощник?")
    elif step == 6:
        data['role'] = text
        await update.message.reply_text("8. Знакомы ли вы с моим AU? Готовы ли изучить?")
    elif step == 7:
        data['au'] = text
        final_text = (
            f"🔔 **Новая анкета!**\n\n"
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
        await context.bot.send_message(chat_id=ADMIN_ID, text=final_text, parse_mode='Markdown')
        await update.message.reply_text("Спасибо! Ваша анкета отправлена.")
        del user_data[user_id]

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/')
def home():
    return "Bot is alive!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return 'ok'

# --- ЗАПУСК ---
if __name__ == '__main__':
    # Устанавливаем вебхук при старте (Render будет вызывать эту функцию)
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    telegram_app.bot.set_webhook(url=webhook_url)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
