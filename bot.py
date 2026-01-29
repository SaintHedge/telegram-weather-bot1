import os
import requests
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
CITY_QUERY = "Kremenchuk,UA"

def wind_direction(deg: int) -> str:
    directions = [
        "Пн", "Пн-Сх", "Сх", "Пд-Сх",
        "Пд", "Пд-Зх", "Зх", "Пн-Зх"
    ]
    return directions[round(deg / 45) % 8]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! 🌤\n"
        "Команда /weather — погода в Кременчуку\n\n"
        "Показує:\n"
        "• погоду зараз\n"
        "• прогноз на 6 / 12 / 18 годин (якщо ще попереду)"
    )

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # 🔹 ПОТОЧНА ПОГОДА
        current_url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={CITY_QUERY}&units=metric&lang=uk&appid={WEATHER_API_KEY}"
        )
        current = requests.get(current_url, timeout=10).json()

        city_name = current["name"]
        tz = timezone(timedelta(seconds=current["timezone"]))
        now_local = datetime.now(tz)

        temp_now = current["main"]["temp"]
        feels = current["main"]["feels_like"]
        humidity = current["main"]["humidity"]

        wind_speed = current["wind"]["speed"]
        wind_deg = current["wind"].get("deg", 0)
        wind_dir = wind_direction(wind_deg)

        desc_now = current["weather"][0]["description"].capitalize()

        text = (
            f"📍 {city_name}\n"
            f"🕒 Зараз ({now_local:%H:%M}):\n"
            f"🌡 Температура: {temp_now}°C (відчувається як {feels}°C)\n"
            f"💧 Вологість: {humidity}%\n"
            f"🌬 Вітер: {wind_speed} м/с, {wind_dir}\n"
            f"☁️ {desc_now}\n\n"
            f"⏰ Прогноз на сьогодні:\n"
        )

        # 🔹 ПРОГНОЗ
        forecast_url = (
            "https://api.openweathermap.org/data/2.5/forecast"
            f"?q={CITY_QUERY}&units=metric&lang=uk&appid={WEATHER_API_KEY}"
        )
        forecast = requests.get(forecast_url, timeout=10).json()

        target_hours = [6, 12, 18]
        found = False

        for item in forecast["list"]:
            dt_local = datetime.fromtimestamp(item["dt"], tz)

            if dt_local.date() != now_local.date():
                continue
            if dt_local.hour not in target_hours:
                continue
            if dt_local <= now_local:
                continue

            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"].capitalize()

            text += f"🕒 {dt_local:%H:%M} — {temp}°C, {desc}\n"
            found = True

        if not found:
            text += "Немає прогнозу на сьогодні 🙃"

        await update.message.reply_text(text)

    except Exception as e:
        await update.message.reply_text("⚠️ Не вдалося отримати погоду")
        print(e)

def main():
    if not BOT_TOKEN or not WEATHER_API_KEY:
        raise RuntimeError("BOT_TOKEN або WEATHER_API_KEY не задані")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))

    app.run_polling()

if __name__ == "__main__":
    main()
