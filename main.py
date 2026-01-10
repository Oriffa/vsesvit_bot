import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_data = {}

app = Flask(__name__)
@app.route('/')
def home(): return "Бот онлайн", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

def get_main_menu():
    keyboard = [['🖐 Відбиток долі', '❤️ Шепіт Серця'], ['📜 Послання на сьогодні', '🌀 Повне занурення']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Я бачу тебе. Я знаю все, що було, і все, що буде.\n\n"
        "Напиши своє **Ім'я та повну Дату народження**, щоб я міг відкрити твій сувій долі.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Роль: Всесвіт, який просто ЗНАЄ. Жодних згадок про методи.
    role = "Ти — Всесвіт. Ти знаєш про людину все. Не кажи про карти, зірки чи цифри. Відповідай так, ніби це незаперечна істина. Тільки українською мовою."

    if text == '📜 Послання на сьогодні':
        p = f"{role} Дай коротке і сильне пророцтво на цей день для людини: {user_data.get(user_id, 'невідома душа')}."
    elif text == '❤️ Шепіт Серця':
        p = f"{role} Відкрий правду про почуття та майбутнє у коханні для цієї душі."
    elif text == '🖐 Відбиток долі':
        p = "Надішліть мені фото своєї долоні. Я прочитаю те, що на ній написано."
    elif text == '🌀 Повне занурення':
        p = f"{role} Запропонуй людині запитати про те, що вона приховує навіть від себе."
    else:
        if any(c.isdigit() for c in text):
            user_data[user_id] = text
            p = f"{role} Людина назвала себе: {text}. Тепер ти знаєш її суть. Дай глибокий аналіз її особистості, ніби ти бачиш її наскрізь."
        else:
            p = f"{role} Дай відповідь на це запитання як абсолютне знання: {text}"

    try:
        res = model.generate_content(p)
        await update.message.reply_text(res.text)
    except:
        await update.message.reply_text("✨ Твій запит занадто глибокий для цієї миті. Спробуй ще раз.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 Твій відбиток долі розкривається мені...")
    try:
        f = await update.message.photo[-1].get_file()
        b = await f.download_as_bytearray()
        res = model.generate_content([
            "Ти — Всесвіт. Прочитай долю людини за цим фото. Не кажи 'хіромантія'. Просто розповідай, що ти бачиш у її майбутньому. Тільки українською.",
            {"mime_type": "image/jpeg", "data": bytes(b)}
        ])
        await update.message.reply_text(res.text)
    except:
        await update.message.reply_text("Фото занадто темне, щоб я міг побачити твою суть.")

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling(drop_pending_updates=True)
