import sys
from sanic import Sanic, HTTPResponse
from sanic.response import redirect, json
from .db import init_db, get_db
from .petition_utils import schema_validation, create_petition

# options
DEBUG = any(x in ['-d', '--dev', '--debug'] for x in sys.argv)

app = Sanic('CV_DISPATCHER')
app.config.OAS = False
app.config.DEBUG = DEBUG

if DEBUG:
    app.config.CORS_ORIGINS = ','.join([
        'http://localhost:8000',
        'http://localhost:3000'
    ])
else:
    app.config.CORS_ORIGINS = 'http://localhost:8000'

# Server Listeners
@app.before_server_start
async def app_before_start(app, loop):
    init_db()

@app.middleware('request')
async def handle_request(request):
    db = get_db()
    db.connect()

@app.middleware('response')
async def handle_response(request, response):
    db = get_db()
    if not db.is_closed():
        db.close()


if DEBUG:
    @app.get('/')
    @app.get('/<path:path>')
    async def debug_mode(request, path=None):
        redirect_path = 'http://localhost:3000{}'.format(
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
        # status CREATED or EXIST
        status, messages = create_petition(data)

    return json({
        'status': status,
        'messages': messages
    })
