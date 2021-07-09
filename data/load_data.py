import json


def load_items_from_file(path: str) -> list:
    with open(path) as p:
        data = json.load(p)
        return data["items"]


def load_items_as_dict(path: str) -> dict:
    items = load_items_from_file(path)
    items_dict = {}
    for item in items:
        name = item["name"]
        items_dict[name] = item
    return items_dict


def load_projects() -> dict:
    return load_items_as_dict("data/projects.json")


def load_profiles() -> dict:
    return load_items_as_dict("data/profiles.json")
