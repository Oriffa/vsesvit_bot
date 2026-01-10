import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Ключі
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Словник для пам'яті (ім'я та дата)
user_info = {}

app = Flask(__name__)
@app.route('/')
def home(): return "Оракул онлайн", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

def get_main_menu():
    keyboard = [['🖐 Відбиток долі', '❤️ Шепіт Серця'], ['📜 Послання на сьогодні', '🌀 Повне занурення']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Вітаю, душе. Я твій провідник: Таролог, Нумеролог та Психолог.\n\n"
        "Щоб я міг зазирнути у твою долю, напиши своє **Ім'я та повну Дату народження**.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Визначаємо роль бота
    base_role = "Ти — професійний Таролог, Нумеролог, Психолог та Езотерик. Відповідай глибоко, містично, але з психологічним підходом. Тільки українською мовою. "

    if text == '📜 Послання на сьогодні':
        info = user_info.get(user_id, "користувач")
        prompt = f"{base_role} Дай персональне передбачення на сьогодні для {info}. Використовуй знання про енергію планет."
    elif text == '❤️ Шепіт Серця':
        prompt = f"{base_role} Ти експерт із відносин. Дай глибоку пораду про кохання, яка допоможе людині відкрити серце."
    elif text == '🖐 Відбиток долі':
        prompt = "Попроси користувача надіслати ФОТО долоні. Скажи, що ти проаналізуєш лінії життя, серця та розуму."
    elif text == '🌀 Повне занурення':
        prompt = f"{base_role} Запропонуй розкрити таємницю підсвідомості. Запитай, яка ситуація зараз найбільше турбує людину."
    else:
        # Зберігаємо дані користувача (ім'я/дата) або відповідаємо на питання
        if any(char.isdigit() for char in text): # Якщо в тексті є цифри, вважаємо це датою
            user_info[user_id] = text
            prompt = f"{base_role} Користувач надав свої дані: {text}. Зроби короткий нумерологічний розрахунок і скажи головне про його призначення."
        else:
            prompt = f"{base_role} Дай глибоку відповідь як оракул на це: {text}"

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text("🌌 Енергетичний канал заблоковано... Спробуй ще раз.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # АНАЛІЗ ФОТО ДОЛОНІ
    await update.message.reply_text("🔮 Бачу твої лінії... Зчитую інформацію з твого відбитку долі...")
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()
        
        response = model.generate_content([
            "Ти професійний Хіромант. Проаналізуй лінії на цій долоні. Розкажи про характер, здоров'я та майбутнє. Відповідай українською.",
            {"mime_type": "image/jpeg", "data": bytes(photo_bytes)}
        ])
        await update.message.reply_text(response.text)
    except Exception:
        await update.message.reply_text("Фото нечітке. Зроби знімок долоні при кращому освітленні.")

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo)) # Додаємо реакцію на фото
    application.run_polling(drop_pending_updates=True)
