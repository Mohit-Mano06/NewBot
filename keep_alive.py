# This file is used to keep the bot up on render by http request at a set interval


from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is still online"

def run():
    app.run(host='0.0.0.0', port = 100000)

def keep_alive():
    t = Thread(target=run)
    t.start()