import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# 1. НАЛАШТУВАННЯ (ОБОВ'ЯЗКОВО ПЕРЕВІР СВОЇ КЛЮЧІ)
8463164329:AAGPNll44K_NAVMPm7EHFqFT7zxs6MfGPiM

AIzaSyAihaTmWx_GMAtiR0suXMbbZUmqMFw_aOI
# Налаштування Gemini (1500 запитів/день безкоштовно)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Налаштування Flask для Koyeb (щоб сервіс бачив активність)
app = Flask(__name__)
@app.route('/')
def home():
    return "Всесвіт працює!", 200

def run_flask():
    # Koyeb використовує порт 8080 за замовчуванням
    app.run(host='0.0.0.0', port=8080)

# Логіка бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Вітаю у Всесвіті! Я — твій містичний провідник. Надішліть фото своєї долоні, і я розкрию таємниці долі.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отримуємо фото
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    
    await update.message.reply_text("🔮 Зірки дивляться на твої лінії... Аналізую долоню...")
    
    try:
        # Запит до Gemini
        response = model.generate_content([
            "Ти — професійний і містичний хіромант. Проаналізуй лінії на цій долоні українською мовою. "
            "Зверни увагу на лінію життя, серця та розуму. Дай загальний магічний прогноз.",
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Магічний зв'язок перервано: {e}")

if __name__ == '__main__':
    # Запускаємо веб-сервер у фоновому потоці
    threading.Thread(target=run_flask).start()
    
    # Запускаємо Telegram бота
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Бот запускається...")
    application.run_polling()
