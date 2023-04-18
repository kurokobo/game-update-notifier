import json
import os

from modules import models


def save_dict_as_json(dict, path):
    with open(path, mode="wt", encoding="utf-8") as file:
        json.dump(dict, file, ensure_ascii=False, indent=2, default=models.json_default)

def load_json_as_dict(path):
    try:
        with open(path, mode="r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}

def create_directory(path):
    os.makedirs(path, exist_ok=True)


def replace_file(old_path, new_path):
    if os.path.exists(old_path):
        os.replace(old_path, new_path)
