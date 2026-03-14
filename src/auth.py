from dataclasses import dataclass,field
import json
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

@dataclass
class KaggleAuth:
    cookie_str:str|None = None
    session_file:str = "session.json"
    session: requests.Session = field(init=False)

    def __post_init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent":"Mozilla/5.0",
            "content-type":"application/json"
        })

        if self._load_session():
            return
        
        if self.cookie_str:
            self._inject_cookie_string(self.cookie_str)
            self._update_xsrf()
            self._save_session()
            return
        self.refresh()
    
    def _inject_cookie_string(self,cookie_str):
        for parts in cookie_str.split(";"):
            k,v = parts.split().split("=",1)
            self.session.cookies.set(k,v)
    
    def _update_xsrf(self):
        xsrf = self.session.cookies.get('XSRF-TOKEN')
        
        if xsrf:
            self.session.headers['x-xsrf-token'] = xsrf

    def refresh(self):
        options = Options()

        options.add_argument("--headless=new")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service,options=options)

        try:
            driver.get("https://www.kaggle.com/harrykesh")
            cookies = driver.get_cookies()

            self.session.cookies.clear()

            for c in cookies:
                self.session.cookies.set(
                    c['name'],
                    c['value']
                )

            self._update_xsrf()
            self._save_session()

        finally:
            driver.quit()

    def _save_session(self):
        data = {
            "cookies":self.session.cookies.get_dict()
        }

        with open(self.session_file,'w') as f:
            json.dump(data,f)

    def _load_session(self):
        if not os.path.exists(self.session_file):
            return False
        with open(self.session_file,'r') as f:
            data = json.load(f)
        
        for k,v in data['cookies'].items():
            self.session.cookies.set(k,v)
        
        self._update_xsrf()

        return True

## DON'T LOOK AT THIS CODE !!!
# @dataclass
# class example:
#     cookies = {"cookie":"ka_sessionid=97cbe512285d5d27ef0070809bf46be0; GCLB=CPWE--DSqYCrCxAD; ACCEPTED_COOKIES=true; __Host-KAGGLEID=CfDJ8MXf3ve5BXlLqj3to84NtJolsAPIfw4rVchoxI4K6vpQFNtNe-gE6FzSuXcTClh9YQCKUSgiZQdkq4Re_zfub7Hkh1iW-l-WSUMSzAGLcPHibA1_gSQE37n1; CSRF-TOKEN=CfDJ8MXf3ve5BXlLqj3to84NtJqAfcBQDWQD5bgh6FXWJz4kDY3K-dbNC1eNdH0M6dOIHD6uGYND2bN6uq95dI2OvSaQBIIVo8evHbWBHLgBTw; build-hash=5f6b9e021a8bda18f03caa862f3ef9064d9f1d1b; ka_db=CfDJ8MXf3ve5BXlLqj3to84NtJpOcaM0u_opxfJdArt4i92Y_1PFzOh6RsUz7t2v6tLA40XEiXgy34kISCU8D54eO_w6D-HBUERZzGVSATuC6kgMNV5_Z6EbJ1njXaY; XSRF-TOKEN=CfDJ8MXf3ve5BXlLqj3to84NtJqKJNK1mmg7SANAaIRbuDLHX-IVw7TCqLo4e-Qg1OmuGjuc3XGSqWsYPaW2KF3sBbserd32DHPzY-Eb0sH1G09SgrRwZQfElo8Yxibv02NroTVtn0cwy8zZm7rv5MjZVlU; CLIENT-TOKEN=eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJpc3MiOiJrYWdnbGUiLCJhdWQiOiJjbGllbnQiLCJzdWIiOiJoYXJyeWtlc2giLCJuYnQiOiIyMDI2LTAzLTA5VDE2OjQ0OjI4LjA1Mjc5NDVaIiwiaWF0IjoiMjAyNi0wMy0wOVQxNjo0NDoyOC4wNTI3OTQ1WiIsImp0aSI6IjE2OTY2NmJlLWVjMjEtNDVjNi05YmE4LWJhYTRiODE1ZDkxOCIsImV4cCI6IjIwMjYtMDQtMDlUMTY6NDQ6MjguMDUyNzk0NVoiLCJ1aWQiOjIxMTM5MjU2LCJkaXNwbGF5TmFtZSI6ImhhcnJ5a2VzaDA2NyIsImVtYWlsIjoiaGFyaWtlc2h2NjMwQGdtYWlsLmNvbSIsInRpZXIiOiJleHBlcnQiLCJ2ZXJpZmllZCI6dHJ1ZSwicHJvZmlsZVVybCI6Ii9oYXJyeWtlc2giLCJ0aHVtYm5haWxVcmwiOiJodHRwczovL3N0b3JhZ2UuZ29vZ2xlYXBpcy5jb20va2FnZ2xlLWF2YXRhcnMvdGh1bWJuYWlscy8yMTEzOTI1Ni1rZy5qcGc_dD0yMDI2LTAyLTAzLTA1LTA0LTI4IiwiZmZoIjoiN2RmNzM0ODdjOTgxOTkxODk0MTAzYjFjZGQ4YTIxYjNkODAxNjg5ZTkxOTI4ZmU5ZWY4MTU3YmY0N2QzMDQ4ZCIsInBpZCI6ImthZ2dsZS0xNjE2MDciLCJzdmMiOiJ3ZWItZmUiLCJzZGFrIjoiQUl6YVN5QTRlTnFVZFJSc2tKc0NaV1Z6LXFMNjU1WGE1SkVNcmVFIiwiYmxkIjoiNWY2YjllMDIxYThiZGExOGYwM2NhYTg2MmYzZWY5MDY0ZDlmMWQxYiJ9"}
#     headers = {
#     "User-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
#     "content-type":"application/json",
#     "x-xsrf-token":"CfDJ8MXf3ve5BXlLqj3to84NtJqKJNK1mmg7SANAaIRbuDLHX-IVw7TCqLo4e-Qg1OmuGjuc3XGSqWsYPaW2KF3sBbserd32DHPzY-Eb0sH1G09SgrRwZQfElo8Yxibv02NroTVtn0cwy8zZm7rv5MjZVlU",
#     }