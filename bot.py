from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY = "Kremenchuk,UA"

def wind_direction(deg):
    """Повертає напрямок вітру у вигляді стрілки або назви"""
    dirs = ["Пн", "Пн-Сх", "Сх", "Пд-Сх", "Пд", "Пд-Зх", "Зх", "Пн-Зх"]
    ix = int((deg + 22.5) / 45) % 8
    return dirs[ix]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! 🌤\nНапиши /weather — покажу погоду в Кременчуку"
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&units=metric&lang=uk&appid={WEATHER_API_KEY}"
    try:
        data = requests.get(url, timeout=10).json()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        wind_deg = data["wind"]["deg"]
        description = data["weather"][0]["description"].capitalize()

        wind_dir = wind_direction(wind_deg)

        text = (
            f"📍 {CITY}\n"
            f"🌡 Температура: {temp}°C (відчувається як {feels_like}°C)\n"
            f"💧 Вологість: {humidity}%\n"
            f"🌬 Вітер: {wind_speed} м/с ({wind_dir})\n"
            f"☁️ {description}"
        )

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text(f"❌ Помилка отримання погоди: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.run_polling()

if __name__ == "__main__":
    main()
