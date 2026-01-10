import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Ключі з Koyeb
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Налаштування моделі - ВИПРАВЛЕНО
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-pro')

app = Flask(__name__)
@app.route('/')
def home(): return "Бот Всесвіт працює!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# Твоє меню
def get_main_menu():
    keyboard = [
        ['🖐 Відбиток долі', '❤️ Шепіт Серця'],
        ['📜 Послання на сьогодні', '🌀 Повне занурення']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Вітаю у Всесвіті! Я твій містичний провідник.\nОбери послугу:",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    prompts = {
        '🖐 Відбиток долі': "Ти містичний хіромант. Очікуй фото. Відповідай українською.",
        '❤️ Шепіт Серця': "Ти духовний наставник про любов. Відповідай українською.",
        '📜 Послання на сьогодні': "Дай містичне передбачення на сьогодні українською.",
        '🌀 Повне занурення': "Ти глибокий філософський оракул. Відповідай українською."
    }
    prompt = prompts.get(text, "Просто поспілкуйся зі мною як мудрий Всесвіт українською.")
    
    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Вибачте, сталася помилка: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    await update.message.reply_text("🔮 Аналізую...")
    
    # Виправлено для фото
    vision_model = genai.GenerativeModel('models/gemini-pro-vision')
    try:
        response = vision_model.generate_content([
            "Проаналізуй фото у містичному стилі українською мовою.",
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Помилка аналізу: {e}")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling(drop_pending_updates=True)
