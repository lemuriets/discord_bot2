import json


def update_guilds(path_to_json_file: str, guild_id: int, method: str) -> None:
    try:
        with open(path_to_json_file, 'r', encoding='utf-8') as json_file:
            py_dict = json.load(json_file)
    except FileNotFoundError:
        return None

    if method.lower() == 'append':
        py_dict.get('guild_ids').append(guild_id)

    elif method.lower() == 'remove':
        py_dict.get('guild_ids').remove(guild_id)

    with open(path_to_json_file, 'w', encoding='utf-8') as new_json_file:
        json.dump(py_dict, new_json_file, indent=4)
