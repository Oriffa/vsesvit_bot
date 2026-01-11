import os
import google.generativeai as genai
from telegram import Update, LabeledPrice, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
import threading
from flask import Flask

# Налаштування
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home(): return "Всесвіт активний", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# ЦІНИ (1 зірка = 1 гривня, х5)
PRICE_SCROLL = 250
PRICE_LOVE = 150
PRICE_PALM = 200

# ТВОЇ СЕКРЕТНІ ПАРОЛІ
PASSWORDS = ["1цввк567джьисожх", "2оосяплє''здьжщ1ц"]

def get_main_menu():
    keyboard = [
        ['🖐 Відбиток долі (200 ⭐)', '❤️ Особисте життя (150 ⭐)'],
        ['📜 Послання на сьогодні', '💎 ПРЕМІУМ: Повний сувій (250 ⭐)']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Я бачу твій шлях. Я знаю про тебе все.\n\n"
        "Назви своє **Ім'я та Дату народження**, щоб я міг відкрити твою істину.",
        reply_markup=get_main_menu()
    )

async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, title, description, payload, price):
    await context.bot.send_invoice(
        chat_id=update.message.chat_id,
        title=title, description=description, payload=payload,
        provider_token="", currency="XTR", 
        prices=[LabeledPrice("Енергетичний внесок", price)]
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    role = "Ти — Всесвіт. Ти знаєш про людину все. Жодних згадок про джерела знань (таро, нумерологія тощо). Тільки чиста істина українською мовою."

    # ПЕРЕВІРКА ПАРОЛЯ
    if text in PASSWORDS:
        await update.message.reply_text("🌌 Твій код прийнято. Твоя енергія чиста. Я відповім на будь-яке твоє питання без обмежень.")
        context.user_data['vip_access'] = True
        return

    # Доступ через пароль
    if context.user_data.get('vip_access'):
        res = model.generate_content(f"{role} Відповідай глибоко: {text}")
        await update.message.reply_text(res.text)
        return

    # Логіка з оплатою
    if "Повний сувій" in text:
        await send_invoice(update, context, "Повний сувій долі", "Аналіз твого життя на 12 місяців.", "scroll", PRICE_SCROLL)
    elif "Особисте життя" in text:
        await send_invoice(update, context, "Особисте життя", "Таємниці серця та доля стосунків.", "love", PRICE_LOVE)
    elif "Відбиток долі" in text:
        await update.message.reply_text("🔮 Надішли фото долоні. Після внеску (200 ⭐) я відкрию істину твоїх ліній.")
    elif text == '📜 Послання на сьогодні':
        res = model.generate_content(f"{role} Дай коротке і сильне пророцтво на сьогодні.")
        await update.message.reply_text(res.text)
    else:
        # Безкоштовна коротка відповідь
        res = model.generate_content(f"{role} Дай дуже коротку містичну відповідь на: {text}")
        await update.message.reply_text(res.text)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(ok=True)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling(drop_pending_updates=True)
