import json

def save_state(data, filename = 'state.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_state(filename = 'state.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}