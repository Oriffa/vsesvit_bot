import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Тепер беремо ключі з налаштувань системи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)
@app.route('/')
def home(): return "OK", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Вітаю у Всесвіті! Надішліть фото долоні.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    await update.message.reply_text("🔮 Аналізую...")
    try:
        response = model.generate_content([
            "Ти — містичний хіромант. Проаналізуй долоню українською мовою.",
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Помилка: {e}")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()
