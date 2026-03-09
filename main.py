import json
from auth import example
from client import KaggleClient
from collector import UserCollector
from features import extract
from analysis import classify_user
from visualizer import radar_chart
import requests

session = requests.Session()

client = KaggleClient(
    session,
    auth=example,
    username='abhishek'
)

# collector = UserCollector(client)

# data = collector.collect()

# features = extract(data)

# archetype = classify_user(features)

# print("User:", client.username)
# print("Archetype:", archetype)
# print("Features:", features)

# radar_chart(features)

print((client.get_dashboard()))

with open('example.json','w') as f:
    json.dump(client.get_dashboard(),f)
