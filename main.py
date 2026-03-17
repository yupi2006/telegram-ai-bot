import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

TOKEN = os.getenv("8790861166:AAFV_Ia6ouyUgeFYqOmpQ0kk_T5ZQuzteDE")
OPENROUTER_API_KEY = os.getenv("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")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

user_state = {}

ROLES = ["👔 Директор", "💬 Друг", "❤️ Близкий человек", "💼 Клиент", "👨‍👩‍👧 Родители"]
TONES = ["🙂 Мягко", "💪 Уверенно", "✅ Чтобы согласились", "❤️ Тепло", "🤝 Вежливо"]


def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if keyboard:
        data["reply_markup"] = keyboard

    requests.post(f"{BASE_URL}/sendMessage", json=data)


def get_keyboard(options):
    return {
        "keyboard": [[{"text": x}] for x in options],
        "resize_keyboard": True
    }


def ai_generate(role, tone, text):
    prompt = f"""
Перепиши сообщение под ситуацию.

Кому: {role}
Тон: {tone}
Текст: {text}

Дай 3 варианта, коротко, по делу, по-человечески.
Формат:
1. ...
2. ...
3. ...
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://example.com",
            "X-Title": "Telegram AI Bot"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    return response.json()["choices"][0]["message"]["content"]


@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()

    if "message" not in data:
        return {"ok": True}

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")

    if user_id not in user_state:
        user_state[user_id] = {}

    if text == "/start":
        user_state[user_id] = {}
        send_message(chat_id, "Кому ты пишешь?", get_keyboard(ROLES))
        return {"ok": True}

    if text in ROLES:
        user_state[user_id]["role"] = text
        send_message(chat_id, "Какой тон?", get_keyboard(TONES))
        return {"ok": True}

    if text in TONES:
        user_state[user_id]["tone"] = text
        send_message(chat_id, "Отправь текст")
        return {"ok": True}

    role = user_state[user_id].get("role")
    tone = user_state[user_id].get("tone")

    if not role:
        send_message(chat_id, "Сначала выбери кому пишешь", get_keyboard(ROLES))
        return {"ok": True}

    if not tone:
        send_message(chat_id, "Теперь выбери тон", get_keyboard(TONES))
        return {"ok": True}

    result = ai_generate(role, tone, text)
    send_message(chat_id, f"Вот варианты:\n\n{result}")

    return {"ok": True}


@app.get("/")
def home():
    return {"status": "ok"}
