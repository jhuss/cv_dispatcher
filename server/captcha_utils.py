import random
import secrets
import string
from captcha.image import ImageCaptcha
from datetime import datetime, timedelta


CAPTCHA_EXPIRATION_5MIN = 5


class CaptchaManager():
    __image_builder = ImageCaptcha(width=200, height=60)
    store = {}
    timestamp = {}

    def generate(self, size=5):
        use_chars = '{}{}'.format(string.ascii_letters, string.digits)
        value = ''.join(random.choice(use_chars) for _ in range(size))
        return (value, self.__image_builder.generate(value))

    def register(self, value):
        token = secrets.token_urlsafe(16)

        if token in self.store.keys():
            token = self.register(value)

        self.store[token] = str(value).lower()
        self.timestamp[token] = datetime.utcnow()

        return token

    def forget(self, id):
        if id in self.store.keys():
            del self.store[id]
            del self.timestamp[id]

        # purgue expired
        expired = []
        for key in self.timestamp.keys():
            if self.__is_expired(key):
                expired.append(key)
        
        for key in expired:
            del self.store[key]
            del self.timestamp[key]

    def validate(self, id, value):
        valid = False
        expired = True

        if id in self.store.keys():
            valid = self.store[id] == str(value).lower()
            expired = self.__is_expired(id)

        return (valid, expired)

    def __is_expired(self, id):
        now = datetime.utcnow()
        return not now - timedelta(minutes=CAPTCHA_EXPIRATION_5MIN) <= self.timestamp[id] <= now
