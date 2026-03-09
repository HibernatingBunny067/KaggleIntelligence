from typing import Literal
import time
class KaggleClient:
    BASE_URL = 'https://www.kaggle.com/api/i/'
    def __init__(self,session,auth,username):
        self.session = session
        self.auth = auth
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


    def _post(self, endpoint, payload, log_once=False):
        url = self.BASE_URL + endpoint
        key = (endpoint,str(payload))
        if key in self._cache:
            return self._cache[key]
        for attempt in range(3):

            try:

                start = time.time()

                response = self.session.post(
                    url,
                    json=payload,
                    headers=self.auth.headers,
                    cookies=self.auth.cookies,
                    timeout=15
                )

                end = time.time()

                if log_once:
                    print(f"[Kaggle API] {endpoint} ({end-start:.2f}s)")

                response.raise_for_status()
                data = response.json()
                self._cache[key] = data
                return data

            except Exception as e:

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
    def get_competitions(self):
        pass

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
    
    def _get_competitions(self, page_size=20, skip=0,log_once=False):

        payload = {
            "pageToken": "",
            "pageSize": page_size,
            "skip": skip,
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

        return self._post(
            "search.SearchContentService/ListSearchContent",
            payload,
            log_once
        )
    def get_all_competitions(self):
        competitons = []
        skip = 0
        page_size = 20
        first_call = True

        while True:
            data = self._get_competitions(page_size=page_size,skip=skip,log_once = first_call)
            first_call = False

            docs = data.get("documents",[])

            if not docs:
                break
            competitons.extend(docs)

            if len(docs) < page_size:
                break

            skip += page_size

        return competitons

    def get_dashboard(self):
        return {
            "profile":self.user_info,
            "activity":self.get_user_activity(),
            "medal":self.get_medals(),
            "competitions":self.get_all_competitions(),
            "ranking":self.get_ranking_history()
        }