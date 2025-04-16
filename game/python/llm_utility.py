import requests
import gradio as gr
import random
import json
import shelve
import time
from flask import Flask, request
from flask_cors import CORS
import world_utility as helper
from world_utility import load_world, save_world


def generate_JSON(messages, options={"temperature": 1.0, "top_k": 100, "top_p": 1.0}, model="hermes3:latest"):
    payload = {
        "model": "hermes3:latest",
        "messages": messages,
        "stream": False,
        "options": options
    }
    response = requests.post("http://localhost:11434/api/chat", json=payload)
    data = json.loads(response.text)
    result = data["message"]["content"]

    return result
