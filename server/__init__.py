import sys
from base64 import b64encode
from sanic import Sanic, HTTPResponse
from sanic.response import redirect, html, json, file
from subprocess import Popen, PIPE
from .db import init_db, get_db
from .utils import AppMode, AppConfig, generate_url
from .petition_utils import schema_validation, create_petition
from .download_utils import validate_token
from .captcha_utils import CaptchaManager, CAPTCHA_EXPIRATION_5MIN


app = Sanic('CV_DISPATCHER')
captcha = CaptchaManager()

# config
CONFIG = AppConfig()
app.config.OAS = False
app.config.CORS_ORIGINS = generate_url(CONFIG['url']['https'], CONFIG['url']['base'])
app.config.FORWARDED_SECRET = CONFIG['server']['secret']

if app.config.FORWARDED_SECRET in [None, '']:
    raise Exception('You must assign a secret key in the server configuration')

if AppMode().is_development():
    backend_server = CONFIG['server']
    frontend_server = CONFIG['dev']['front']['server']

    app.config.CORS_ORIGINS = ','.join([
        app.config.CORS_ORIGINS,
        generate_url(backend_server['ssl']['enable'], backend_server['name'], backend_server['port']),
        generate_url(frontend_server['ssl']['enable'], frontend_server['name'], frontend_server['port'])
    ])

# Server Listeners
@app.before_server_start
async def app_before_start(app, loop):
    app.ctx.task_queue_process = Popen(['huey_consumer.py', '-l', 'tasks.log', 'server.tasks.huey'], stdout=PIPE, stderr=PIPE)
    init_db()

@app.after_server_stop
async def app_after_stop(app, loop):
    app.ctx.task_queue_process.terminate()

@app.middleware('request')
async def handle_request(request):
    db = get_db()
    request.ctx.db = db

@app.middleware('response')
async def handle_response(request, response):
    db = request.ctx.db
    if not db.is_closed():
        db.close()


if AppMode().is_development():
    @app.get('/')
    @app.get('/<path:path>')
    async def debug_mode(request, path=None):
        frontend_server = CONFIG['dev']['front']['server']
        redirect_path = '{}{}'.format(
            generate_url(frontend_server['ssl']['enable'], frontend_server['name'], frontend_server['port']),
            '/{}'.format(path) if path is not None else ''
        )
        response: HTTPResponse = redirect(redirect_path)
        return response
else:
    # TODO: check client/dist dir exist
    app.static('/', 'client/dist')

    @app.get('/')
    def home(request):
        with open('client/dist/index.html', encoding='utf8') as f:
            contents = f.read()
            return html(contents)

@app.post('/petition')
async def petition(request):
    data = request.json
    status = 'OK'
    messages = []

    valid_data, messages = schema_validation(data)
    if not valid_data:
        status = 'ERROR'

    if status == 'OK':
        captcha_id = request.cookies.get('captcha_id')
        valid_captcha, expired_captcha = captcha.validate(captcha_id, data['captcha'])

        if not valid_captcha:
            status = 'ERROR'
            messages = ['Captcha is not valid']
        if expired_captcha:
            status = 'CAPTCHA-EXPIRED'
            messages = ['Captcha has expired']
            captcha.forget(captcha_id)

        if status == 'OK':
            # status CREATED, FORWARDED or EXIST
            status, messages = create_petition(data)

            if status in ['CREATED', 'FORWARDED']:
                captcha.forget(captcha_id)

    return json({
        'status': status,
        'messages': messages
    })

@app.get('/captcha')
async def dispatch_captcha(request):
    value, image = captcha.generate()
    cookie_value = request.cookies.get('captcha_id')

    if cookie_value is not None:
        captcha.forget(cookie_value)

    captcha_id = captcha.register(value)
    response = json({
        'image': b64encode(image.getvalue()).decode()
    })
    response.cookies['captcha_id'] = captcha_id
    response.cookies['captcha_id']['max-age'] = CAPTCHA_EXPIRATION_5MIN * 60  # in seconds
    response.cookies['captcha_id']['samesite'] = 'None'
    response.cookies['captcha_id']['secure'] = True

    return response

@app.get('/download/<token:str>')
async def download(request, token):
    is_valid = validate_token(token)

    if is_valid:
        # TODO: check cv file exist
        return await file('cv_files/{}'.format(CONFIG['cv_files']['current_file']), filename=CONFIG['cv_files']['download_filename'])

    return redirect('/')
