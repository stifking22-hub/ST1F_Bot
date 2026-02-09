import os
import telebot
import random
from pathlib import Path

# =========================================
# 🔥 TOKEN из Railway
# =========================================
TOKEN = os.getenv("TOKEN")

if not TOKEN or ":" not in TOKEN:
    print("❌ TOKEN не найден или неправильный")
    exit()

bot = telebot.TeleBot(TOKEN)

print("🔥 ST1F Mus!c BOT запущен и готов к работе!")

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


def send_random_from(folder, message, caption):
    file = get_random_file(folder)

    if not file:
        bot.reply_to(message, "❌ Биты не найдены в папке")
        return

    with open(file, "rb") as f:
        bot.send_audio(
            message.chat.id,
            f,
            caption=caption
        )


# =========================================
# 🚀 START
# =========================================
@bot.message_handler(commands=["start"])
def start(message):
    text = """
🎛 ST1F Mus!c Beat Store

Добро пожаловать!

/genres — жанры
/randombeat — случайный бит
/price — прайс
/drumkit — драм пак
/contact — купить
"""
    bot.send_message(message.chat.id, text)


# =========================================
# 🎼 GENRES
# =========================================
@bot.message_handler(commands=["genres"])
def genres(message):
    text = """
🎵 Жанры:

/cinematic_epic
/cinematic_sad

/drill_aggressive
/drill_melodic

/hiphop_boombap
/hiphop_oldschool

/lofi_relax
/lofi_study

/phonk_dark
/phonk_drift
/phonk_memphis

/soul_emotional
/soul_smooth

/trap_chill
/trap_dark
/trap_hard
"""
    bot.send_message(message.chat.id, text)


# =========================================
# 🎲 RANDOM
# =========================================
@bot.message_handler(commands=["randombeat"])
def randombeat(message):
    all_files = list(BASE_DIR.rglob("*.*"))

    if not all_files:
        bot.reply_to(message, "❌ Нет битов")
        return

    file = random.choice(all_files)

    with open(file, "rb") as f:
        bot.send_audio(message.chat.id, f, caption="🎲 Случайный бит")


# =========================================
# 💰 PRICE
# =========================================
@bot.message_handler(commands=["price"])
def price(message):
    text = f"""
💰 Прайс:

25$ — MP3 lease
100$ — WAV exclusive

Покупка:
👉 {OWNER_LINK}
"""
    bot.send_message(message.chat.id, text)


# =========================================
# 🥁 DRUMKIT
# =========================================
@bot.message_handler(commands=["drumkit"])
def drumkit(message):
    file = get_random_file(DRUMS_DIR)

    if not file:
        bot.reply_to(message, "❌ Drumkit не найден")
        return

    with open(file, "rb") as f:
        bot.send_document(
            message.chat.id,
            f,
            caption=f"🥁 Drumkit — 50$\n👉 {OWNER_LINK}"
        )


# =========================================
# 📞 CONTACT
# =========================================
@bot.message_handler(commands=["contact"])
def contact(message):
    bot.send_message(message.chat.id, f"Напиши сюда:\n👉 {OWNER_LINK}")


# =========================================
# 🎵 Автогенерация команд жанров
# =========================================
GENRE_MAP = {
    "cinematic_epic": "beats/Cinematic/Epic",
    "cinematic_sad": "beats/Cinematic/Sad",

    "drill_aggressive": "beats/Drill/Aggressive",
    "drill_melodic": "beats/Drill/Melodic",

    "hiphop_boombap": "beats/Hip-Hop/BoomBap",
    "hiphop_oldschool": "beats/Hip-Hop/OldSchool",

    "lofi_relax": "beats/LoFi/Relax",
    "lofi_study": "beats/LoFi/Study",

    "phonk_dark": "beats/Phonk/Dark",
    "phonk_drift": "beats/Phonk/Drift",
    "phonk_memphis": "beats/Phonk/Memphis",

    "soul_emotional": "beats/Soul/Emotional",
    "soul_smooth": "beats/Soul/Smooth",

    "trap_chill": "beats/Trap/Chill",
    "trap_dark": "beats/Trap/Dark",
    "trap_hard": "beats/Trap/Hard",
}


for cmd, path in GENRE_MAP.items():
    def make_handler(p):
        return lambda m: send_random_from(Path(p), m, f"🎧 {cmd}")

    bot.message_handler(commands=[cmd])(make_handler(path))


# =========================================
# 🚀 RUN
# =========================================
bot.infinity_polling(skip_pending=True)