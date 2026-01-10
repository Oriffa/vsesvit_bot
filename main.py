import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Автоматичний вибір моделі, щоб уникнути 404
try:
    # Пробуємо знайти актуальну назву моделі в системі
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = 'models/gemini-pro' if 'models/gemini-pro' in available_models else available_models[0]
    model = genai.GenerativeModel(model_name)
except Exception:
    # Якщо список не підтягнувся, ставимо універсальну назву
    model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)
@app.route('/')
def home(): return "Бот працює!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

def get_main_menu():
    keyboard = [['🖐 Відбиток долі', '❤️ Шепіт Серця'], ['📜 Послання на сьогодні', '🌀 Повне занурення']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Вітаю! Всесвіт на зв'язку. Оберіть кнопку:", reply_markup=get_main_menu())

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Додаємо чітку інструкцію для кожної кнопки
    instruction = "Відповідай українською мовою. "
    if text == '📜 Послання на сьогодні':
        instruction += "Дай коротке магічне передбачення."
    else:
        instruction += f"Дай відповідь на запит: {text}"

    try:
        # Використовуємо спрощений виклик
        response = model.generate_content(instruction)
        await update.message.reply_text(response.text)
    except Exception as e:
        # Виводимо назву моделі, яку намагався використати бот, щоб зрозуміти проблему
        await update.message.reply_text(f"Помилка моделі {model.model_name}: {e}")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
