# https://pypi.org/project/GoogleNews/
import logging

from GoogleNews import GoogleNews


class google_news:
    def __init__(self):
        # Set logging
        self.logger_gooogle_news = logging.getLogger('google_news')
        f_handler = logging.FileHandler('Telegram.log')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger_gooogle_news.addHandler(f_handler)

    def get_google_news(self, key_word, language='ru'):
        try:
            assert key_word
            assert isinstance(key_word, str)
        except AssertionError:
            self.logger_gooogle_news.exception(f"google_news: key_word is not valid ({key_word}).")
            return None

        try:
            googlenews = GoogleNews(lang=f'{language}', period='5d', region=f'{language.upper()}')
            googlenews.search(f'{key_word}')
            first_link = googlenews.results()[0]
            result = f'{first_link.get("title")}. \nДата: {first_link.get("date")}\nМедиа:{first_link.get("media")}'
        except Exception as e:
            self.logger_gooogle_news.exception(f"google_news: problem with google news. {e}")
            return None

        return result


if __name__ == "__main__":
    instance = google_news()
    print(instance.get_google_news('Агутин', language='ru'))

