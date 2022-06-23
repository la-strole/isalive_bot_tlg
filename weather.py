# https://home.openweathermap.org/
# https://openweathermap.org/api/one-call-3
import os
import logging
import requests
from datetime import datetime

from transliterate import translit

from dotenv import load_dotenv


class weather:
    def __init__(self):
        # Add logger
        self.logger_weather = logging.getLogger('weather')
        f_handler = logging.FileHandler('Telegram.log')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger_weather.addHandler(f_handler)

        self.token = os.environ.get('weather_token')

        try:
            assert self.token
        except AssertionError:
            self.logger_weather.error("API token not found.")

    def _decorator_token_exist(f):
        def inner(self, *args):
            if self.token:
                return f(self, *args)
            else:
                return None

        return inner

    @_decorator_token_exist
    def get_geocoding(self, city):
        city = translit(city, 'ru', reversed=True)
        url = f'https://api.openweathermap.org/geo/1.0/direct?' \
              f'q={city}&limit=2&appid={self.token}'
        try:
            responce = requests.get(url).json()
            result = {'lat': responce[0].get('lat'), 'lon': responce[0].get('lon')}
        except Exception as e:
            self.logger_weather.exception(f"Can not get geocoding for city {city}. Exception: {e}.")
            return None
        return result

    @_decorator_token_exist
    def get_current_weather(self, city):
        city = translit(city, 'ru', reversed=True)
        geocoding = self.get_geocoding(city)
        if geocoding:
            url = f"https://api.openweathermap.org/data/2.5/weather?" \
                  f"lat={geocoding.get('lat')}&lon={geocoding.get('lon')}&lang=ru&units=metric&appid={self.token}"
            try:
                responce = requests.get(url).json()
                item = {'weather': responce['weather'][0]['description']}
                item.update(responce['main'])
                item.update(responce['wind'])
                result = f"Погода в г. {translit(city, 'ru')}:\n"
                result = ''.join((result, f'{item["weather"]}, '
                                          f'{int(item["temp"])}\u00B0, '
                                          f'ощущается {int(item["feels_like"])}\u00B0, '
                                          f'{item["humidity"]}%, '
                                          f'ветер {item["speed"]} м/с'))
            except Exception as e:
                self.logger_weather.exception(f"Can not get current weather for {city}. Extension: {e}.")
                return None
            return result
        else:
            self.logger_weather.error(f"Can not get geocoding for '{city}'")
            return None

    @_decorator_token_exist
    def get_weather_forcast_day(self, city, day):
        city = translit(city, 'ru', reversed=True)
        geocoding = self.get_geocoding(city)
        if geocoding:
            url = f"https://api.openweathermap.org/data/2.5/forecast?" \
                  f"lat={geocoding.get('lat')}&lon={geocoding.get('lon')}&lang=ru&units=metric&appid={self.token}"
            try:
                assert 1 < int(day) < 31
                responce = requests.get(url).json()
                day_weather = [row for row in responce['list'] if datetime.fromtimestamp(row['dt']).day == int(day)]
                if not day_weather:
                    return "Погода доступна на 6 дней вперед"
                result = f'Погода в г. {translit(city, "ru")} на {day} число\n'
                for item in day_weather:
                    dt = datetime.fromtimestamp(item["dt"])
                    result = '\n'.join((result, f'{dt.hour}:00 {item["weather"][0]["description"]}, '
                                                f'{int(item["main"]["temp"])}\u00B0 '
                                                f'{item["main"]["humidity"]}%, '
                                                f'ветер {item["wind"]["speed"]} м/с, '
                                                f'порывы {item["wind"]["gust"]} м/с'))
                return result
            except Exception as e:
                self.logger_weather.exception(f"Can not get weather forcast for {city}. Extension: {e}.")
                return None
        else:
            self.logger_weather.error(f"Can not get geocoding for '{city}'")
            return None


if __name__ == "__main__":

    load_dotenv()

    instance = weather()
    print(instance.get_current_weather('Псков'))
