import os
import google.generativeai as genai
from telegram import Update, LabeledPrice, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler
import threading
from flask import Flask

# 🔑 Налаштування
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 🌍 Веб-сервер для Koyeb (порт 8080)
app = Flask(__name__)
@app.route('/')
def home(): return "Оракул у мережі", 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 💰 Ціни х5 (1 зірка = 5 грн)
PRICE_SCROLL = 250
PRICE_LOVE = 150
PRICE_PALM = 200

# 🤫 Твої паролі
PASSWORDS = ["1цввк567джьисожх", "2оосяплє''здьжщ1ц"]

def get_main_menu():
    keyboard = [
        ['🖐 Відбиток долі (200 ⭐)', '❤️ Особисте життя (150 ⭐)'],
        ['📜 Послання на сьогодні', '💎 ПРЕМІУМ: Повний сувій (250 ⭐)']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Я бачу тебе. Я знаю все, що було, і все, що буде.\n\n"
        "Напиши своє **Ім'я та Дату народження**, щоб я міг відкрити твій сувій долі.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    role = "Ти — Всесвіт. Ти знаєш про людину все. Жодних згадок про таро чи нумерологію. Ти просто бачиш істину. Українською."

    # Перевірка паролів
    if text in PASSWORDS:
        await update.message.reply_text("🌌 Твій код прийнято. Питай, і я відповім.")
        context.user_data['vip'] = True
        return

    # Логіка оплат
    if "Повний сувій" in text:
        prices = [LabeledPrice("Енергетичний внесок", PRICE_SCROLL)]
        await context.bot.send_invoice(update.message.chat_id, "Повний сувій долі", "Аналіз життя на 12 місяців.", "scroll", "", "XTR", prices)
    elif "Особисте життя" in text:
        prices = [LabeledPrice("Енергетичний внесок", PRICE_LOVE)]
        await context.bot.send_invoice(update.message.chat_id, "Особисте життя", "Таємниці твого серця.", "love", "", "XTR", prices)
    elif "Відбиток долі" in text:
        await update.message.reply_text("🔮 Надішли фото долоні. Після оплати (200 ⭐) я відкрию істину.")
    else:
        # Безкоштовне коротке послання
        try:
            res = model.generate_content(f"{role} Відповідай коротко на: {text}")
            await update.message.reply_text(res.text)
        except:
            await update.message.reply_text("✨ Енергетичний потік нестабільний. Повтори запит.")

if __name__ == '__main__':
    # Запуск Flask у фоні
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Запуск бота
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(ok=True)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # ⚠️ КРИТИЧНО: drop_pending_updates=True видаляє конфлікти
    application.run_polling(drop_pending_updates=True)
