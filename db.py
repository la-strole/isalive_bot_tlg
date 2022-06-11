import sqlite3
import logging
import os

from sqlite3 import Error


class database:

    def __init__(self):
        # logging
        self.logger_db = logging.getLogger('db')
        f_handler = logging.FileHandler('Telegram.log')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        self.logger_db.addHandler(f_handler)

        self.db_name = f'{os.environ.get("db_path")}/user_db.db'

        if not os.path.isfile('./user_db.db'):
            with open('schema.sql') as fp:
                try:
                    with sqlite3.connect(self.db_name) as con:
                        con.executescript(fp.read())
                        con.commit()
                except Error as e:
                    self.logger_db.exception(f"Can not create database. {e}")

    def create_new_user(self, chat_id):
        try:
            assert chat_id is not None
            chat_id = int(chat_id)
        except AssertionError as e:
            self.logger_db.exception(f"Can not create new user - chat_id is empty. {e}")
            return None

        try:
            with sqlite3.connect(self.db_name) as con:
                con.row_factory = sqlite3.Row
                rows = con.execute("SELECT * FROM users "
                                   "WHERE chat_id = ?",
                                   (chat_id,))

        except Error as e:
            self.logger_db.exception(f"Can not get user. {e}")
            return None

        if not rows.fetchone():
            try:
                with sqlite3.connect(self.db_name) as con:
                    con.row_factory = sqlite3.Row
                    con.execute('INSERT INTO users '
                                '(chat_id) '
                                'VALUES (?)',
                                (chat_id,))
                    con.commit()
            except Error as e:
                self.logger_db.exception(f"Can not commit to user database. {e}")
                return None

    def config_user(self, kwargs):
        try:
            for key in kwargs:
                assert key in ('chat_id', 'send_trends', 'send_notifications',
                               'time_to_trends', 'time_to_notifications')
        except AssertionError as e:
            self.logger_db.exception(f"Can not modify user settings. {e}")
            return None

        try:
            with sqlite3.connect(self.db_name) as con:
                con.row_factory = sqlite3.Row
                con.execute("UPDATE users "
                            "SET "
                            "send_trends = ?,"
                            "send_notifications = ?, "
                            "time_to_trends = ?, "
                            "time_to_notifications = ? "
                            "WHERE chat_id = ?",
                            (kwargs['send_trends'], kwargs['send_notifications'], kwargs['time_to_trends'],
                             kwargs['time_to_notifications'], kwargs['chat_id']))
                con.commit()
        except Error as e:
            self.logger_db.exception(f"Can not change configuration for user. {e}")

    def change_last_cartoon_number(self, chat_id, cartoon_number):

        try:
            assert chat_id is not None
            assert cartoon_number is not None
            int(cartoon_number)
            int(chat_id)
        except ValueError as e:
            self.logger_db.exception(f"Cartoon number can not converted to integer. {e}")
            return None
        except AssertionError as e:
            self.logger_db.exception(f"Looks like cartoon_number or chat_id is None. {e}")
            return None

        try:
            with sqlite3.connect(self.db_name) as con:
                con.row_factory = sqlite3.Row
                con.execute("UPDATE users "
                            "SET last_cartoon_number = ? "
                            "WHERE chat_id = ?",
                            (cartoon_number, chat_id))
                con.commit()
        except Error as e:
            self.logger_db.exception(f"Can not change last_cartoon_number. {e}")

    def change_current_cartoon_number(self, chat_id, cartoon_number):
        try:
            assert chat_id is not None
            assert cartoon_number is not None
            int(cartoon_number)
            int(chat_id)
        except ValueError as e:
            self.logger_db.exception(f"Cartoon number can not converted to integer. {e}")
            return None
        except AssertionError as e:
            self.logger_db.exception(f"Looks like cartoon_number or chat_id is None. {e}")
            return None

        try:
            with sqlite3.connect(self.db_name) as con:
                con.row_factory = sqlite3.Row
                con.execute("UPDATE users "
                            "SET current_cartoon_number = ? "
                            "WHERE chat_id = ?",
                            (cartoon_number, chat_id))
                con.commit()
        except Error as e:
            self.logger_db.exception(f"Can not change current_cartoon_number. {e}")

    def delete_user(self, chat_id):
        try:
            with sqlite3.connect(self.db_name) as con:
                con.row_factory = sqlite3.Row
                con.execute("DELETE FROM users "
                            "WHERE chat_id = ?",
                            (chat_id,))
                con.commit()
        except Error as e:
            self.logger_db.exception(f"Can not delete user. {e}")

    def get_users(self):
        try:
            with sqlite3.connect(self.db_name) as con:
                con.row_factory = sqlite3.Row
                rows = con.execute("SELECT * FROM users")
                result = [dict(row) for row in rows.fetchall()]
        except Error as e:
            self.logger_db.exception(f"Can not get users. {e}")
            return None
        return result

    def get_user(self, chat_id):
        try:
            with sqlite3.connect(self.db_name) as con:
                con.row_factory = sqlite3.Row
                rows = con.execute("SELECT * FROM users "
                                   "WHERE chat_id = ?",
                                   (chat_id,))
                result = dict(rows.fetchone())
        except Error as e:
            self.logger_db.exception(f"Can not get user. {e}")
            return None
        return result


if __name__ == "__main__":
    instance = database()

    instance.create_new_user('1234567890')
    kwargs = {'send_trends': 0, 'send_notifications': 0, 'time_to_trends': '00.00', 'time_to_notifications': '03.00',
              'chat_id': '1234567890'}
    instance.config_user(kwargs)

    # instance.delete_user(chat_id='1234567890')
    print(instance.get_user('1234567890'))
