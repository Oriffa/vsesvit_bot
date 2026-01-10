import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Ключі вже в налаштуваннях Koyeb
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home(): return "Бот працює!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# Просте меню українською
def get_main_menu():
    keyboard = [['🤖 Запитати Всесвіт'], ['🖼 Аналіз фото']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я твій інтелектуальний помічник 'Всесвіт'.\n\nЯ можу відповідати на твої питання та аналізувати зображення. Що тебе цікавить?",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if user_text in ['🤖 Запитати Всесвіт', '🖼 Аналіз фото']:
        await update.message.reply_text("Я слухаю тебе. Напиши своє питання або надішли фото.")
        return

    try:
        response = model.generate_content(f"Відповідай українською мовою: {user_text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Вибач, сталася помилка: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    await update.message.reply_text("Аналізую зображення...")
    try:
        response = model.generate_content([
            "Опиши, що на цьому фото українською мовою, та дай свої рекомендації.",
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Помилка при обробці фото: {e}")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()
