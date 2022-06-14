import sys
from sanic import Sanic, HTTPResponse
from sanic.response import redirect, text

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
    print(request.json)
    return text("OK")
