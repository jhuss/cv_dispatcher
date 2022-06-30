import jsonschema
import re
import secrets
from peewee import DoesNotExist
from .db import CVRequest
from .tasks import send_download_link
from .utils import clean_input
from .download_utils import generate_download_url


PETITION_SCHEMA = {
    'type': 'object',
    'properties': {
        'address': { 'type': 'string', 'format': 'email' },
        'name': { 'type': 'string' },
        'note': { 'type': 'string' },
        'captcha': { 'type': 'string' },
        'forward': { 'type': 'boolean' },
    },
    'required': ['address', 'name', 'captcha'],
    'additionalProperties': False
}

def schema_validation(data):
    data_validator = jsonschema.Draft202012Validator(PETITION_SCHEMA, format_checker=jsonschema.FormatChecker())
    data_errors = sorted(data_validator.iter_errors(data), key=lambda e: e.schema_path)

    def required_string(match_obj):
        return '{} {} field'.format(match_obj.group(1).capitalize(), match_obj.group(2))

    if len(data_errors) > 0:
        messages = []

        for error in data_errors:
            error_path = list(error.path)
            if len(error_path) > 0:
                field = str(error_path[-1]).capitalize()
                condition = 'is not a valid' if error.validator == 'format' else 'must be'
                invalid = error.validator_value
                messages.append('{} {} {}'.format(field, condition, invalid))
            else:
                if error.validator == 'additionalProperties':
                     messages = ['The form is invalid']
                     break
                elif error.validator == 'required':
                    required_msg = re.sub(r'\'(.+)\' (.+) (property)', required_string, error.message)
                    messages.append(required_msg)

        return (False, messages)

    return (True, [])

def create_petition(data):
    # search for the last entry with the same email:
    # if: it has not been downloaded, use the same record again
    # if: it was already downloaded, create new
    # if: no previous entry, create new

    email = clean_input(data.get('address'))
    create = False

    try:
        petition_record = CVRequest.select().where(CVRequest.email == email).order_by(CVRequest.created_date.desc()).get()
        if petition_record.downloaded:
            create = True  # It was already downloaded, we create a new request
        else:
            if data.get('forward', False):
                send_email = send_download_link(
                    petition_record.email,
                    petition_record.name,
                    generate_download_url(petition_record.token)
                )
                send_email()
                return ('FORWARDED', ['The link to download will arrive in the email'])

            return ('EXIST', ['A request already exists, do you want to forward the download link?'])
    except DoesNotExist:
        create = True

    if create:
        petition_record = CVRequest(
            email=email,
            name=clean_input(data.get('name')),
            note=clean_input(data.get('note')),
            token=generate_token(),
        )
        petition_record.save()
        send_email = send_download_link(
            petition_record.email,
            petition_record.name,
            generate_download_url(petition_record.token)
        )
        send_email()
        return ('CREATED', ['The request was created correctly, the link to download will arrive in the email'])

    return ('ERROR', ['The request could not be processed'])

def generate_token():
    token = secrets.token_urlsafe(16)
    try:
        existing = CVRequest.select().where(CVRequest.token == token).get()
        return generate_token()
    except DoesNotExist:
        return token
