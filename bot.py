import os
import telebot
from pathlib import Path

# Получаем токен из переменной окружения Railway
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("⚠️ ERROR: BOT_TOKEN не найден! Проверь Variables на Railway")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Проверка папки beats
beats_path = Path("beats")
if not beats_path.exists() or not any(beats_path.iterdir()):
    print("⚠️ ВНИМАНИЕ: Папка 'beats' пуста или не найдена!")
else:
    print(f"✅ Папка 'beats' готова. Найдено {len(list(beats_path.iterdir()))} файлов.")

# Пример команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🔥 ST1F BOT запущен и готов к работе!")

# Основной запуск с обработкой 409
def safe_polling():
    while True:
        try:
            bot.polling(none_stop=True, skip_pending=True)
        except telebot.apihelper.ApiTelegramException as e:
            if "409" in str(e):
                print("⚠️ 409 Conflict: другой экземпляр бота активен. Перезапуск через 5 сек...")
                import time
                time.sleep(5)
            else:
                raise e

if __name__ == "__main__":
    safe_polling()