import json
import os

data = None
def load_data():
    global data
    with open('data.json', 'r') as f:
        data = json.load(f)

def save_data():
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)