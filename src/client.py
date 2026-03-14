import requests
from typing import Literal,Union
import time
from src.logger import logging

logger = logging.getLogger(__name__)

class KaggleClient:
    BASE_URL = 'https://www.kaggle.com/api/i/'
    def __init__(self,session:requests.Session,username):
        self.session = session
        self.username = username
        self.user_info = {}
        self.user_id = None
        self._cache = {}
        self._get_user_info()

    def _get_user_info(self) -> None:
        payload = {
            "relativeUrl":f"/{self.username}"
        }
        data = self._post(
            "routing.RoutingService/GetPageDataByUrl",
            payload=payload
        )  
        
        profile = data.get("userProfile",{})
        self.user_info = profile
        self.user_id = profile.get('userId')
        print('UserId: {id}'.format(id = self.user_id))


    def _post(self, endpoint, payload, log_once=False) -> Union[dict,list[dict]]:
        logger.info(f"Request to Endpoint: {endpoint}")
        url = self.BASE_URL + endpoint
        key = (endpoint,str(payload))
        if key in self._cache:
            logger.info(f'Returning cached result.')
            return self._cache[key]
        for attempt in range(3):
            logger.info('Attempting the request.')
            try:

                start = time.time()

                response = self.session.post(
                    url,
                    json=payload,
                    # headers=self.auth.headers,
                    # cookies=self.auth.cookies,
                    timeout=15
                )

                end = time.time()

                if log_once:
                    print(f"[Kaggle API] {endpoint} ({end-start:.2f}s)")

                response.raise_for_status()
                data:dict = response.json()
                self._cache[key] = data
                return data

            except Exception as e:
                logger.warning(f'Exception raise: {e}')
                if attempt == 2:
                    raise

                time.sleep(1)
    
    def get_page_data(self,relativeurl):
        payload = {
            'relativeUrl':relativeurl
        }
        return self._post(
            "routing.RoutingService/GetPageDataByUrl",
            payload=payload
        )
    
    def get_user_activity(self):
        payload = {
            'userName':self.username
        }
        return self._post(
            "users.ProfileService/GetUserActivity",
            payload=payload
        )
    def get_recent_submission(self,activity = Literal['EDITED','VIEWED'],item_count=5):
        payload = {
            "userId":self.user_id,
            "returnedType":activity,
            "itemCount":item_count
        }
        return self._post(
            "users.RecentlyViewedService/GetRecentlyViewedItems",
            payload=payload
        )

    def get_medals(self):
        payload = {
            "userId":self.user_id
        }
        return self._post(
            "users.RankingService/GetUserMedalCounts",
            payload=payload
        )

    def get_followers(self):
        payload = {
            "userId":self.user_id,
            "pageSize":8,
            "userIdType":"FROM_USER"
        }
        return self._post(
            "users.ProfileService/ListFollowers",
            payload=payload
        )
    def get_following(self):
        payload = {
            "userId":self.user_id,
            "pageSize":8,
            "userIdType":"TO_USER"
        }
        return self._post(
            'users.ProfileService/ListFollowers',
            payload=payload
        )
    def get_ranking_history(self):
        payload = {
            "userId":self.user_id
        }
        return self._post(
            "users.RankingService/GetUserRankingHistory",
            payload=payload
        )
    
    def _paginate(self,endpoint:str,payload:dict,page_size:int=20) -> list[dict]:
        result = []
        skip = 0
        first_call = True

        while True:
            payload['pageSize'] = page_size
            payload['skip'] = skip

            data = self._post(endpoint,payload,log_once=first_call)
            first_call = False

            docs = data.get('documents',[])

            if not docs:
                break
            result.extend(docs)

            if len(docs) < page_size:
                break
            skip += page_size
        return result

    def get_all_competitions(self) ->list[dict]:
        payload = {
            "pageToken": "",
            "pageSize":"",
            "competitionsOrderBy": "SEARCH_COMPETITIONS_ORDER_BY_TEAM_RANK",
            "filters": {
                "query": "",
                "documentTypes": ["COMPETITION"],
                "listType": "LIST_TYPE_USER_PROFILE",
                "privacy": "PUBLIC",
                "ownerUserId": self.user_id,
                "ownerType": "OWNER_TYPE_OWNS",
                "competitionFilters": {
                    "role": "SEARCH_COMPETITIONS_ROLE_PARTICIPANT_ONLY",
                    "status": "SEARCH_COMPETITIONS_STATUS_COMPLETE",
                    "profileVisibility": "SEARCH_COMPETITIONS_PROFILE_VISIBILITY_VISIBLE"
                }
            }
        }

        return self._paginate(
            "search.SearchContentService/ListSearchContent",
            payload
        )

    def get_all_scripts(self) ->list[dict[str,Union[str,dict[str,str]]]]:
        payload = {
            "pageToken": "",
            "pageSize":"",
            "competitionsOrderBy": "LIST_SEARCH_CONTENT_ORDER_BY_VOTES",
            "filters": {
                "query": "",
                "documentTypes": ["KERNEL"],
                "listType": "LIST_TYPE_USER_PROFILE",
                "privacy": "PUBLIC",
                "ownerUserId": self.user_id,
                "ownerType": "OWNER_TYPE_UNSPECIFIED",
                "discussionFilters":{
                    "onlyNewComments":False,
                    "sourceType":"SEARCH_DISCUSSIONS_SOURCE_TYPE_UNSPECIFIED",
                    "writeUpInclusionType":"WRITE_UPP_INCLUSION_TYPE_INCLUDE"
                }
            }
        }

        return self._paginate(
            "https://www.kaggle.com/api/i/search.SearchContentService/ListSearchContent",
            payload
        )

    def get_all_datasets(self):
        ...
    def get_all_discussions(self): 
        ...

    def get_dashboard(self):
        return {
            "profile":self.user_info,
            "activity":self.get_user_activity(),
            "medal":self.get_medals(),
            "competitions":self.get_all_competitions(),
            "ranking":self.get_ranking_history()
        }