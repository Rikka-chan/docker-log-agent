import tailer
from useful import get_path_to_log, \
                   search_expression,\
                   process_file, \
                   collect_logfiles, \
                   pack_container, \
                   get_container_name

from flask import Flask
from flask_jsonrpc import JSONRPC
from gevent import pool
from gevent.wsgi import WSGIServer
from gevent import monkey
monkey.patch_all()

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api')


def grep_expression(containers_ids=None, expression=None):
    if not containers_ids or not expression:
        return None

    result = {}
    group = pool.Group()
    for container in containers_ids:
        path = get_path_to_log(container)
        result[container] = {'name': get_container_name(container),
                             'data': []}
        group.apply_async(search_expression, (path, expression), {'result': result[container]['data']})

    group.join()
    return result


@jsonrpc.method('tail')
def tail(container_id, numlines=50):
    return process_file(tailer.tail, container_id, numlines)


@jsonrpc.method('head')
def head(container_id, numlines=50):
    return process_file(tailer.head, container_id, numlines)


@jsonrpc.method('grep')
def grep(*args, **kwargs):
    result = {}
    operations = {'expression': grep_expression}

    for operation in operations:
        if operation in kwargs:
            result[operation] = operations[operation](**kwargs[operation])
    return result


@jsonrpc.method('list')
def containers_list():
    containers = collect_logfiles()
    containers = list(map(pack_container, containers))
    return containers


if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()
