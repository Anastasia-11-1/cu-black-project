import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import requests
import asyncio

ACC_WEATHER_API_KEY = 'T4gKEYGaY9ywpv1GcIkG5WkzcGBAWZNy'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот прогноза погоды. Используйте /weather для запроса прогноза.")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "/start - Приветствие\n"
        "/help - Список команд\n"
        "/weather - Запрос прогноза погоды"
    )
    await message.answer(help_text)

@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    await message.answer("Введите все точки маршрута (например, 'Москва, Санкт-Петербург, Сочи, 3').")

@dp.message()
async def handle_message(message: types.Message):
    user_input = message.text.strip()

    if ',' in user_input:
        route_parts = user_input.split(',')
        points = [part.strip() for part in route_parts[:-1]]
        days = int(route_parts[-1].strip())

        weather_info = get_weather(points, days)

        if weather_info:
            await message.answer(weather_info)
        else:
            await message.answer("Не удалось получить прогноз погоды. Попробуйте еще раз.")
    else:
        await message.answer("Пожалуйста, введите корректный маршрут в формате 'Город1, Город2,  ..., Количество дней'.")

def get_weather(points, days):
    weather_reports = []

    for point in points:
        cnt = days
        location_key = get_location_key(point)
        if location_key:
            url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}?apikey={ACC_WEATHER_API_KEY}&language=ru-ru&details=true&metric=true"
            try:
                response = requests.get(url)
                data = response.json()

                if response.status_code == 200 and data:
                    for day in data['DailyForecasts']:
                        if cnt > 0:
                            date = day['Date']
                            temp_min = day['Temperature']['Minimum']['Value']
                            temp_max = day['Temperature']['Maximum']['Value']
                            weather_description = day['Day']['IconPhrase']
                            weather_reports.append(f"Погода в городе {point} на {date}: {temp_min}°C - {temp_max}°C, {weather_description}.\n")
                            cnt -= 1
                else:
                    weather_reports.append(f"Не удалось получить данные для {point}.")
            except Exception as e:
                logging.error(f"Ошибка при получении данных для {point}: {e}")
                weather_reports.append(f"Ошибка при получении данных для {point}.")
        else:
            weather_reports.append(f"Не удалось найти местоположение для {point}.")

    return "\n".join(weather_reports)

def get_location_key(location_name):
    url = f"http://dataservice.accuweather.com/locations/v1/search?q={location_name}&apikey={ACC_WEATHER_API_KEY}&language=ru-ru"

    try:
        response = requests.get(url)
        data = response.json()
        print(data)

        if response.status_code == 200 and data:
            return data[0]['Key']
        else:
            return None

    except Exception as e:
        logging.error(f"Ошибка при получении ключа местоположения для {location_name}: {e}")
        return None

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
