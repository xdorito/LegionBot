import json
from datetime import datetime


class BotStateManager:
    def __init__(self, filename='state.json'):
        self.filename = filename
        self.state = self.load_state()

    def save_state(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load_state(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_state = {'ELECTION_STARTED': False,
                             'CANDIDATES_ALLOWED': False,
                             'LAST_ANNOUNCE': int(datetime.now().timestamp())}
            with open(self.filename, 'w') as f:
                json.dump(default_state, f)
            return default_state

    def get_state(self, key):
        return self.state.get(key)

    def update_state(self, updates: dict):
        self.state.update(updates)
        self.save_state(self.state)
