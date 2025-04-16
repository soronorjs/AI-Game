import requests
import json
import world_utility

context = ""
url = "http://localhost:11434/api/chat"
system_prompt = '''Your job is to create interesting, lore-rich fantasy worlds with a rich narrative as well as unique and varied environments, cultures and traditions. Instructions:
- Generate in plain, not too flowery text.
- Be consice. You must stay below 3-5 sentences.
- The worlds will have rich dynamics based on real-life social constructs.
- The denizens of this world will have adapted to the conditions and environment in unique ways.
'''

def generate_worlds(num_worlds, world_generation_prompt):
    worlds = {}
    for _ in range(num_worlds):
        payload = {
            "model": "hermes3:latest",
            "messages": [
                {"role":"user", "content":world_generation_prompt + " Use this format: \n World Name: \n World Description"},
                {"role":"assistant", "content":system_prompt}
            ],
            "stream": False,
            "options": {"temperature":1.0, "top_k": 100, "top_p": 1.0}
        }
        response = requests.post(url, json=payload)
        world_data = json.loads(response.text)
        world_name = world_data["message"]["content"].strip().split("World Name:")[1].strip().split("\n")[0]
        world_description = world_data["message"]["content"].strip().split("World Description:")[1].strip().split("\n")[0]
        world_dict = {"World Name": world_name, "World Description ": world_description}
        worlds[world_name] = world_dict
    return worlds

generated_worlds = generate_worlds(1, "Generate an unique and interesting world with room for deep and rich lore. The world should have a lot of info 'Between the lines'. Keep the description consice")
generated_worlds_list = list(generated_worlds.keys())

def generate_kingdoms(num_kingdoms, kingdom_generation_prompt, current_world):
    kingdoms = {}
    for _ in range(num_kingdoms):
        payload = {
            "model": "hermes3:latest",
            "messages": [
                {"role":"user", "content":kingdom_generation_prompt + " Use this format: \n Kingdom Name: \n Kingdom Description"},
                {"role":"user", "content":"The kingdom is located in this world: " + str(current_world)},
                {"role":"assistant", "content":system_prompt}
            ],
            "stream": False,
            "options": {"temperature":1.0, "top_k": 100, "top_p": 1.0}
        }
        response = requests.post(url, json=payload)
        kingdom_data = json.loads(response.text)
        kingdom_name = kingdom_data["message"]["content"].strip().split("Kingdom Name:")[1].strip().split("\n")[0]
        kingdom_description = kingdom_data["message"]["content"].strip().split("Kingdom Description:")[1].strip().split("\n")[0]
        kingdom_dict = {"Kingdom Name": kingdom_name, "Kingdom Description ": kingdom_description}
        kingdoms[kingdom_name] = kingdom_dict
    return kingdoms

for world in range(len(generated_worlds_list)):
    current_world = generated_worlds[generated_worlds_list[world]]
    generated_kingdoms = generate_kingdoms(1, "Generate an unique and interesting kingdom with room for deep and rich lore. The kingdom should have a lot of info 'Between the lines'. Keep the description consice", current_world)
    generated_kingdoms_list = list(generated_kingdoms.keys())
    current_world["Kingdoms"] = generated_kingdoms

# world_utility.save_world(generated_worlds[generated_worlds_list[0]], "Worlds/world.json")