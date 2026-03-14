from src.auth import KaggleAuth
from src.client import KaggleClient
from src.utils import dump_obj
import requests

auth = KaggleAuth()
session = auth.session

client = KaggleClient(
    session=session,
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

# print((client.get_dashboard()))

dump_obj(client.get_dashboard(),'Abhishek_data')

