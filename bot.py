import os
import telebot
import random
from pathlib import Path
from telebot import types
from flask import Flask, request   # Flask для webhook

# =========================================
# 🔥 TOKEN из Railway
# =========================================
TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = 5540959332

if not TOKEN or ":" not in TOKEN:
    print("❌ TOKEN не найден или неправильный")
    exit()

bot = telebot.TeleBot(TOKEN)
print("🔥 ST1F Mus!c BOT стартует...")

# =========================================
# ⚙️ Пути
# =========================================
BASE_DIR = Path("beats")
DRUMS_DIR = Path("drums")
OWNER_LINK = "https://t.me/stif_king"

# =========================================
# 🎵 Утилиты
# =========================================
def get_random_file(folder: Path):
    if not folder.exists():
        return None
    files = list(folder.glob("*.*"))
    if not files:
        return None
    return random.choice(files)

def log_download(user, action, file=None):
    name = user.first_name
    username = user.username if user.username else "нет_юзернейма"
    fname = file if file else "-"
    msg = f"📥 {name} (@{username}) — {action} — {fname}"
    try:
        bot.send_message(ADMIN_CHAT_ID, msg)
    except Exception as e:
        print("❌ Не удалось отправить лог админу:", repr(e))

def send_random_from(folder: Path, message, caption, action="genre"):
    file = get_random_file(folder)
    if not file:
        bot.reply_to(message, "❌ Файлы не найдены в папке")
        return
    bot.send_audio(message.chat.id, open(file, "rb"), caption=caption)
    log_download(message.from_user, action, file.name)

# =========================================
# 📝 GENRE MAP
# =========================================
GENRE_MAP = {
    "cinematic_epic": BASE_DIR / "cinematic" / "epic",
    "cinematic_sad": BASE_DIR / "cinematic" / "sad",
    "drill_aggressive": BASE_DIR / "drill" / "aggressive",
    "drill_melodic": BASE_DIR / "drill" / "melodic",
    "hiphop_boombap": BASE_DIR / "hip-hop" / "boombap",
    "hiphop_oldschool": BASE_DIR / "hip-hop" / "oldschool",
    "lofi_relax": BASE_DIR / "lofi" / "relax",
    "lofi_study": BASE_DIR / "lofi" / "study",
    "phonk_dark": BASE_DIR / "phonk" / "dark",
    "phonk_drift": BASE_DIR / "phonk" / "drift",
    "phonk_memphis": BASE_DIR / "phonk" / "memphis",
    "soul_emotional": BASE_DIR / "soul" / "emotional",
    "soul_smooth": BASE_DIR / "soul" / "smooth",
    "trap_chill": BASE_DIR / "trap" / "chill",
    "trap_dark": BASE_DIR / "trap" / "dark",
    "trap_hard": BASE_DIR / "trap" / "hard",
}

# =========================================
# 🚀 START с кнопками
# =========================================
@bot.message_handler(commands=["start"])
def start(message):
    text = "🎛 ST1F Mus!c Beat Store\nВыбери действие:"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🎵 Жанры", callback_data="genres"),
        types.InlineKeyboardButton("🎲 Случайный бит", callback_data="randombeat"),
        types.InlineKeyboardButton("💰 Прайс", callback_data="price"),
        types.InlineKeyboardButton("🥁 Drums Pack", callback_data="drums"),
        types.InlineKeyboardButton("💡 Идеи / Тексты", callback_data="lyrics"),
        types.InlineKeyboardButton("📞 Контакты", callback_data="contact")
    )
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# =========================================
# 🎹 ОБРАБОТКА КНОПОК
# =========================================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "genres":
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for cmd in GENRE_MAP.keys():
            keyboard.add(types.InlineKeyboardButton(cmd.replace("_"," ").title(), callback_data=cmd))
        bot.send_message(call.message.chat.id, "🎵 Выберите жанр / настроение:", reply_markup=keyboard)

    elif call.data in GENRE_MAP:
        send_random_from(GENRE_MAP[call.data], call.message, f"🎧 {call.data.replace('_',' ').title()}", action=call.data)

    elif call.data == "randombeat":
        all_files = list(BASE_DIR.rglob("*.*"))
        if not all_files:
            bot.reply_to(call.message, "❌ Нет битов")
            return
        file = random.choice(all_files)
        bot.send_audio(call.message.chat.id, open(file, "rb"), caption="🎲 Случайный бит")
        log_download(call.from_user, "randombeat", file.name)

    elif call.data == "price":
        text = f"""
💰 Прайс за биты:

25$ — MP3
100$ — WAV

Покупка:
👉 {OWNER_LINK}
"""
        bot.send_message(call.message.chat.id, text)

    elif call.data == "drums":
        file = get_random_file(DRUMS_DIR)
        if not file:
            bot.reply_to(call.message, "❌ Drumkit не найден")
            return
        bot.send_document(call.message.chat.id, open(file, "rb"), caption=f"🥁 Drumkit — 50$\n👉 {OWNER_LINK}")
        log_download(call.from_user, "drums", file.name)

    elif call.data == "lyrics":
        text = """
🎵 Идеи / Тексты для треков:

1. Moody trap с глубоким басом
2. Epic cinematic для интро
3. Phonk Memphis vibe
4. LoFi chill для стримов
5. Drill aggressive punchlines
"""
        bot.send_message(call.message.chat.id, text)
        log_download(call.from_user, "lyrics")

    elif call.data == "contact":
        bot.send_message(call.message.chat.id, f"Напиши сюда:\n👉 {OWNER_LINK}")

# =========================================
# 🚀 RUN через webhook
# =========================================
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.stream.read().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    url = os.getenv("RAILWAY_URL")  # например https://st1fbot-production.up.railway.app
    bot.remove_webhook()
    bot.set_webhook(url + "/" + TOKEN)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))