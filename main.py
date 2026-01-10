import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Ключі з Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Налаштування моделі (Виправлено назву для усунення помилки 404)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

app = Flask(__name__)
@app.route('/')
def home(): return "Всесвіт на зв'язку", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# Містичне меню
def get_main_menu():
    keyboard = [
        ['✋ Відбиток долі', '❤️ Шепіт Серця'],
        ['📜 Послання на сьогодні', '🌀 Повне занурення']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Системна установка для ШІ (Жодних згадок про джерела)
SYSTEM_PROMPT = (
    "Ти — містичний голос Всесвіту. Твої відповіді глибокі, загадкові та мудрі. "
    "Ти розмовляєш тільки українською мовою. Ти ніколи не згадуєш, що ти ШІ, "
    "не кажеш про Google або алгоритми. Ти знаєш про людину все через енергію."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Вітаю у Всесвіті. Я бачив твій прихід.\n\n"
        "Обери шлях, яким ми підемо сьогодні, або надішли фото для розшифровки твого буття.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context_prompt = ""
    
    if text == '✋ Відбиток долі':
        context_prompt = "Проаналізуй лінії на долоні. Розкажи про минуле та майбутнє."
    elif text == '❤️ Шепіт Серця':
        context_prompt = "Ти бачиш серце наскрізь. Розкажи про кохання та почуття."
    elif text == '📜 Послання на сьогодні':
        context_prompt = "Дай коротке, але сильне містичне передбачення на цей день."
    elif text == '🌀 Повне занурення':
        context_prompt = "Зроби глибокий аналіз енергетики людини, її призначення та таємних сил."
    else:
        context_prompt = f"Людина питає: '{text}'. Дай відповідь як оракул."

    full_prompt = f"{SYSTEM_PROMPT}\n\n{context_prompt}"
    
    try:
        if not update.message.photo:
            response = model.generate_content(full_prompt)
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("🌀 Енергія зчитується... Зачекай.")
    except Exception as e:
        await update.message.reply_text("Зв'язок із Всесвітом перервано. Спробуй ще раз.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    
    instruction = f"{SYSTEM_PROMPT}\nПроаналізуй це зображення як містичний артефакт (долоню, обличчя або знаки) і дай розгорнуту відповідь."
    
    try:
        response = model.generate_content([
            instruction,
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception as e:
        # Виправлення помилки версії v1beta у коді
        await update.message.reply_text("Помилка зчитування образу. Переконайся, що модель налаштована на v1.")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    application.run_polling()
