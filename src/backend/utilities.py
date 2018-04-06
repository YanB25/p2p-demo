'''
utilities functions here
'''
import json
def objEncode(obj):
    return json.dumps(obj).encode('utf-8')
def objDecode(binary):
    return json.loads(binary.decode('utf-8'))