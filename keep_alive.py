# TaskForge-Bot - Developed by Mohit
# GitHub: https://github.com/Mohit-Mano06/TaskForge-Bot
# License: MIT

# This file is used to keep the bot up on render by http request at a set interval


from flask import Flask
from threading import Thread
import os


app = Flask('')

@app.route('/')
def home():
    return {
        "status": "online",
        "bot": "TaskForge"
    }

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port = port)

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()