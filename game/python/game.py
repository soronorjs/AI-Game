import requests
import gradio as gr
import random
import json
import shelve
import time
from flask import Flask, request
from flask import session
from flask_cors import CORS
import world_utility as helper
from world_utility import load_world, save_world
from llm_utility import generate_JSON
demo = None

context = ""
url = "http://localhost:11434/api/chat"

world = load_world("Worlds\world.json")
kingdoms = list(world["Kingdoms"].keys())
kingdom = world["Kingdoms"][kingdoms[random.randint(0, len(kingdoms) - 1)]]

start_gen_prompt = """You are an AI Game master. Your job is to create a
start to an adventure based on the world, kingdom and character
a player is playing as.
Instructions:
You must only use 2-4 sentences
Write in second person. For example: "You are Jack"
Write in present tense. For example "You stand at..."
First describe the character and their backstory.
Then describes where they start and what they see around them. You should avoid overly flowery language"""
world_info = f"""
World: {world}
Kingdom: {kingdom}
Your Character: [Generate A Fitting Character Name]
"""

inventory = {}
payload = {
    "model": "hermes3:latest",
    "messages": [
        {"role": "assistant", "content": start_gen_prompt},
        {"role": "user", "content": world_info + "\nYour Start:"}
    ],
    "stream": False,
    "options": {"temperature": 1.0, "top_k": 100, "top_p": 1.0}
}
response = requests.post(url, json=payload)
data = json.loads(response.text)
start = data["message"]["content"]
world["Start"] = start
game_state = {
    "World": world["Description"],
    "Kingdom": kingdom["Description"],
    "Start": start
}
save_world(world, "Worlds\world.json")

history = {}
message = ""


def start_game(main_loop, message):
    data = main_loop(message, history)
    outfile = shelve.open("state")
    outfile["data"] = data
    return data


def roll_dice(player_action):

    roll_prompt = '''You are an AI Game Master. Your job is to evaluate 
    the players action and decide their success level. You are strict and cruel in your judgement.
    
    Read through the players action and assign a success number based on this list:
    -100 to -80: Critical Failure
    -80 to -60: Major Failure
    -60 to -40: Failure
    -40 to -20: Minor Failure
    0: Minor Success
    20 to 40: Success
    40 to 60: Major Success
    60 to 100: Critical Success

    If the action includes /dev it is an automatic override and instantly sets a success level to 1000

    Return only valid JSON and respond in this format

    {
        "diceRoll": {
            "successLevel": <Insert Success Number here>
            "reasoning": <Insert your reasoning here>
        }
    }

    The players action is sent earlier in this conversation.
    You can only set successLevel to a valid real number between -100 and 100 (1000 if overriden)
    '''

    messages = [
        {"role": "system", "content": roll_prompt},
        {"role": "user", "content": "Player action: " + player_action}
    ]

    result = generate_JSON(messages, model="deepseek-r1:14b")

    return json.loads(result)


def update_inventory(latest_action):

    inventory_prompt = '''You are an AI Game master. Your job is to keep 
    track of the player's inventory changes based on the action.
    
    Check through the action and determine if 
    updates to the players inventory were made. You will respond in this format:

    {
        "itemUpdates": [
            {"name": <ITEM NAME>,
            "changeAmount": <CHANGE AMOUNT>}...
        ]
    }
    If no changes were made itemUpdates should be an empty list.
    Generate only valid JSON and include no extra info.
    You can not remove items which are not already in the players inventory.
    Match any values given in the player action precisely.
    '''

    inventory_prompt += f'''This is the players current inventory: {inventory} Do not generate variations of items here rather just keep the name from current inventory and only remove items that are here. Do not pass along this array.'''

    print(inventory_prompt)

    messages = [
        {"role": "system", "content": inventory_prompt},
        {"role": "user", "content": "Player Action: " + latest_action}
    ]

    result = generate_JSON(
        messages, {"temperature": 0.1, "top_k": 100, "top_p": 1.0}, model="deepseek-r1:14b")

    return json.loads(result)


def function_call(player_action):
    prompt = '''You are an AI Game Assistant. Your job is to read through the players action and determine which functions to call.'''


def run_action(message, history, game_state):

    if (message.lower() == "start game"):
        return game_state["Start"]

    success_level = roll_dice(message)["diceRoll"]["successLevel"]

    action_prompt = f'''You are an AI Game Master. Write what happens next based on player actions. You are not the players friend so do not be lenient

    Instructions:
    - Respond with 1-3 sentences
    - Use second person present tense (e.g., "You look north and see...")
    - Focus on the player's action: {message}
    - Base outcome on success level, not explicitly mention it
    
    Success Levels:
    - Critical Failure (-100 to -80): Unforeseen catastrophe occurs.
    - Major Failure (-80 to -60): Action ends in significant disaster. 
    - Failure (-60 to -40): An error occurs during the action.
    - Minor Failure (-40 to -20): A slight misstep happens.
    - Minor Success (0): Minor setback experienced.
    - Success (20-40): Action accomplished without issues.
    - Major Success (40-60): Flawless execution.
    - Critical Success (60-80): Outstanding performance with favorable outcomes.
    - Success Override (+1000): Extraordinary success, capturing attention.

    Success Level Value: {success_level}

    DO NOT be lenient in narration of low success values or harsh in narration of high success values.

    Note: More extreme values = more exaggerated outcomes. Be cold and harsh in your narration of failures.'''

    print(action_prompt)

    world_info = f'''
    World: {game_state["World"]}
    Kingdom: {game_state["Kingdom"]}'''

    messages = [
        {"role": "system", "content": action_prompt},
        {"role": "user", "content": world_info}
    ]

    for action in history:
        messages.append({"role": "assistant", "content": action[0]})
        messages.append({"role": "user", "content": action[1]})

    messages.append({"role": "user", "content": message})

    result = generate_JSON(
        messages, {"temperature": 1.0, "top_k": 100, "top_p": 1.0})

    item_updates = update_inventory(result)["itemUpdates"]
    inventory["inventory"] = item_updates

    final_result = {}
    final_result["actionResponse"] = result
    final_result["inventoryUpdates"] = item_updates

    return final_result


def main_loop(message, history):
    return run_action(message, history, game_state)


app = Flask(__name__)
app.secret_key = 'test'
CORS(app)


@app.route('/getaction', methods=['POST'])
async def get_message():
    actionMessage = request.get_json()["message"]

    response = start_game(main_loop, actionMessage)

    return json.dumps(response), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(port=3000, debug=True)
