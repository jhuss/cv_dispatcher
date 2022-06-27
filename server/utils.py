import html
import tomlkit
from os import environ


class AppMode():
    __PRODUCTION = 'PROD'
    __DEVELOPMENT = 'DEV'
    __modes = [__PRODUCTION, __DEVELOPMENT]

    def __get_mode(self):
        mode = str(environ.get('APP_MODE', self.__PRODUCTION)).upper()

        if mode not in self.__modes:
            raise Exception('Invalid APP_MODE: {}'.format(mode))

        return mode

    def is_production(self):
        return self.__get_mode() == self.__PRODUCTION

    def is_development(self):
        return self.__get_mode() == self.__DEVELOPMENT


class AppConfig(object):
    def __new__(cls):
        if AppMode().is_development():
            with open('config/dev.toml', 'rb') as f:
                return tomlkit.load(f)

        with open('config/prod.toml', 'rb') as f:
                return tomlkit.load(f)


def generate_url(is_https=False, hostname=None, port=None):
    if hostname is None:
        raise Exception('Missing hostname')

    schema = 'https' if is_https else 'http'
    port = '' if port is None else ':{}'.format(port)

    return '{}://{}{}'.format(schema, hostname, port)

def clean_input(input_string):
    if input_string:
        return html.escape(input_string).strip()
