import logging

import requests


def is_alive():

    logger = logging.getLogger('is_alive_checker')
    f_handler = logging.FileHandler('Telegram.log')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

    url = 'https://parhom.tech'
    page = requests.get(url)

    if page.status_code == 200:
        if 'Yes' in page.text:
            return True
        else:
            return False
    else:
        logger.error(f"Can not get page {url}. Status code is {page.status_code}")
        return -1
