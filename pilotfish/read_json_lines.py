import json
import re

filename = 'received_request.json'

with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()

# Extrait tous les objets JSON entre accolades {}
json_objects = re.findall(r'\{.*?\}', content)

for obj_str in json_objects:
    try:
        data = json.loads(obj_str)
        print(data)
    except json.JSONDecodeError as e:
        print("Erreur JSON sur cet objet:", e)
