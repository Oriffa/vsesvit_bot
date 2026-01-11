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
def home(): return "Оракул у мережі", 200

# ЦІНИ х5
PRICE_SCROLL = 250
PRICE_LOVE = 150
PRICE_PALM = 200

# ПАРОЛІ
PASSWORDS = ["1цввк567джьисожх", "2оосяплє''здьжщ1ц"]

def get_main_menu():
    keyboard = [
        ['🖐 Відбиток долі (200 ⭐)', '❤️ Особисте життя (150 ⭐)'],
        ['📜 Послання на сьогодні', '💎 ПРЕМІУМ: Повний сувій (250 ⭐)']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear() # Скидаємо дані для нової анкети
    await update.message.reply_text(
        "✨ Я бачу твій прихід, але щоб відкрити твій шлях, мені потрібно знати твій земний початок.\n\n"
        "Напиши своє **Ім'я та Дату народження** (наприклад: Марія, 12.05.1995).",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_info = context.user_data.get('user_info')
    
    # СИСТЕМНА РОЛЬ (Жодних згадок про джерела!)
    role = "Ти — Всесвіт. Ти знаєш істину. Ти не використовуєш карти чи цифри явно, ти просто бачиш долю. Жодної нумерології. Українською."

    # 1. ПЕРЕВІРКА ПАРОЛЯ
    if text in PASSWORDS:
        await update.message.reply_text("🌌 Твій код прийнято. Я бачу твою долю без перешкод.")
        context.user_data['vip'] = True
        return

    # 2. АНКЕТУВАННЯ (Зберігаємо дані користувача)
    if not user_info and not any(btn in (text or "") for row in get_main_menu().keyboard for btn in row):
        context.user_data['user_info'] = text
        await update.message.reply_text(f"✨ Я відчув твої вібрації, {text}. Тепер твій шлях відкритий. Обери, куди ми попрямуємо далі.", reply_markup=get_main_menu())
        return

    # 3. ОБРОБКА ФОТО (Хіромантія)
    if update.message.photo:
        if context.user_data.get('vip'):
            await update.message.reply_text("🔮 Твій відбиток унікальний. Я бачу лінії твого майбутнього... (Всесвіт готує відповідь)")
            res = model.generate_content(f"{role} Користувач: {user_info}. Аналізуй лінії на долоні (фото отримано) і дай глибоке пророцтво.")
            await update.message.reply_text(res.text)
        else:
            await update.message.reply_text("🔮 Твій відбиток вимагає енергетичного внеску (200 ⭐), щоб я міг його прочитати.")
        return

    # 4. ОБРОБКА КНОПОК ТА ОПЛАТ
    if "Повний сувій" in text:
        await context.bot.send_invoice(update.message.chat_id, "Повний сувій", f"Для {user_info}: Глибоке знання на 12 місяців.", "scroll", "", "XTR", [LabeledPrice("Внесок", PRICE_SCROLL)])
    elif "Особисте життя" in text:
        await context.bot.send_invoice(update.message.chat_id, "Особисте життя", f"Для {user_info}: Таємниці серця.", "love", "", "XTR", [LabeledPrice("Внесок", PRICE_LOVE)])
    elif "Відбиток долі" in text:
        await update.message.reply_text("🔮 Надішли чітке фото своєї долоні.")
    elif "Послання на сьогодні" in text:
        p = f"{role} Користувач {user_info}. Витягни карту (внутрішньо) і дай сильне пророцтво на сьогодні."
        res = model.generate_content(p)
        await update.message.reply_text(res.text)
    else:
        # Вільні питання
        if not user_info:
            await update.message.reply_text("✨ Спершу назви своє Ім'я та Дату народження.")
            return
        p = f"{role} Користувач {user_info} питає: {text}. Дай істинну відповідь."
        try:
            res = model.generate_content(p)
            await update.message.reply_text(res.text)
        except:
            await update.message.reply_text("✨ Енергетичний потік нестабільний. Повтори пізніше.")

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(ok=True)))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    # drop_pending_updates=True ВИДАЛЯЄ КОНФЛІКТИ
    application.run_polling(drop_pending_updates=True)
