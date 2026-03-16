from src import *

auth = KaggleAuth()
session = auth.session

client = KaggleClient(
    session=session,
    username='abhishek'
)

collector = Collector(client)

features = FeatureExtractor(collector)
feats = features.build()
print('\n')
print(feats)
dump_obj(feats)
