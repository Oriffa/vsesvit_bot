import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Ключі тепер беруться з налаштувань Koyeb (Environment Variables)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Налаштування моделі (виправлено на актуальну версію)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home(): return "Бот працює!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# Головне меню (Кнопки)
def get_main_menu():
    keyboard = [['🔮 Гадання по руці', '🃏 Карти Таро'], ['☕ Кавова гуща', '✨ Порада Всесвіту']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Вітаю у Всесвіті! Я твій містичний провідник.\n\n"
        "Обери послугу в меню або просто надішліть фото для аналізу.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    prompt = ""
    
    if text == '🔮 Гадання по руці':
        prompt = "Ти — містичний хіромант. Очікуй фото долоні і розкажи про долю за лініями. Відповідай українською."
    elif text == '🃏 Карти Таро':
        prompt = "Ти — майстер Таро. Очікуй фото карт або запитання і зроби розклад. Відповідай українською."
    elif text == '☕ Кавова гуща':
        prompt = "Ти — знавець гадання на каві. Проаналізуй візерунки на фото. Відповідай українською."
    elif text == '✨ Порада Всесвіту':
        prompt = "Дай коротке містичне передбачення або мудру пораду на сьогодні українською мовою."
    else:
        prompt = "Ти — універсальний оракул. Дай відповідь на питання або проаналізуй фото українською мовою."

    if not update.message.photo:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    else:
        await update.message.reply_text("🔮 Аналізую ваше фото...")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    
    # Універсальна інструкція для фото
    instruction = "Ти — містичний оракул. Проаналізуй це зображення (долоню, карти або каву) і дай розгорнуту відповідь українською мовою."
    
    try:
        response = model.generate_content([
            instruction,
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Вибачте, сталася помилка: {e}")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    application.run_polling()
