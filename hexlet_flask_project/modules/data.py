import json

class Repository:
    def __init__(self, filepath):
        self.filepath = filepath

    def read_data(self):
        with open(self.filepath, 'r') as f:
            data = json.load(f)
        return data
    
    def save(self, final_data):
        with open(self.filepath, 'w') as f:
            json.dump(final_data, f)

    def get_data(self):
        return self.read_data()
    
    def find(self, id):
        users = self.read_data()
        result = []
        if len(users) == 0:
            return result
        for user in users:
            if user['id'] == int(id):
                break
        return user
    
    def delete(self, id):
        users = self.read_data()
        for user in users:
            if user['id'] == int(id):
                users.remove(user)
                break
        self.save(users)

