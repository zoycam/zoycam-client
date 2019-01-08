import json
import random
import string

def fread(filename, mode):
    f = open(filename, mode)
    c = f.read()
    f.close()
    return c

def fwrite(filename, mode, content):
    f = open(filename, mode)
    f.write(content)
    f.close()

def serialize(command, payload):
    return json.dumps({"version" : 1,
                       "command" : command,
                       "payload" : payload}, sort_keys=True)

def deserialize(msg):
    parsed = json.loads(msg)
    if "command" in parsed and "payload" in parsed:
        return parsed["command"], parsed["payload"]
    else: return "", ""

def randstring(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
