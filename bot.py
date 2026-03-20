import os
import random
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# НАСТРОЙКИ
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

if not BOT_TOKEN:
    raise ValueError("Не задан BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app_flask = Flask(__name__)

# =========================
# БАЗА ИДЕЙ
# =========================
coin_names = [
    "Donald Dump", "Rugzilla", "Moon Hamster X", "Exit Liquidity Pro",
    "Doge Bankruptcy", "Pepe Dividend", "Chart Killer", "Pump Funeral",
    "Zero Hero", "Scamurai", "Dump Daddy", "Bear President",
]

tickers = [
    "DUMP", "RUG", "MHX", "EXIT", "BANK", "KILL",
    "ZERO", "MOON", "COPE", "FOMO", "NGMI", "REKT",
]

descriptions = [
    "The only coin built to dump with style.",
    "A premium meme coin for maximum chaos.",
    "Born to trend, designed to confuse.",
    "Luxury-level meme energy with zero shame.",
    "For legends, degens and future bagholders.",
    "Not financial advice. Pure entertainment.",
]

slogans = [
    "Built To Dump",
    "Nobody Dumps Better",
    "Make Charts Dump Again",
    "Born To Rug",
    "Moon Or Zero",
    "Luxury Scam Energy",
    "Pump Is Temporary, Meme Is Forever",
]

meme_scenes = [
    "Трейдер радостно заходит в токен, через секунду график летит вниз.",
    "Разработчик в очках обещает луну, а на фоне уже горит график.",
    "Парень говорит 'я зашёл на дне', а дно оказывается только началом.",
    "Чат кричит GM, а на графике минус 87%.",
]

meme_top_texts = [
    "I'M EARLY BRO",
    "THIS ONE IS DIFFERENT",
    "EASY 100X",
    "STRONG COMMUNITY",
]

meme_bottom_texts = [
    "5 minutes before the dump",
    "chart says otherwise",
    "liquidity has left the chat",
    "straight to zero",
]

x_post_templates = [
    "$TICKER is not here to pump.\nIt is here to make chart history.\n#memecoin #crypto",
    "Meet $TICKER — a premium meme coin with luxury dump technology.\nBuilt different. Built wrong.",
    "$TICKER is for those who missed DOGE, missed PEPE, and still learned nothing.",
]

tg_post_templates = [
    "🚀 Новый мемкоин: $NAME\n\nTicker: $TICKER\nСлоган: $SLOGAN\n\nГотовы делать историю или хотя бы мемы?",
    "🔥 Встречайте $NAME\n\n$DESC\n\nTicker: $TICKER\n#memecoin #telegram",
    "💥 $NAME уже здесь\n\n$DESC\n\nСлоган дня: $SLOGAN",
]

telegram_app = Application.builder().token(BOT_TOKEN).build()

# =========================
# ГЕНЕРАТОРЫ
# =========================
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
    top = random.choice(meme_top_texts)
    bottom = random.choice(meme_bottom_texts)

    return (
        f"😂 <b>Идея для мема</b>\n\n"
        f"🎬 <b>Сцена:</b> {scene}\n"
        f"⬆️ <b>Текст сверху:</b> {top}\n"
        f"⬇️ <b>Текст снизу:</b> {bottom}"
    )

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

def generate_launch_pack_text() -> str:
    name = random.choice(coin_names)
    ticker = random.choice(tickers)
    desc = random.choice(descriptions)
    selected_slogans = random.sample(slogans, 3)
    tweet_1 = random.choice(x_post_templates).replace("$TICKER", ticker)
    tweet_2 = random.choice(x_post_templates).replace("$TICKER", ticker)
    meme_scene = random.choice(meme_scenes)

    return (
        f"🔥 <b>Пак запуска</b>\n\n"
        f"🪙 <b>Название:</b> {name}\n"
        f"💠 <b>Тикер:</b> ${ticker}\n"
        f"📜 <b>Описание:</b> {desc}\n\n"
        f"💬 <b>3 слогана:</b>\n"
        f"— {selected_slogans[0]}\n"
        f"— {selected_slogans[1]}\n"
        f"— {selected_slogans[2]}\n\n"
        f"📣 <b>2 поста для X:</b>\n"
        f"1. {tweet_1}\n\n"
        f"2. {tweet_2}\n\n"
        f"😂 <b>Идея мема:</b>\n"
        f"{meme_scene}"
    )

def main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🚀 Сгенерировать токен", callback_data="gen_token")],
        [InlineKeyboardButton("😂 Идея для мема", callback_data="gen_meme")],
        [InlineKeyboardButton("📣 Пост для X", callback_data="gen_x")],
        [InlineKeyboardButton("📱 Пост для Telegram", callback_data="gen_tg")],
        [InlineKeyboardButton("🔥 Пак запуска", callback_data="gen_pack")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🔥 <b>Добро пожаловать в RUG FACTORY</b>\n\n"
        "Здесь рождаются лучшие худшие мемкоины интернета.\n\n"
        "Выбирай, что генерировать:"
    )
    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=main_menu(),
            parse_mode="HTML",
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    if query.data == "gen_token":
        text = generate_token_text()
    elif query.data == "gen_meme":
        text = generate_meme_idea_text()
    elif query.data == "gen_x":
        text = generate_x_post_text()
    elif query.data == "gen_tg":
        text = generate_tg_post_text()
    elif query.data == "gen_pack":
        text = generate_launch_pack_text()
    else:
        text = "Что-то пошло не так."

    await query.message.reply_text(
        text,
        reply_markup=main_menu(),
        parse_mode="HTML",
    )

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

@app_flask.route("/")
def health():
    return "Bot is running"

@app_flask.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

async def setup():
    await telegram_app.initialize()
    await telegram_app.start()

    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"
        await telegram_app.bot.set_webhook(webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
    else:
        logger.warning("RENDER_EXTERNAL_URL не задан")

import asyncio
asyncio.get_event_loop().run_until_complete(setup())

if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app_flask.run(host="0.0.0.0", port=port)
