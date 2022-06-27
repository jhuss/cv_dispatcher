from datetime import datetime, timedelta
from peewee import DoesNotExist
from .db import CVRequest
from .utils import AppConfig, generate_url, clean_input


CONFIG = AppConfig()


def validate_token(token):
    token = clean_input(token)
    valid = False

    try:
        petition_record = CVRequest.select().where(CVRequest.token == token).get()

        if petition_record.downloaded == False:
            petition_record.downloaded = True
            petition_record.downloaded_date = datetime.utcnow()
            petition_record.save()
            valid = True
        else:
            now = datetime.utcnow()
            if now - timedelta(hours=24) <= petition_record.downloaded_date <= now:
                # token with less than 24h since its first download can still be downloadable
                valid = True
    except DoesNotExist:
        pass

    return valid

def generate_download_url(token):
    base_url = generate_url(CONFIG['url']['https'], CONFIG['url']['base'])
    return '{}/download/{}'.format(base_url, token)
