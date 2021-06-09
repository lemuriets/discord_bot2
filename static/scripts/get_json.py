import json


def type_check(type_object: type):
    def decorator(func):
        def wrapper(path):
            if not isinstance(path, type_object):
                raise TypeError('Передан неправильный тип в параметр функции')
            return func(path)
        return wrapper
    return decorator


@type_check(str)
def get_json_file(path: str) -> dict:
    if not path.endswith('.json'):
        return dict()
    try:
        with open(path, 'r', encoding='utf-8') as json_file:
            python_dict = json.load(json_file)
        return python_dict
    except FileNotFoundError:
        return dict()
