import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# 1. ВСТАВ СВОЇ КЛЮЧІ МІЖ ЛАПКАМИ ""
TELEGRAM_TOKEN = "8463164329:AAGPNll44K_NAVMPm7EHFqFT7zxs6MfGPiM"
GEMINI_API_KEY = "AIzaSyAihaTmWx_GMAtiR0suXMbbZUmqMFw_aOI"

# Налаштування Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Веб-сервер для Koyeb
app = Flask(name)
@app.route('/')
def home(): return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Логіка бота
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

if name == 'main':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()
