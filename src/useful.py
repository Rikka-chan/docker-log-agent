import os
import re
import glob

from docker import Client

path_to_logs = '/var/lib/docker/containers/'
cli = Client(base_url='unix://var/run/docker.sock')


def get_path_to_log(container_id):
    return path_to_logs + '{0}/{0}-json.log'.format(container_id)


def collect_logfiles():
    return glob.iglob(path_to_logs + '/**/*.log', recursive=True)


def get_container_name(container_id):
    if not container_id:
        return

    inspect = cli.inspect_container(container_id)
    return inspect.get('Name').replace('/', '')


def get_id_from_patn(path):
    container_id = re.search(r'(((\w)+?)(?=-json\.log))', path)
    return container_id.group(0)


def pack_container(path):
    result = {
        'size': str(os.path.getsize(path)),
        'id': get_id_from_patn(path),
        'name': get_container_name(get_id_from_patn(path))
    }
    return result


def process_file(fn, container_id, numlines):
    path = get_path_to_log(container_id)
    try:
        logfile = open(path)
        # pass generic function name
        lines = fn(logfile, numlines)
        return lines
    finally:
        logfile.close()


def search_expression(path, expression, result=None):
    logfile = open(path)
    for line in logfile:
        match = re.search(expression, line)
        if match:
            result.append({'line': line,
                           'match': match.group(0)})