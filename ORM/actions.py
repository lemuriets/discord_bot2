from .connect import client, collection


def add_to_db(user_id: int, username: str) -> None:
    if collection.count_documents({'_id': user_id}) == 0:
        new_user = {
            '_id': user_id,
            'name': username,
            'description': 'no description',
            'warns': 0
        }

        collection.insert_one(new_user)


def update_description(user_id: int, new_description: str) -> None:
    collection.update_one({'_id': user_id}, {'$set': {'description': new_description}})


def reset_warn(user_id: int, new_value: int) -> None:
    collection.update_one({'_id': user_id}, {'$set': {'warns': int(new_value)}})


def give_warn(user_id: int) -> None:
    collection.update_one({'_id': user_id}, {'$inc': {'warns': 1}})


def get_user(user_id: int) -> dict:
    user = collection.find_one({'_id': user_id})
    return user
