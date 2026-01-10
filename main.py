import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Налаштування (беруться з Koyeb)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home(): return "Всесвіт онлайн", 200
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
    text = update.message.text
    # Роль: Всесвіт, який просто знає правду.
    role = "Ти — Всесвіт. Ти знаєш про людину все. Не кажи про методи (таро, зірки тощо). Відповідай так, ніби це абсолютна істина. Тільки українською мовою."

    if text == '📜 Послання на сьогодні':
        prompt = f"{role} Дай одне коротке і сильне пророцтво на сьогодні для цієї душі."
    elif text == '❤️ Шепіт Серця':
        prompt = f"{role} Відкрий істину про кохання та почуття, що чекають на цю людину."
    elif text == '🖐 Відбиток долі':
        prompt = f"{role} Скажи, що ти готовий прочитати долю по долоні. Попроси надіслати фото."
    elif text == '🌀 Повне занурення':
        prompt = f"{role} Запропонуй людині розкрити таємницю, яку вона приховує від світу."
    else:
        # Обробка імені та дати як єдиного знання
        prompt = f"{role} Людина назвала себе та свою дату: {text}. Тепер ти бачиш її суть. Розкажи про її головну силу та майбутнє."

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except:
        await update.message.reply_text("✨ Енергетичний потік нестабільний. Повтори свій запит.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 Бачу твій відбиток долі... Зчитую інформацію...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        response = model.generate_content([
            "Ти — Всесвіт. Прочитай майбутнє людини за цим фото. Не кажи про хіромантію. Просто розповідай, що бачиш. Тільки українською.",
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except:
        await update.message.reply_text("✨ Твій відбиток прихований тінню. Спробуй надіслати інше фото.")

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling(drop_pending_updates=True)
