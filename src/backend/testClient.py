import socket 
import json
import utilities
data = {
    'name': 'benson',
    'age': 18
}
json_data = json.dumps(data)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5005))
s.send(utilities.objEncode({
    'name': 'benson',
    'age' : 18
}))
s.close()