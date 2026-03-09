from client import KaggleClient
class UserCollector:
    def __init__(self,client:KaggleClient):
        self.client = client
    
    def collect(self):
        data = {}

        data['profile'] = self.client.user_info
        data['activity'] = self.client.get_user_activity()
        data['medals'] = self.client.get_medals()
        return data
    
