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

app = Flask(__name__)
@app.route('/')
def home(): return "Оракул працює", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

def get_main_menu():
    keyboard = [['🖐 Відбиток долі', '❤️ Шепіт Серця'], ['📜 Послання на сьогодні', '🌀 Повне занурення']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Вітаю, душе. Я твій провідник у світ езотерики, нумерології та психології.\n\n"
        "Щоб я міг бачити твою долю чітко, напиши своє **Ім'я та повну Дату народження**.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # Промпт, що задає боту професійні ролі
    base_role = "Ти - поєднання Таролога, Нумеролога, Психолога та Езотерика. Твої передбачення глибокі, реальні та трохи містичні. "

    if text == '📜 Послання на сьогодні':
        prompt = base_role + "Дай чітке містичне передбачення на сьогодні на основі енергії дня. Коротко."
    elif text == '❤️ Шепіт Серця':
        prompt = base_role + "Ти Психолог-езотерик. Проаналізуй сферу кохання та дай пораду, яка змінить життя."
    elif text == '🖐 Відбиток долі':
        prompt = base_role + "Попроси надіслати фото долоні. Скажи, що лінії розкажуть про минуле та майбутнє."
    elif text == '🌀 Повне занурення':
        prompt = base_role + "Запропонуй людині розкрити таємницю її підсвідомості. Запитай, що її турбує."
    else:
        prompt = base_role + f"Користувач каже: {text}. Якщо це ім'я та дата - зроби нумерологічний аналіз. Якщо питання - дай глибоку відповідь."

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Зв'язок із космосом перервано... Спробуй пізніше.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ОБРОБКА ФОТО (Хіромантія)
    await update.message.reply_text("🔮 Бачу твої лінії... Аналізую відбиток долі...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        response = model.generate_content([
            "Ти професійний Хіромант. Проаналізуй лінії на цій долоні. Розкажи про характер, кар'єру та здоров'я українською мовою.",
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("Фото надто туманне для мого зору. Спробуй ще раз.")

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo)) # РЕАКЦІЯ НА ФОТО
    application.run_polling(drop_pending_updates=True)
