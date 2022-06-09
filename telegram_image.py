import logging

from bs4 import BeautifulSoup
import requests


def is_page_status_ok(page, logger):
    try:
        assert page.status_code == 200
    except AssertionError:
        logger.exception(f"Response is not code 200 it is {page.status_code}")
        return -1


class elkin_cartoon:
    def __init__(self):

        # Add logging
        self.logger_image = logging.getLogger('telegram_image')
        f_handler = logging.FileHandler('Telegram.log')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger_image.setLevel('WARNING')
        self.logger_image.addHandler(f_handler)

        self.current_number = None
        # self.last_number = self.get_last_number()

    def get_last_number(self):

        page = requests.get('https://t.me/s/elkincartoon')
        if is_page_status_ok(page, self.logger_image) == -1:
            return None

        try:
            soup = BeautifulSoup(page.content, 'lxml')
            images = soup.find_all("a", class_="tgme_widget_message_photo_wrap")
            last_number = int((images[-1].attrs['href']).split('/')[-1])
            return last_number
        except Exception:
            return None

    def get_cartoon_url(self, number):

        self.current_number = number
        new_page = requests.get(f'https://t.me/elkincartoon/{number}')
        if is_page_status_ok(new_page, self.logger_image) == -1:
            return 'https://www.europeanagriteltour.com/wp-content/uploads/2019/07/Putin-bigbrother.jpg'

        try:
            new_soup = BeautifulSoup(new_page.content, 'lxml')
            image = new_soup.find_all("meta", attrs={'property': 'og:image'})
            url = image[0].attrs['content']
        except Exception as e:
            self.logger_image.exception(f"Exception {e}")
            return 'https://www.europeanagriteltour.com/wp-content/uploads/2019/07/Putin-bigbrother.jpg'

        if url == "https://cdn4.telegram-cdn.org/file/IjpvSwwsvCTBZ_kieuxJXf1P61fBDJHoHUfQYaJZngUgTHdz" \
                  "nFN9v53RP29J0Aa1-KpH_cTCoOxdm_EdaknMzXkxNC289aKp05905W9NEdcObIfD9c_-IboJDpKx2Uy5dc_D" \
                  "1P5z8DloS7DmBL5vIaNFYpH4HBnvbvSDScGTjj8KFnOdK3jHlVLGKcC08ehBzKi_TIhkHVU7gmJGY5Gf1ID0m" \
                  "9k7fjMeuIi02dsy8O1FzX38aLPMvu4tvHQCQLP8SibwxD0QvytH0wYoG0WRNwogOpTWdin5L8cLcJtSG2gO2h" \
                  "EOE1U-RMTa-pmT3uGpkrS3nQibWVvyUhKLqkneJg.jpg":
            self.logger_image.warning("Recursion")
            self.current_number -= 1
            if self.current_number < 2:
                return 'https://www.europeanagriteltour.com/wp-content/uploads/2019/07/Putin-bigbrother.jpg'
            return self.get_cartoon_url(self.current_number)
        self.current_number -= 1
        if self.current_number < 2:
            return 'https://www.europeanagriteltour.com/wp-content/uploads/2019/07/Putin-bigbrother.jpg'
        return url
