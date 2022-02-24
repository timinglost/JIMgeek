import json
import yaml


def get_data(parm, config):
    """Функция получения данных"""
    return json.loads(parm.recv(config['MAX_PACKAGE_LENGTH']).decode(config['ENCODING']))


def post_data(parm, data, config):
    """Функция отпрпавки данных"""
    return parm.send(json.dumps(data).encode(config['ENCODING']))


def load_config(name):
    """Функция распаковки файлов yaml"""
    with open(name) as config_yaml:
        return yaml.load(config_yaml, Loader=yaml.Loader)
