import sys
from sanic import Sanic, HTTPResponse
from sanic.response import redirect, json, file
from subprocess import Popen, PIPE
from .db import init_db, get_db
from .utils import AppMode, AppConfig, generate_url
from .petition_utils import schema_validation, create_petition
from .download_utils import validate_token


app = Sanic('CV_DISPATCHER')

# config
CONFIG = AppConfig()
app.config.OAS = False
app.config.CORS_ORIGINS = generate_url(CONFIG['url']['https'], CONFIG['url']['base'])

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
    db.connect()

@app.middleware('response')
async def handle_response(request, response):
    db = get_db()
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
    app.static('/public', 'client/public')

    @app.get('/')
    def home(request):
        # TODO: check index.html exist
        response: HTTPResponse = redirect('/index.html')
        return response

@app.post('/petition')
async def petition(request):
    data = request.json
    status = 'OK'
    messages = []

    valid_data, messages = schema_validation(data)
    if not valid_data:
        status = 'ERROR'

    if status == 'OK':
        # status CREATED, RESEND or EXIST
        status, messages = create_petition(data)

    return json({
        'status': status,
        'messages': messages
    })

@app.get('/download/<token:str>')
async def download(request, token):
    is_valid = validate_token(token)

    if is_valid:
        # TODO: check cv file exist
        return await file('cv_files/{}'.format(CONFIG['cv_files']['current_file']), filename=CONFIG['cv_files']['download_filename'])

    return redirect('/')
