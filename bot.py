import telebot
from telebot import types
import os
import random
import zipfile
from datetime import datetime

TOKEN = "8140147029:AAHfv5dKYaEmEtD4HU1D7lLxcKBsxKOQXVM"

bot = telebot.TeleBot(TOKEN)

user_state = {}
known_users = set()


# ================= ЛОГИ =================
def log(user, action):
    os.makedirs("logs", exist_ok=True)

    username = user.username if user.username else "no_username"
    time = datetime.now().strftime("%d.%m %H:%M")

    with open("logs/orders.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time}] @{username} ({user.id}) -> {action}\n")


# ================= МЕНЮ =================
def main_menu(chat_id):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("🎧 Нужен бит")
    kb.row("📦 Пак битов")
    kb.row("✍️ Текст / идеи")
    kb.row("💰 Прайс", "📩 Контакты")

    bot.send_message(chat_id, "Выбери действие:", reply_markup=kb)


# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    user = msg.from_user

    if user.id not in known_users:
        known_users.add(user.id)

        bot.send_message(
            msg.chat.id,
            f"Добро пожаловать, {user.first_name} 🔥\n"
            "ST1F Music Bot на связи.\n"
            "Подберу биты, тексты и драм-паки."
        )

        log(user, "New user joined")

    main_menu(msg.chat.id)


# ================= ТЕКСТОВЫЕ КОМАНДЫ =================
@bot.message_handler(func=lambda m: True)
def handle(msg):
    text = msg.text.lower()
    chat_id = msg.chat.id

    if "бит" in text:
        send_genres(chat_id)

    elif "пак" in text:
        send_drums_zip(chat_id)

    elif "текст" in text:
        send_texts(chat_id)

    elif "прайс" in text:
        send_price(chat_id)

    elif "контакт" in text:
        bot.send_message(chat_id, "📩 @st1f_music")


# ================= ЖАНРЫ =================
def send_genres(chat_id):
    if not os.path.exists("beats"):
        bot.send_message(chat_id, "Папка beats пуста 😅")
        return

    kb = types.InlineKeyboardMarkup()

    for genre in os.listdir("beats"):
        kb.add(types.InlineKeyboardButton(genre, callback_data=f"genre:{genre}"))

    bot.send_message(chat_id, "Выбери жанр:", reply_markup=kb)


# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    data = call.data

    if data.startswith("genre:"):
        genre = data.split(":")[1]
        user_state[chat_id] = genre

        path = f"beats/{genre}"
        kb = types.InlineKeyboardMarkup()

        for mood in os.listdir(path):
            kb.add(types.InlineKeyboardButton(mood, callback_data=f"mood:{mood}"))

        bot.send_message(chat_id, "Выбери настроение:", reply_markup=kb)

    elif data.startswith("mood:"):
        mood = data.split(":")[1]
        genre = user_state.get(chat_id)
        send_beats(chat_id, genre, mood)


# ================= ОТПРАВКА БИТОВ =================
def send_beats(chat_id, genre, mood):
    path = f"beats/{genre}/{mood}"

    if not os.path.exists(path):
        bot.send_message(chat_id, "Файлов нет 😅")
        return

    files = os.listdir(path)

    if not files:
        bot.send_message(chat_id, "Папка пуста 😅")
        return

    selected = random.sample(files, min(3, len(files)))

    for file in selected:
        bot.send_audio(chat_id, open(f"{path}/{file}", "rb"))

    user = bot.get_chat(chat_id)
    log(user, f"Beat: {genre}/{mood}")


# ================= ZIP ДРАМ-ПАК =================
def send_drums_zip(chat_id):
    pack_path = "Drums/ST1F Mus!c x Moody"
    zip_name = "ST1F_Music_x_Moody_Drum_Pack.zip"

    if not os.path.exists(pack_path):
        bot.send_message(chat_id, "Драм-пак не найден 😅")
        return

    with zipfile.ZipFile(zip_name, "w") as z:
        for root, dirs, files in os.walk(pack_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=pack_path)
                z.write(full_path, arcname)

    bot.send_document(chat_id, open(zip_name, "rb"))

    user = bot.get_chat(chat_id)
    log(user, "Drum Pack downloaded")


# ================= ТЕКСТЫ =================
def send_texts(chat_id):
    path = "texts/lyrics.txt"

    if not os.path.exists(path):
        bot.send_message(chat_id, "lyrics.txt не найден")
        return

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in random.sample(lines, min(5, len(lines))):
        bot.send_message(chat_id, line.strip())

    user = bot.get_chat(chat_id)
    log(user, "Lyrics requested")


# ================= ПРАЙС =================
def send_price(chat_id):
    kb = types.InlineKeyboardMarkup()

    kb.add(types.InlineKeyboardButton("💳 Купить Lease (20$)", url="https://t.me/st1f_music"))
    kb.add(types.InlineKeyboardButton("💎 Exclusive (100$)", url="https://t.me/st1f_music"))

    bot.send_message(
        chat_id,
        "💰 Прайс:\nLease — 20$\nExclusive — 100$\n\nСвяжись для покупки:",
        reply_markup=kb
    )


# ================= СТАРТ БОТА =================
print("🔥 ST1F BOT запущен")
bot.polling(none_stop=True, skip_pending=True)