import json


def update_admins(path_to_json_file: str, key, user_id: int, method: str) -> None:
    try:
        with open(path_to_json_file, 'r', encoding='utf-8') as json_file:
            py_dict = json.load(json_file)
    except FileNotFoundError:
        return None

    if method.lower() == 'append':
        if user_id not in py_dict.get(key):
            py_dict.get(key).append(user_id)
    elif method.lower() == 'remove':
        if user_id in py_dict.get(key):
            py_dict.get(key).remove(user_id)
    else:
        return None

    with open(path_to_json_file, 'w', encoding='utf-8') as new_json_file:
        json.dump(py_dict, new_json_file, indent=4)
