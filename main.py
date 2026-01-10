import os
import google.generativeai as genai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

# Ключі (беруться з налаштувань Koyeb)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Налаштування Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Функція вибору моделі, щоб уникнути помилки 404
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Вибираємо найновішу доступну модель
    selected_model = available_models[0] if available_models else 'gemini-1.5-flash'
    model = genai.GenerativeModel(selected_model)
except Exception:
    model = genai.GenerativeModel('gemini-1.5-flash')

# Веб-сервер для Koyeb
app = Flask(__name__)
@app.route('/')
def home(): return "Всесвіт онлайн!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# Головне меню
def get_main_menu():
    keyboard = [
        ['🖐 Відбиток долі', '❤️ Шепіт Серця'],
        ['📜 Послання на сьогодні', '🌀 Повне занурення']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Вітаю у Всесвіті! Я твій містичний провідник.\nОбери свій шлях нижче:",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Створюємо містичні інструкції для кожної кнопки
    if text == '📜 Послання на сьогодні':
        prompt = "Ти — Всесвіт. Дай одне коротке, загадкове і надихаюче передбачення на сьогодні. Тільки 1-2 речення українською мовою. Без списків!"
    elif text == '❤️ Шепіт Серця':
        prompt = "Ти — голос істинного кохання. Дай одну коротку і глибоку пораду про стосунки. Тільки 1 речення українською."
    elif text == '🖐 Відбиток долі':
        prompt = "Ти — таємничий хіромант. Попроси користувача надіслати фото його долоні, щоб ти міг побачити лінії його долі."
    elif text == '🌀 Повне занурення':
        prompt = "Ти — оракул глибоких істин. Запропонуй користувачеві поставити будь-яке питання про його життя."
    else:
        # Для звичайних повідомлень
        prompt = f"Ти — мудрий Всесвіт. Відповідай коротко (до 2 речень), містично і тільки українською мовою на це: {text}"

    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        if "403" in str(e):
            await update.message.reply_text("🔮 Твій ключ доступу заблоковано Google. Потрібно оновити API Key в налаштуваннях Koyeb.")
        else:
            await update.message.reply_text("🌌 Зірки зараз приховані хмарами... Спробуй ще раз за мить.")

if __name__ == '__main__':
    # Запуск Flask у фоновому режимі
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Запуск Telegram бота
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Видаляємо старі оновлення, щоб не було конфліктів
    application.run_polling(drop_pending_updates=True)
