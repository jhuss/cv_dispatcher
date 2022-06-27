import server

if __name__ == '__main__':
    server.app.run(
        host=server.CONFIG['server']['name'],
        port=server.CONFIG['server']['port'],
        dev=server.AppMode().is_development(),
        debug=server.AppMode().is_development()
    )
