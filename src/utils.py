import json
import pickle
import os

def dump_obj(obj,filename:str="exp"):
    if isinstance(obj,(dict,list,tuple)):
        os.makedirs('./artifacts/json',exist_ok=True)
        try:
            with open(f'./artifacts/json/{filename}.json','w') as f:
                json.dump(obj,f)
                return 1
        except Exception as e:
            raise e
    else:
        with open(f'./artifacts/{filename}.pkl','w') as f:
            pickle.dump(obj,f)
            return 