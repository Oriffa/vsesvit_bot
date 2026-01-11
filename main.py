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
def home(): return "OK", 200

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
    context.user_data.clear()
    await update.message.reply_text(
        "✨ Я бачу твій прихід. Щоб відкрити істину, мені потрібні твоє **Ім'я та Дата народження**.",
        reply_markup=get_main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return
    
    user_info = context.user_data.get('user_info')
    role = "Ти — Всесвіт. Ти знаєш істину про людину. Жодних згадок таро чи нумерології. Тільки пророцтва українською."

    # 1. ПЕРЕВІРКА ПАРОЛЯ
    if text in PASSWORDS:
        await update.message.reply_text("🌌 Код прийнято. Я бачу твій шлях без перешкод.")
        context.user_data['vip'] = True
        return

    # 2. ПЕРЕВІРКА КНОПОК (Ця логіка тепер не викликає помилок)
    if "Послання на сьогодні" in text:
        info = user_info if user_info else "Мандрівник"
        res = model.generate_content(f"{role} Користувач: {info}. Дай глибоке пророцтво на сьогодні.")
        await update.message.reply_text(res.text)
        return

    if "Особисте життя" in text:
        await context.bot.send_invoice(update.message.chat_id, "Особисте життя", "Таємниці серця.", "love", "", "XTR", [LabeledPrice("Зірки", PRICE_LOVE)])
        return

    if "Повний сувій" in text:
        await context.bot.send_invoice(update.message.chat_id, "Повний сувій", "Твоя доля на 12 місяців.", "scroll", "", "XTR", [LabeledPrice("Зірки", PRICE_SCROLL)])
        return

    if "Відбиток долі" in text:
        await update.message.reply_text("🔮 Надішли фото своєї долоні. Після внеску (200 ⭐) я відкрию істину твоїх ліній.")
        return

    # 3. РЕЄСТРАЦІЯ ІМЕНІ (якщо це не кнопка)
    if not user_info:
        context.user_data['user_info'] = text
        await update.message.reply_text(f"✨ Я відчув твою енергію, {text}. Тепер питай або обирай шлях у меню.")
        return

    # 4. ВІЛЬНІ ПИТАННЯ
    res = model.generate_content(f"{role} Користувач {user_info} питає: {text}")
    await update.message.reply_text(res.text)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_info = context.user_data.get('user_info', "Мандрівник")
    if context.user_data.get('vip'):
        await update.message.reply_text("🔮 Я бачу твій відбиток...")
        res = model.generate_content(f"Ти Всесвіт. Проаналізуй долоню користувача {user_info} і дай пророцтво.")
        await update.message.reply_text(res.text)
    else:
        await update.message.reply_text("🔮 Твоя доля закрита. Скористайся кнопкою 'Відбиток долі', щоб внести 200 ⭐.")

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(PreCheckoutQueryHandler(lambda u, c: u.pre_checkout_query.answer(ok=True)))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(drop_pending_updates=True)
