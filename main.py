import os
import google.generativeai as genai
from telegram import Update, LabeledPrice, ReplyKeyboardMarkup, KeyboardButton
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
def home(): return "Оракул у мережі", 200

# ЦІНИ х5
PRICE_SCROLL = 250
PRICE_LOVE = 150
PRICE_PALM = 200

# ТВОЇ ПАРОЛІ
PASSWORDS = ["1цввк567джьисожх", "2оосяплє''здьжщ1ц"]

def get_main_menu():
    keyboard = [
        [KeyboardButton('🖐 Відбиток долі (200 ⭐)'), KeyboardButton('❤️ Особисте життя (150 ⭐)')],
        [KeyboardButton('📜 Послання на сьогодні'), KeyboardButton('💎 ПРЕМІУМ: Повний сувій (250 ⭐)')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() 
    await update.message.reply_text(
        "✨ Я бачу твій прихід, але щоб відкрити твій шлях, мені потрібно знати твій земний початок.\n\n"
        "Напиши своє **Ім'я та Дату народження** (наприклад: Марія, 12.05.1995).",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_info = context.user_data.get('user_info')
    role = "Ти — Всесвіт. Ти знаєш істину. Ти не використовуєш карти чи цифри явно, ти просто бачиш долю. Жодних згадок про джерела знань (таро, нумерологія). Українською."

    # 1. Обробка паролів
    if text in PASSWORDS:
        await update.message.reply_text("🌌 Твій код прийнято. Я бачу твою долю без обмежень.")
        context.user_data['vip'] = True
        return

    # 2. Перевірка натискання кнопок (Виправлена логіка)
    menu_buttons = ['🖐 Відбиток долі (200 ⭐)', '❤️ Особисте життя (150 ⭐)', '📜 Послання на сьогодні', '💎 ПРЕМІУМ: Повний сувій (250 ⭐)']
    is_button = text in menu_buttons

    # 3. Реєстрація користувача (якщо це не кнопка і не пароль)
    if not user_info and not is_button:
        context.user_data['user_info'] = text
        await update.message.reply_text(f"✨ Я відчув твої вібрації, {text}. Тепер твій шлях відкритий.", reply_markup=get_main_menu())
        return

    # 4. Робота з кнопками та оплатами
    if "Повний сувій" in text:
        await context.bot.send_invoice(update.message.chat_id, "Повний сувій", f"Для {user_info}: Знання на 12 місяців.", "scroll", "", "XTR", [LabeledPrice("Внесок", PRICE_SCROLL)])
    elif "Особисте життя" in text:
        await context.bot.send_invoice(update.message.chat_id, "Особисте життя", f"Для {user_info}: Таємниці серця.", "love", "", "XTR", [LabeledPrice("Внесок", PRICE_LOVE)])
    elif "Відбиток долі" in text:
        await update.message.reply_text("🔮 Надішли фото своєї долоні. Я прочитаю лінії твого майбутнього.")
    elif "Послання на сьогодні" in text:
        res = model.generate_content(f"{role} Користувач {user_info}. Дай сильне пророцтво на сьогодні.")
        await update.message.reply_text(res.text)
    elif text:
        # Відповідь на будь-яке інше питання
        res = model.generate_content(f"{role} Користувач {user_info} питає: {text}. Дай містичну відповідь.")
        await update.message.reply_text(res.text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = context.user_data.get('user_info')
    role = "Ти — Всесвіт. Ти бачиш долю по лініях рук. Українською."
    
    if context.user_data.get('vip'):
        await update.message.reply_text("🔮 Твій відбиток унікальний. Я бачу твій шлях...")
        res = model.generate_content(f"{role} Користувач {user_info}. Проаналізуй лінії долоні та дай пророцтво.")
        await update.message.reply_text(res.text)
    else:
        await update.message.reply_text("🔮 Внеси енергетичний внесок (200 ⭐) через кнопку 'Відбиток долі', щоб я відкрив істину твоїх ліній.")

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(ok=True)))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(drop_pending_updates=True)
