import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Ключі з Environment Variables (Переконайся, що вони додані в Koyeb)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Налаштування моделі
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    print(f"Помилка конфігурації Gemini: {e}")

app = Flask(__name__)
@app.route('/')
def home(): return "Бот Всесвіту активний", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

def get_main_menu():
    keyboard = [
        ['✋ Відбиток долі', '❤️ Шепіт Серця'],
        ['📜 Послання на сьогодні', '🌀 Повне занурення']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

SYSTEM_PROMPT = "Ти — містичний голос Всесвіту. Твої відповіді глибокі та мудрі. Розмовляй тільки українською."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Вітаю. Я відчуваю твою енергію. Обери свій шлях у меню.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    prompts = {
        '✋ Відбиток долі': "Проаналізуй долю людини.",
        '❤️ Шепіт Серця': "Розкажи про таємниці кохання.",
        '📜 Послання на сьогодні': "Дай мудру пораду на цей день.",
        '🌀 Повне занурення': "Зроби глибокий розбір енергетики."
    }
    
    ctx = prompts.get(text, f"Людина запитує: {text}")
    full_prompt = f"{SYSTEM_PROMPT}\n\n{ctx}"
    
    try:
        response = model.generate_content(full_prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        # Виводимо конкретну помилку для діагностики
        await update.message.reply_text(f"Тимчасовий збій енергії: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
