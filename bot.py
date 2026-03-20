import os
import random
import logging
import asyncio

from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").replace("@", "")

if not BOT_TOKEN:
    raise ValueError("Не задан BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app_flask = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

FREE_LIMIT = 3
user_limits = {}

coin_names = [
    "Donald Dump", "Rugzilla", "Moon Hamster X", "Exit Liquidity Pro",
    "Doge Bankruptcy", "Pepe Dividend", "Chart Killer", "Pump Funeral"
]

tickers = ["DUMP", "RUG", "MHX", "EXIT", "BANK", "KILL", "ZERO", "MOON"]

descriptions = [
    "The only coin built to dump with style.",
    "A premium meme coin for maximum chaos.",
    "Born to trend, designed to confuse.",
    "Luxury-level meme energy with zero shame.",
]

slogans = [
    "Built To Dump",
    "Nobody Dumps Better",
    "Make Charts Dump Again",
    "Born To Rug",
    "Moon Or Zero",
]

meme_scenes = [
    "Трейдер радостно заходит в токен, через секунду график летит вниз.",
    "Разработчик в очках обещает луну, а на фоне уже горит график.",
    "Чат кричит GM, а на графике минус 87%.",
]

x_post_templates = [
    "$TICKER is not here to pump.\nIt is here to make chart history.",
    "Meet $TICKER — a premium meme coin with luxury dump technology.",
    "$TICKER is for those who missed DOGE and still learned nothing.",
]

tg_post_templates = [
    "🚀 Новый мемкоин: $NAME\n\nTicker: $TICKER\nСлоган: $SLOGAN",
    "🔥 Встречайте $NAME\n\n$DESC\n\nTicker: $TICKER",
    "💥 $NAME уже здесь\n\n$DESC\n\nСлоган дня: $SLOGAN",
]


def get_limit(user_id: int) -> int:
    if user_id not in user_limits:
        user_limits[user_id] = FREE_LIMIT
    return user_limits[user_id]


def consume_limit(user_id: int) -> bool:
    if user_id not in user_limits:
        user_limits[user_id] = FREE_LIMIT
    if user_limits[user_id] <= 0:
        return False
    user_limits[user_id] -= 1
    return True


def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🚀 Сгенерировать токен", callback_data="gen_token")],
        [InlineKeyboardButton("😂 Идея для мема", callback_data="gen_meme")],
        [InlineKeyboardButton("📣 Пост для X", callback_data="gen_x")],
        [InlineKeyboardButton("📱 Пост для Telegram", callback_data="gen_tg")],
        [InlineKeyboardButton("⭐ Купить доступ", callback_data="buy")],
    ]
    return InlineKeyboardMarkup(keyboard)


def generate_token_text() -> str:
    name = random.choice(coin_names)
    ticker = random.choice(tickers)
    desc = random.choice(descriptions)
    selected_slogans = random.sample(slogans, 3)

    return (
        f"🪙 <b>Название:</b> {name}\n"
        f"💠 <b>Тикер:</b> ${ticker}\n"
        f"📜 <b>Описание:</b> {desc}\n\n"
        f"💬 <b>Слоганы:</b>\n"
        f"— {selected_slogans[0]}\n"
        f"— {selected_slogans[1]}\n"
        f"— {selected_slogans[2]}"
    )


def generate_meme_idea_text() -> str:
    scene = random.choice(meme_scenes)
    return f"😂 <b>Идея для мема</b>\n\n🎬 <b>Сцена:</b> {scene}"


def generate_x_post_text() -> str:
    ticker = random.choice(tickers)
    template = random.choice(x_post_templates)
    return "📣 <b>Пост для X</b>\n\n" + template.replace("$TICKER", ticker)


def generate_tg_post_text() -> str:
    name = random.choice(coin_names)
    ticker = random.choice(tickers)
    desc = random.choice(descriptions)
    slogan = random.choice(slogans)
    template = random.choice(tg_post_templates)

    text = (
        template
        .replace("$NAME", name)
        .replace("$TICKER", ticker)
        .replace("$DESC", desc)
        .replace("$SLOGAN", slogan)
    )
    return f"📱 <b>Пост для Telegram</b>\n\n{text}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    left = get_limit(user_id)

    text = (
        "🔥 <b>Добро пожаловать в RUG FACTORY</b>\n\n"
        "Бесплатно доступно 3 генерации.\n"
        f"Осталось: {left}\n\n"
        "Выбирай, что генерировать:"
    )
    await update.message.reply_text(text, reply_markup=main_menu(), parse_mode="HTML")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "buy":
        admin_text = f"@{ADMIN_USERNAME}" if ADMIN_USERNAME else "админу"
        await query.message.reply_text(
            f"⭐ Для доступа напиши {admin_text}",
            parse_mode="HTML",
        )
        return

    if query.data in ["gen_token", "gen_meme", "gen_x", "gen_tg"]:
        if not consume_limit(user_id):
            admin_text = f"@{ADMIN_USERNAME}" if ADMIN_USERNAME else "админу"
            await query.message.reply_text(
                f"❌ Бесплатный лимит закончился.\n\nНапиши {admin_text} для доступа.",
                reply_markup=main_menu(),
                parse_mode="HTML",
            )
            return

        if query.data == "gen_token":
            text = generate_token_text()
        elif query.data == "gen_meme":
            text = generate_meme_idea_text()
        elif query.data == "gen_x":
            text = generate_x_post_text()
        else:
            text = generate_tg_post_text()

        left = get_limit(user_id)
        await query.message.reply_text(
            f"{text}\n\n📊 Осталось бесплатно: {left}",
            reply_markup=main_menu(),
            parse_mode="HTML",
        )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))


@app_flask.route("/", methods=["GET"])
def health():
    return "Bot is running", 200


@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    async def process():
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)

    asyncio.run(process())
    return "ok", 200


async def telegram_setup():
    await telegram_app.initialize()
    await telegram_app.start()

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
        await telegram_app.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")


asyncio.run(telegram_setup())

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app_flask.run(host="0.0.0.0", port=port)
