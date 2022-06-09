# https://pypi.org/project/pyTelegramBotAPI
# https://towardsdatascience.com/google-trends-api-for-python-a84bc25db88f?gi=ddd552717c2a
# https://pypi.org/project/pytrends/

import logging
from pytrends.request import TrendReq


class google_trends:
    def __init__(self):
        # Add logging
        self.logger_google_trands = logging.getLogger('google_trands')
        f_handler = logging.FileHandler('Telegram.log')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger_google_trands.addHandler(f_handler)

    def google_interest_by_region(self, key_word):
        pytrend = TrendReq()
        if key_word:
            pytrend.build_payload(kw_list=[f'{key_word}'])  # Interest by Region
            df = pytrend.interest_by_region()
            df = df.sort_values(by=[f"{key_word}"], ascending=False)
            head = df.head(10)
            result = ''
            for i, v in zip(head.index, head.values):
                result = '\n'.join((result, f'{i}\t{v}'))
            return result
        else:
            self.logger_google_trands.error("google_interest_by_region: key_word is empty.")
            return None

    def google_trending_search(self, country, number_head=10):

        pytrend = TrendReq()

        # check country
        if country:
            try:
                assert isinstance(country, str)
            except AssertionError:
                self.logger_google_trands.error(f"google_tranding_search: country is not a string. It is {country}")
                return None

            country = country.lower()
            country = country.replace(' ', '_')
            try:
                df = pytrend.trending_searches(pn=country)
            except KeyError:
                self.logger_google_trands.error(f"google_tranding_search: country is not valid. It is {country}")
                return None

            num_array = df.to_numpy()

            # check number of rows
            try:
                assert number_head < 20
            except AssertionError:
                self.logger_google_trands.error(f"google_tranding_search: number of rows > 20. It is {number_head}. "
                                                f"It was set to max value")
                number_head = num_array.size

            # result = '\n'.join([f'{start_numeration + 1 + n}\t{num_array.item(n)}' for n in range(number_head)])
            result = [f'{num_array.item(n)}' for n in range(number_head)]
            return result
        else:
            self.logger_google_trands.error(f"google_tranding_search: country is empty")
            return None


if __name__ == "__main__":
    instance = google_trends()
    # print(instance.google_interest_by_region('война'))
    print(instance.google_trending_search('russia'))
