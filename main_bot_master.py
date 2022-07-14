# https://pypi.org/project/pyTelegramBotAPI
# https://towardsdatascience.com/google-trends-api-for-python-a84bc25db88f?gi=ddd552717c2a
# https://www.pythontutorial.net/advanced-python/python-threading/
# https://dev.to/biplov/handling-passwords-and-secret-keys-using-environment-variables-2ei0


from threading import Thread
import logging
import re
import time
import os
from datetime import date

import telebot
import schedule
from dotenv import load_dotenv

import google_news
import google_trands
import is_alive_checker
import telegram_image
import db
import weather


class main_bot:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.environ.get('bot_TOKEN')
        self.bot = telebot.TeleBot(self.bot_token, parse_mode=None)
        # Add logger
        self.logger_main_bot = logging.getLogger('main_bot_master')
        f_handler = logging.FileHandler('Telegram.log')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger_main_bot.addHandler(f_handler)

        self.database = db.database()
        self.google_trends = google_trands.google_trends()
        self.google_news = google_news.google_news()

    def run_bot(self):

        def one_letter_command_e(message):
            try:
                if len(message.text) == 1 and message.text in ['e', 'E', 'е', 'Е']:
                    return True
                else:
                    return False
            except Exception:
                return False

        def one_letter_command_t(message):
            try:
                if len(message.text) == 1 and message.text in ['t', 'T', 'т', 'Т']:
                    return True
                else:
                    return False
            except Exception:
                return False

        def is_replay_for_google_trends(message):
            if message.reply_to_message:
                replaied_message = message.reply_to_message.text
                try:
                    title = replaied_message.split('\n')[0]
                except Exception:
                    return False
                if title == 'Тренды Google:':
                    return True
                else:
                    return False
            else:
                return False

        @self.bot.message_handler(commands=['help', ])
        def send_help(message):
            self.bot.reply_to(message, "1. Отправьте букву 'e', чтобы получить карикатуру Елкина;\n"
                                       "2. Отправьте букву 't', чтобы получить тренды поиска Google на текущий момент;\n"
                                       "3. Раз в день в 12.00 будут приходить актуальные запросы в Google "
                                       "по России и Украине;\n"
                                       "4. Чтобы получить новость по актуальному запросу в ответ на него отправьте "
                                       "цифру с номером запроса;\n"
                                       "5. Раз в день в 9.00 будет приходить текущий статус;\n"
                                       "6. 'погода <город>' - узнать текущую погоду, погода <город> <число> - "
                                       "погода на число (доступно на 6 днй вперед);\n"
                                       "7. Как только помрет - придет уведомление."
                              )

        @self.bot.message_handler(commands=["start", ])
        def send_welcome(message):
            self.bot.reply_to(message, "Как только - так сразу!")
            self.database.create_new_user(message.chat.id)

        @self.bot.message_handler(func=one_letter_command_e)
        def send_cartoon(message):
            # Get last cartoon number
            cartoon = telegram_image.elkin_cartoon()
            last_number = cartoon.get_last_number()

            # if last number > last_number in database
            user_row = self.database.get_user(message.chat.id)
            db_last_number = user_row.get('last_cartoon_number')
            if not db_last_number or db_last_number < last_number:
                self.database.change_last_cartoon_number(message.chat.id, last_number)
                self.database.change_current_cartoon_number(message.chat.id, last_number)
                user_row['current_cartoon_number'] = last_number
            self.bot.send_message(message.chat.id, cartoon.get_cartoon_url(user_row.get('current_cartoon_number')))
            self.database.change_current_cartoon_number(message.chat.id, cartoon.current_number)

        @self.bot.message_handler(func=one_letter_command_t)
        def send_google_trends(message):

            russian_trends = self.google_trends.google_trending_search("russia")
            ukranian_trends = self.google_trends.google_trending_search("ukraine")
            result = 'Тренды Google:\n\nВ России:\n'
            for num, item in enumerate(russian_trends):
                result = '\n'.join((result, f'{num + 1}\t{item}'))
            result = '\n'.join((result, f'\n\nВ Украине:\n'))
            for num, item in enumerate(ukranian_trends):
                result = '\n'.join((result, f'{num + 1 + len(russian_trends)}\t{item}'))
            result = f'{result}\n----------'
            self.bot.send_message(message.chat.id, result)

        @self.bot.message_handler(func=is_replay_for_google_trends)
        def send_google_news(message):
            try:
                number = int(message.text)
                assert 0 < number <= 20
                if number <= 10:
                    language = 'ru'
                else:
                    language = 'ua'
            except Exception as e:
                self.logger_main_bot.exception(f'Error than answer to trends. {e}')
                self.bot.send_message(message.chat.id, 'Попробуйте еще раз.')
                return

            replaied_message = message.reply_to_message.text

            search_word = re.findall(f'\n{number}(.+)\n', replaied_message)
            if search_word:
                search_result = self.google_news.get_google_news(search_word[0], language=language)
            else:
                search_result = None
            if search_result:
                self.bot.send_message(message.chat.id, search_result)
            else:
                self.bot.send_message(message.chat.id, 'Попробуйте еще раз. Ничего не найти.')

        @self.bot.message_handler(func=lambda m: m.text.startswith('Погода ') or m.text.startswith('погода '))
        def send_weather(message):
            try:
                first_line = re.findall(r'[пП]огода (\D+)(\d*)', message.text)[0]
                city = first_line[0]
                day = first_line[1]

                if city and day:
                    msg = weather.weather().get_weather_forcast_day(city, day)
                    if msg:
                        self.bot.send_message(message.chat.id, msg)
                    else:
                        self.bot.send_message(message.chat.id, f'Не могу найти погоду для {city}. Попробуйте еще раз.')
                elif city:
                    msg = weather.weather().get_current_weather(city)
                    if msg:
                        self.bot.send_message(message.chat.id, msg)
                    else:
                        self.bot.send_message(message.chat.id, f'Не могу найти погоду для {city}. Попробуйте еще раз.')
                else:
                    self.bot.send_message(message.chat.id, f'Не могу найти погоду. Попробуйте еще раз.')

            except Exception as e:
                self.logger_main_bot.exception(f"Can not get weather. {e}")
                return None

        self.bot.infinity_polling()

    def sheduler_bot(self):

        # Check if alive every 30 minutes / Send if no
        def is_alive_checker_bot():
            alive = is_alive_checker.is_alive()
            if alive != -1:
                if not alive:
                    users = self.database.get_users()
                    for user in users:
                        try:
                            self.bot.send_message(user.get('chat_id'), 'ПОМЕР!!!')
                        except Exception as e:
                            self.logger_main_bot.exception(f'{e}')
                            return None
            return None

        # Check if alive every 09/00 / Send if yes or no
        def is_alive_checker_morning_bot():
            alive = is_alive_checker.is_alive()
            if alive != -1:
                users = self.database.get_users()
                for user in users:
                    try:
                        if not alive:
                            self.bot.send_message(user.get('chat_id'), 'ПОМЕР!!!')
                        else:
                            self.bot.send_message(user.get('chat_id'),
                                                  f'все еще жив... '
                                                  f'(уже {(date.today() - date(1952, 10, 7)).days} дней...)')

                    except Exception as e:
                        self.logger_main_bot.exception(f'{e}')
                        return None
            return None

        # Send every day 12/00 google trends
        def google_trends_morning():

            russian_trends = self.google_trends.google_trending_search("russia")
            ukranian_trends = self.google_trends.google_trending_search("ukraine")

            result = 'Тренды Google:\n\nВ России:\n'
            for num, item in enumerate(russian_trends):
                result = '\n'.join((result, f'{num + 1}\t{item}'))
            result = '\n'.join((result, f'\n\nВ Украине:\n'))
            for num, item in enumerate(ukranian_trends):
                result = '\n'.join((result, f'{num + 1 + len(russian_trends)}\t{item}'))
            result = f'{result}\n----------'
            users = self.database.get_users()
            for user in users:
                try:
                    self.bot.send_message(user.get('chat_id'), result)
                except Exception as e:
                    self.logger_main_bot.exception(f'{e}')
                    return None

        schedule.every(30).minutes.do(is_alive_checker_bot)
        schedule.every().day.at("09:00").do(is_alive_checker_morning_bot)
        schedule.every().day.at("12:00").do(google_trends_morning)

        while True:
            schedule.run_pending()
            time.sleep(2)


if __name__ == "__main__":
    instance_main_bot = main_bot()

    thred1 = Thread(target=instance_main_bot.run_bot)
    thred2 = Thread(target=instance_main_bot.sheduler_bot)

    thred1.start()
    thred2.start()
