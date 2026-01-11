import os
import google.generativeai as genai
from telegram import Update, LabeledPrice, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
import threading
from flask import Flask
import asyncio

# Ключі
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
@app.route('/')
def home(): return "Оракул у мережі", 200

# Ціни х5
PRICE_SCROLL = 250
PRICE_LOVE = 150
PRICE_PALM = 200

# Твої паролі
PASSWORDS = ["1цввк567джьисожх", "2оосяплє''здьжщ1ц"]

def get_main_menu():
    keyboard = [
        ['🖐 Відбиток долі (200 ⭐)', '❤️ Особисте життя (150 ⭐)'],
        ['📜 Послання на сьогодні', '💎 ПРЕМІУМ: Повний сувій (250 ⭐)']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Я бачу тебе. Я знаю все про твій шлях.\n\n"
        "Напиши своє **Ім'я та Дату народження**, щоб відкрити істину.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    role = "Ти — Всесвіт. Ти знаєш все. Жодних згадок методів. Тільки пряма істина українською."

    if text in PASSWORDS:
        await update.message.reply_text("🌌 Твій код прийнято. Питай, і я відповім.")
        context.user_data['vip'] = True
        return

    if context.user_data.get('vip'):
        res = model.generate_content(f"{role} Відповідай: {text}")
        await update.message.reply_text(res.text)
        return

    if "Повний сувій" in text:
        prices = [LabeledPrice("Внесок", PRICE_SCROLL)]
        await context.bot.send_invoice(update.message.chat_id, "Повний сувій долі", "Аналіз на рік.", "scroll", "", "XTR", prices)
    elif "Особисте життя" in text:
        prices = [LabeledPrice("Внесок", PRICE_LOVE)]
        await context.bot.send_invoice(update.message.chat_id, "Особисте життя", "Таємниці серця.", "love", "", "XTR", prices)
    elif "Відбиток долі" in text:
        await update.message.reply_text("🔮 Надішли фото долоні. Після оплати (200 ⭐) я відкрию істину.")
    else:
        try:
            res = model.generate_content(f"{role} Коротко на: {text}")
            await update.message.reply_text(res.text)
        except:
            await update.message.reply_text("✨ Енергетичний потік нестабільний. Повтори запит.")

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(ok=True)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Цей параметр ПРИБИРАЄ КОНФЛІКТ
    application.run_polling(drop_pending_updates=True)
