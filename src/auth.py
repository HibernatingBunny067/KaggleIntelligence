from dataclasses import dataclass,field
import json
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from src.logger import logging

loger = logging.getLogger(__name__)
@dataclass
class KaggleAuth:
    cookie_str:str|None = None
    session_file:str = "session.json"
    session: requests.Session = field(init=False)

    def __post_init__(self):
        os.makedirs('Artifacts/Session_Info',exist_ok=True)
        loger.info('Starting session.')
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent":"Mozilla/5.0",
            "content-type":"application/json"
        })

        if self._load_session():
            loger.info("Using cached session info.")
            return
        
        if self.cookie_str:
            loger.info("Fetching new session cookies.")
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

        with open(f'Artifacts/Session_Info/{self.session_file}','w') as f:
            json.dump(data,f)

    def _load_session(self):
        if not os.path.exists(f'Artifacts/Session_Info/{self.session_file}'):
            return False
        with open(f'Artifacts/Session_Info/{self.session_file}','r') as f:
            data = json.load(f)
        
        for k,v in data['cookies'].items():
            self.session.cookies.set(k,v)
        
        self._update_xsrf()

        return True

## DON'T LOOK AT THIS CODE !!!
# @dataclass
# class example:
#     cookies:Dict[str:str]
#     headers:Dict[str:str]