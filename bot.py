import os
import random
import logging
import asyncio

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ВСТАВЬ СВОЙ URL
RENDER_EXTERNAL_URL = "https://telegram-ai-bot-dd6t.onrender.com"

# ВСТАВЬ СВОЙ НИК БЕЗ @
ADMIN_USERNAME = "Photomasteredit"

if not BOT_TOKEN:
    raise ValueError("Не задан BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app_flask = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

FREE_LIMIT = 3
user_limits = {}

coin_names = ["Donald Dump","Rugzilla","Moon Hamster X","Exit Liquidity Pro","Scamurai"]
tickers = ["DUMP","RUG","MHX","EXIT","FOMO"]
descriptions = ["Built to dump.","Luxury meme chaos.","Pure degen energy."]
slogans = ["Built To Dump","Nobody Dumps Better","Moon Or Zero"]

def get_limit(user_id):
    if user_id not in user_limits:
        user_limits[user_id] = FREE_LIMIT
    return user_limits[user_id]

def consume_limit(user_id):
    if user_limits.get(user_id, FREE_LIMIT) <= 0:
        return False
    user_limits[user_id] = user_limits.get(user_id, FREE_LIMIT) - 1
    return True

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Сгенерировать токен", callback_data="token")],
        [InlineKeyboardButton("😂 Идея для мема", callback_data="meme")],
        [InlineKeyboardButton("📣 Пост для X", callback_data="x")],
        [InlineKeyboardButton("📱 Пост для Telegram", callback_data="tg")],
        [InlineKeyboardButton("🔥 Пак запуска", callback_data="pack")],
        [InlineKeyboardButton("⭐ Купить доступ", callback_data="buy")],
    ])

def gen_token():
    return f"🪙 {random.choice(coin_names)}\n💠 ${random.choice(tickers)}\n📜 {random.choice(descriptions)}"

def gen_meme():
    return "😂 Трейдер купил → сразу -80%"

def gen_x():
    return f"$ {random.choice(tickers)} is not here to pump.\nIt is here to dump."

def gen_tg():
    return f"🚀 Новый токен: {random.choice(coin_names)}"

def gen_pack():
    return "🔥 Пак запуска:\nНазвание + посты + идея мема"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    left = get_limit(user_id)

    await update.message.reply_text(
        f"🔥 Добро пожаловать в RUG FACTORY\n\nБесплатно: {left}\n\nВыбирай:",
        reply_markup=menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id

    if q.data == "buy":
        await q.message.reply_text(
            f"🔥 Хочешь без лимита?\nНапиши @{ADMIN_USERNAME}"
        )
        return

    if not consume_limit(user_id):
        await q.message.reply_text(
            f"❌ Бесплатный лимит закончился.\n\n🔥 Хочешь без лимита?\nНапиши @{ADMIN_USERNAME}",
            reply_markup=menu()
        )
        return

    if q.data == "token":
        text = gen_token()
    elif q.data == "meme":
        text = gen_meme()
    elif q.data == "x":
        text = gen_x()
    elif q.data == "tg":
        text = gen_tg()
    else:
        text = gen_pack()

    await q.message.reply_text(
        f"{text}\n\nОсталось: {get_limit(user_id)}",
        reply_markup=menu()
    )

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(buttons))

@app_flask.route("/", methods=["GET"])
def home():
    return "ok"

@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    async def process():
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)

    asyncio.run(process())
    return "ok"

async def setup():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}")

asyncio.run(setup())

if __name__ == "__main__":
    app_flask.run(host="0.0.0.0", port=10000)
