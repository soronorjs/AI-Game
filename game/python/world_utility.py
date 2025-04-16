import json

def save_world(world, filepath):
    with open(filepath, "w") as file:
        json.dump(world, file)

def load_world(filepath):
    with open(filepath, "r") as file:
        return json.load(file)