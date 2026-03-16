import datetime
from src.client import KaggleClient
from typing import DefaultDict

class Collector:
    def __init__(self,client:KaggleClient):
        ''' 
        Takes a kaggle client and normalizes the data before processing
        '''
        self.client = client
        self.user_schema = None

        self._collect_()

    def collect(self):
        return self.user_schema
    
    def _collect_(self) -> None:
        profile = self.client.user_info

        activity = self.client.get_user_activity().get('activities',{})
        competitons = self.client.get_all_competitions() ##list of documents
        scripts = self.client.get_all_scripts()
        datasets = self.client.get_all_datasets()
        discussions = self.client.get_all_discussions()
        medals = self.client.get_medals()
        ranking = self.client.get_ranking_history()

        self.user_schema = {
            "profile":profile,
            "activity":activity,
            "competitions":competitons,
            "scripts":scripts,
            "datasets":datasets,
            "discussions":discussions,
            "medals":medals,
            "ranking":ranking
        }
        self._clean_activity()
        self._clean_competitions()
    
    def _clean_competitions(self):
        cleaned = []
        #for competitions in list of competitions
        for c in self.user_schema.get('competitions',[]):
            doc = c["competitionDocument"]
            # print(c)
            tags = None
            if "tags" in c.keys():
                tags = [x.get("name") for x in c['tags']]
            cleaned.append(
                {
                    "slug":c['slug'], ##name of the competition,
                    "title":c['title'],
                    "subtitle":c['subtitle'],
                    "rank":doc['teamRank'],
                    "teams":doc['teamCount'],
                    "deadline":doc['deadline'],
                    "prizeType":doc['prizeType'] if "prizeType" in doc.keys() else None,
                    "tags": tags 
                }
            )
        self.user_schema['competitions'] = cleaned
    
    # def _clean_activity(self):
    #     cleaned = []

    #     for a in self.user_schema.get('activity',[]):
    #         cleaned.append({
    #             "date":a['date'],
    #             "scripts":a.get("totalScriptsCount",0),
    #             "submissions":a.get("totalSubmissionsCount",0),
    #             "discussions":a.get('totalDiscussionsCount',0),
    #             "datasets":a.get("totalDatasetsCount",0)
    #         })

    #     self.user_schema['activity'] = cleaned

    def _clean_activity(self):
        activity = DefaultDict(lambda :{
            "scripts":0,
            "submissions":0,
            "discussions":0,
            "datasets":0
        })

        for a in self.user_schema.get('activity',[]):
            date = a['date']
            activity[date]["scripts"] += a.get('totalScriptCount',0)
            activity[date]['submissions'] += a.get('totalSubmissionsCount',0)
            activity[date]['discussions'] += a.get("totalDiscussionsCount",0)
            activity[date]['datasets']+= a.get("totalDatasetsCount",0)
        
        cleaned = []

        for date,data in activity.items():
            cleaned.append({
                "date" : datetime.fromisoformat(date.replace("z","")),
                **data
            })

        cleaned.sort(key=lambda x:x['date'])

        self.user_schema['activity'] = cleaned

