import os
import telebot

# Получаем токен из переменной окружения Railway
TOKEN = os.getenv("BOT_TOKEN")

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# Убираем старые вебхуки, чтобы не было ошибки 409
bot.remove_webhook()

# Папка beats (пример)
BEATS_FOLDER = "beats"

# Команда /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "🔥 Привет! ST1F BOT онлайн!")

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def text_handler(message):
    text = message.text.lower()

    if text == "beats":
        # Проверяем есть ли файлы в папке beats
        if os.path.exists(BEATS_FOLDER) and os.listdir(BEATS_FOLDER):
            bot.send_message(message.chat.id, "🎵 Папка beats готова! Файлы на месте ✅")
        else:
            bot.send_message(message.chat.id, "⚠️ Папка beats пуста!")
    else:
        bot.send_message(message.chat.id, f"Ты написал: {message.text}")

# Запуск бота
if __name__ == "__main__":
    print("🔥 ST1F BOT запущен")
    bot.polling(none_stop=True, skip_pending=True)