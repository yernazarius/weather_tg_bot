import telebot
import pprint
import requests
import json
from datetime import timedelta
import datetime
from config import tg_bot_token, open_weather_token
from emoji_set import *

bot = telebot.TeleBot(tg_bot_token)
API = open_weather_token

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет, рад тебя видеть на нашем уроке! Напиши название города')


code_to_smile = {
    "Clear": f"Ясно {clearSky}",
    "Clouds": f"Облачно {clouds}",
    "Rain": f"Дождь {rain}",
    "Drizzle": f"Дождь {drizzle}",
    "Thunderstorm": f"Гроза {thunderstorm}",
    "Snow": f"Снег {snowflake}",
    "Mist": f"Туман {atmosphere}",
    "Few clouds": f"Переменная облачность {fewClouds}"
}

@bot.message_handler(content_types=['text'])
def get_city(message):
    try: # запихал все в try except, чтобы ничего не сломалось и в случае ошибки вывело соответствующий ответ
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&lang=ru&units=metric" #добавил "&lang=ru, можно будет вводить на русском языке и вывод будет соответственно тоже
        )
        data = r.json() # получили все в формате json
        # берем необходимые параметры из полченного json файла
        city = data["name"]
        cur_weather = data["main"]["temp"]
        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, не пойму что там за погода!"
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"] / 1.333 # делим на 1.333 потому что вывод в hPa

        wind = data["wind"]["speed"]
        # в json файле время заката в колве секунд от 1 января 1970го года вроде. и теперь мы с помощью библиотеки datetime переводим в норм время
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])
        # достаем локальное время в заданном месте
        timezone_offset = data['timezone']
        utc_time = datetime.datetime.utcfromtimestamp(data['dt'])
        local_time = utc_time + timedelta(seconds=timezone_offset)


        # bot.send_message(message.chat.id, f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
        #     f"Погода в городе: {city}\nТемпература: {cur_weather}C° {weather_description}\n"
        #     f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
        #     f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n"
        #     f"***Хорошего дня!***\n"
        #     f"*******************\n"
        #     f"{data}"
        # )
        bot.send_message(message.chat.id, 
            f"<i>Время у вас:</i> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n<i>Местное время в заданном городе:</i> {local_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"<i>Город:</i> {city}\n<i>Температура:</i> {cur_weather}C° {wd}\n"
            f"<i>Влажность:</i> {humidity}%\n<i>Давление:</i> {pressure} мм.рт.ст\n<i>Ветер:</i> {wind} м/с\n"
            f"<i>Восход солнца:</i> {sunrise_timestamp}\n<i>Закат солнца:</i> {sunset_timestamp}\n<i>Продолжительность дня:</i> {length_of_the_day}\n"
            f"Обращайтесь!", parse_mode='html'
        )

    except Exception as ex:
        print(ex) # сообщение ошибки выйдет к нам в терминал
        bot.send_message(message.chat.id, "<b>Проверьте название города</b>", parse_mode='html')



bot.polling(none_stop=True)