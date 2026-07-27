import asyncio
import os
import json
import subprocess
import sys
import requests
import urllib.parse
from datetime import datetime, timedelta
from telethon import TelegramClient, events, errors
from telethon.tl.functions.messages import DeleteHistoryRequest
from gtts import gTTS

# ---------- НАСТРОЙКИ ----------
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
CONFIG_PATH = "/storage/emulated/0/userbot_config.json"
LOG_PATH = "/storage/emulated/0/userbot_log.txt"
# --------------------------------

def log(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")

def ensure_mistral():
    try:
        from mistralai import Mistral
        return True
    except ImportError:
        subprocess.run([sys.executable or "python3", "-m", "pip", "install", "mistralai"], capture_output=True)
        try:
            from mistralai import Mistral
            return True
        except ImportError:
            return False

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def save_config(key):
    config = load_config()
    config["mistral_key"] = key
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

config = load_config()
MISTRAL_KEY = config.get("mistral_key", "")
PHONE = config.get("phone", "")
CODE = config.get("code", "")
PASSWORD = config.get("password", "")

muted_users = {}
warn_limits = {}

client = TelegramClient('/storage/emulated/0/userbot_session', API_ID, API_HASH)

# === .help ===
@client.on(events.NewMessage(pattern=r'\.help'))
async def help_cmd(event):
    await event.delete()
    help_text = """
<b>Команды:</b>

<b>Текст и голос:</b>
  <code>.txt текст</code> — анимированная печать
  <code>.voice текст</code> — голосовое сообщение
  <code>.timer N текст</code> — исчезающее сообщение
  <code>.mock</code> — ИзДeВкА над текстом

<b>Нейросети:</b>
  <code>.ai вопрос</code> — Mistral AI
  <code>.draw описание</code> — рисует картинку

<b>Инструменты:</b>
  <code>.trans</code> — перевод сообщения
  <code>.qr ссылка</code> — QR-код
  <code>.save</code> — сохранить в Избранное

<b>Модерация:</b>
  <code>.mute N</code> — мут на N минут
  <code>.unmute</code> — снять мут
  <code>.warn N</code> — лимит сообщений
  <code>.unwarn</code> — снять лимит

<b>Очистка:</b>
  <code>.panic</code> — очистить историю
  <code>.del N</code> — удалить через N сек

<b><code>.setup</code> — сменить ключ</b>
"""
    await event.respond(help_text, parse_mode="html")

# === .setup ===
@client.on(events.NewMessage(pattern=r'\.setup'))
async def setup_cmd(event):
    await event.delete()
    msg = await event.respond("Отправь новый Mistral ключ в ответ.")
    try:
        reply = await client.wait_for(event.chat_id, timeout=60)
        if reply.reply_to_msg_id == msg.id:
            new_key = reply.text.strip()
            save_config(new_key)
            global MISTRAL_KEY
            MISTRAL_KEY = new_key
            await reply.delete()
            await msg.edit("Ключ обновлен! ИИ готов.")
    except:
        await msg.edit("Время вышло.")

# === .mute N ===
@client.on(events.NewMessage(pattern=r'\.mute (\d+)'))
async def mute_cmd(event):
    if not event.is_reply:
        await event.respond("Ответьте на сообщение пользователя.")
        return
    minutes = int(event.pattern_match.group(1))
    target = await event.get_reply_message()
    user_id = target.sender_id
    user_name = target.sender.first_name or "Пользователь"
    muted_users[user_id] = datetime.now() + timedelta(minutes=minutes)
    await event.delete()
    msg = await event.respond(f"🔇 {user_name} замучен на {minutes} мин.")
    await asyncio.sleep(minutes * 60)
    if user_id in muted_users and datetime.now() >= muted_users[user_id]:
        del muted_users[user_id]
        try:
            await msg.edit(f"🔊 Мут снят. {user_name} снова может писать.")
        except: pass

# === .unmute ===
@client.on(events.NewMessage(pattern=r'\.unmute'))
async def unmute_cmd(event):
    if not event.is_reply:
        await event.respond("Ответьте на сообщение пользователя.")
        return
    target = await event.get_reply_message()
    user_id = target.sender_id
    if user_id in muted_users:
        del muted_users[user_id]
    await event.delete()
    await event.respond("🔊 Мут снят.")

# === .panic ===
@client.on(events.NewMessage(pattern=r'\.panic'))
async def panic_cmd(event):
    await event.delete()
    status = await event.respond("Зачищаю переписку...")
    count = 0
    async for msg in client.iter_messages(event.chat_id, limit=None):
        try:
            await msg.delete()
            count += 1
        except: pass
    await client(DeleteHistoryRequest(peer=event.chat_id, max_id=0, just_clear=False))
    await status.edit(f"История очищена. Удалено {count} сообщений.")

# === .del N ===
@client.on(events.NewMessage(pattern=r'\.del (\d+)'))
async def del_cmd(event):
    seconds = int(event.pattern_match.group(1))
    await event.delete()
    status = await event.respond(f"Чат очистится через {seconds} сек...")
    for i in range(seconds, 0, -1):
        await asyncio.sleep(1)
        try: await status.edit(f"Чат очистится через {i} сек...")
        except: pass
    count = 0
    async for m in client.iter_messages(event.chat_id, limit=None):
        try:
            await m.delete()
            count += 1
        except: pass
    await client(DeleteHistoryRequest(peer=event.chat_id, max_id=0, just_clear=False))
    await event.respond(f"Чат очищен. Удалено {count} сообщений.")

# === .txt текст ===
@client.on(events.NewMessage(pattern=r'\.txt (.+)'))
async def txt_cmd(event):
    text = event.pattern_match.group(1)
    await event.delete()
    msg = await event.respond("▌")
    displayed = ""
    for char in text:
        displayed += char
        await asyncio.sleep(0.05)
        try: await msg.edit(displayed + "▌")
        except: pass
    await msg.edit(displayed)

# === .warn N ===
@client.on(events.NewMessage(pattern=r'\.warn (\d+)'))
async def warn_cmd(event):
    if not event.is_reply:
        await event.respond("Ответьте на сообщение пользователя.")
        return
    limit = min(int(event.pattern_match.group(1)), 100)
    target = await event.get_reply_message()
    user_id = target.sender_id
    msg = await event.respond(f"⚠️ Предупреждение [0/{limit}]")
    warn_limits[user_id] = {"limit": limit, "count": 0, "msg_id": msg.id}
    await event.delete()

# === .unwarn ===
@client.on(events.NewMessage(pattern=r'\.unwarn'))
async def unwarn_cmd(event):
    if not event.is_reply:
        await event.respond("Ответьте на сообщение пользователя.")
        return
    target = await event.get_reply_message()
    user_id = target.sender_id
    if user_id in warn_limits:
        try:
            old_msg = await event.client.get_messages(event.chat_id, ids=warn_limits[user_id]["msg_id"])
            await old_msg.delete()
        except: pass
        del warn_limits[user_id]
    if user_id in muted_users:
        del muted_users[user_id]
    await event.delete()
    await event.respond("Варн снят.")

# === .voice текст ===
@client.on(events.NewMessage(pattern=r'\.voice (.+)'))
async def voice_cmd(event):
    text = event.pattern_match.group(1)
    await event.delete()
    status = await event.respond("Генерирую голосовое...")
    try:
        tts = gTTS(text, lang='ru')
        path = f"/tmp/voice_{event.sender_id}.mp3"
        tts.save(path)
        await client.send_file(event.chat_id, path, voice_note=True)
        await status.delete()
        os.remove(path)
    except Exception as e:
        await status.edit(f"Ошибка: {e}")

# === .ai текст ===
@client.on(events.NewMessage(pattern=r'\.ai (.+)'))
async def ai_cmd(event):
    if not MISTRAL_KEY:
        await event.respond("ИИ отключен. Получи ключ на console.mistral.ai и введи через .setup")
        return
    question = event.pattern_match.group(1)
    await event.delete()
    status = await event.respond("Думаю...")
    if not ensure_mistral():
        await status.edit("Не удалось установить ИИ.")
        return
    try:
        from mistralai import Mistral
        client_ai = Mistral(api_key=MISTRAL_KEY)
        response = client_ai.chat.complete(
            model="mistral-large-latest",
            messages=[{"role": "user", "content": question}]
        )
        answer = response.choices[0].message.content
        await status.edit(f"{answer}")
    except Exception as e:
        await status.edit(f"Ошибка: {e}")

# === .draw описание ===
@client.on(events.NewMessage(pattern=r'\.draw (.+)'))
async def draw_cmd(event):
    prompt = event.pattern_match.group(1)
    await event.delete()
    status = await event.respond("Рисую...")
    try:
        from deep_translator import GoogleTranslator
        if any('а' <= c <= 'я' or 'А' <= c <= 'Я' for c in prompt):
            prompt = GoogleTranslator(source="auto", target="en").translate(prompt)
        prompt_encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=512&height=512&nologo=true"
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            await status.edit("Сервер не ответил.")
            return
        path = f"/tmp/draw_{event.sender_id}.jpg"
        with open(path, "wb") as f:
            f.write(response.content)
        await client.send_file(event.chat_id, path, caption=f"{prompt}")
        await status.delete()
        os.remove(path)
    except Exception as e:
        await status.edit(f"Ошибка: {e}")

# === .trans ===
@client.on(events.NewMessage(pattern=r'\.trans(?: (\w+))?'))
async def trans_cmd(event):
    target_lang = event.pattern_match.group(1) or "ru"
    if not event.is_reply:
        await event.respond("Ответьте на сообщение для перевода.")
        return
    reply = await event.get_reply_message()
    if not reply.text:
        await event.respond("Только текст.")
        return
    await event.delete()
    status = await event.respond("Перевожу...")
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source="auto", target=target_lang).translate(reply.text)
        await status.edit(f"[{target_lang}] {translated}")
    except Exception as e:
        await status.edit(f"Ошибка: {e}")

# === .save ===
@client.on(events.NewMessage(pattern=r'\.save'))
async def save_cmd(event):
    if not event.is_reply:
        await event.respond("Ответьте на сообщение для сохранения.")
        return
    reply = await event.get_reply_message()
    await event.delete()
    try:
        me = await client.get_me()
        await client.forward_messages(me.id, reply)
        await event.respond("Сохранено в Избранное.")
    except:
        await event.respond("Ошибка сохранения.")

# === .timer N текст ===
@client.on(events.NewMessage(pattern=r'\.timer (\d+) (.+)'))
async def timer_cmd(event):
    seconds = int(event.pattern_match.group(1))
    text = event.pattern_match.group(2)
    await event.delete()
    msg = await event.respond(f"⏳ {text}")
    await asyncio.sleep(seconds)
    await msg.delete()

# === .mock ===
@client.on(events.NewMessage(pattern=r'\.mock'))
async def mock_cmd(event):
    if not event.is_reply:
        await event.respond("Ответьте на сообщение.")
        return
    reply = await event.get_reply_message()
    if not reply.text:
        await event.respond("Только текст.")
        return
    await event.delete()
    result = ""
    upper = True
    for char in reply.text:
        if char.isalpha():
            result += char.upper() if upper else char.lower()
            upper = not upper
        else:
            result += char
    await event.respond(result)

# === .qr ссылка ===
@client.on(events.NewMessage(pattern=r'\.qr (.+)'))
async def qr_cmd(event):
    text = event.pattern_match.group(1)
    await event.delete()
    status = await event.respond("Генерирую QR-код...")
    try:
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={text}"
        response = requests.get(url)
        path = f"/tmp/qr_{event.sender_id}.png"
        with open(path, "wb") as f: f.write(response.content)
        await client.send_file(event.chat_id, path, caption=f"QR: {text}")
        await status.delete()
        os.remove(path)
    except Exception as e:
        await status.edit(f"Ошибка: {e}")

# === Автоматическая обработка ===
@client.on(events.NewMessage(incoming=True))
async def check_restrictions(event):
    if event.sender_id in muted_users:
        if datetime.now() < muted_users[event.sender_id]:
            await event.delete()
            return
        else:
            del muted_users[event.sender_id]
    if event.sender_id in warn_limits:
        w = warn_limits[event.sender_id]
        w["count"] += 1
        try:
            old_msg = await event.client.get_messages(event.chat_id, ids=w["msg_id"])
            await old_msg.edit(f"⚠️ Предупреждение [{w['count']}/{w['limit']}]")
        except: pass
        if w["count"] >= w["limit"]:
            muted_users[event.sender_id] = datetime.now() + timedelta(hours=1)
            try:
                old_msg = await event.client.get_messages(event.chat_id, ids=w["msg_id"])
                await old_msg.edit(f"Автомут! Лимит {w['limit']} сообщений превышен.")
            except: pass
            del warn_limits[event.sender_id]

# === ЗАПУСК ===
async def main():
    log("Запуск бота...")
    
    code_from_app = CODE
    
    async def code_callback():
        return code_from_app
    
    try:
        await client.start(phone=PHONE, code_callback=code_callback)
        log("Вход выполнен!")
    except errors.SessionPasswordNeededError:
        log("Нужен облачный пароль, вхожу...")
        await client.sign_in(password=PASSWORD)
        log("Вход по паролю!")
    except Exception as e:
        log(f"Ошибка входа: {e}")
        sys.exit(1)
    
    me = await client.get_me()
    log(f"Вошли как: {me.first_name}")
    log("Бот готов к работе!")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
