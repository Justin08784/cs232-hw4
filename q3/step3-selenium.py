import requests
from enum import Enum
from urllib.parse import urlparse

import pandas as pd
import numpy as np

from tqdm import tqdm
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pyvirtualdisplay import Display

import time

repo_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class Encryption_State(Enum):
    HTTPSonly = 0
    both = 1
    HTTPonly = 2
    neither = 3
    
Enc_State_Repr = {
    Encryption_State.HTTPSonly : "HTTPSonly", 
    Encryption_State.both : "both", 
    Encryption_State.HTTPonly : "HTTPonly", 
    Encryption_State.neither : "neither"
}


def kill_zombies():
    all_cmds = "rm -rf /tmp/.com.google.Chrome.*; rm -rf /tmp/.org.chromium.Chromium.*; pkill chrome; pkill Xvfb"
    
    os.system("rm -rf /tmp/.com.google.Chrome.*")
    os.system("rm -rf /tmp/.org.chromium.Chromium.*")
    os.system("pkill chrome")
    os.system("pkill Xvfb")


class Crawler():
    def __init__(self):
        
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(5)
        self.driver = driver
                
        return

    def visit_url(self, dest: str):
        http_reached = False    # http address reachable?
        redirect = False        # http->https redirect? <ignore value unless http_reached>
        http_accessible = False # http address accessible? 
        http_code = ""
        
        https_accessible = False # https address accessible? 
        
        time.sleep(1.5)
        try:
            self.driver.get("http://" + dest)
            http_reached = True
            
            scheme = urlparse(self.driver.current_url).scheme
            
            match scheme:
                case "http":
                    redirect = False
                case "https":
                    redirect = True
                case _:
                    raise ValueError(f"Unknown scheme: {scheme}")
        except:
            http_reached = False
            pass
        
        http_accessible = http_reached and not redirect
        
        
        time.sleep(1.5)
        try:
            self.driver.get("https://" + dest)
            https_accessible = True
        except:
            https_accessible = False
            pass
        
        state = ""
        match (http_accessible, https_accessible):
            case (True, True):
                state = "both"
            case (True, False):
                state = "HTTPonly"
            case (False, True):
                state = "HTTPSonly"
            case (False, False):
                state = "neither"
        
        return state



    def process_df(self, df: pd.DataFrame, dest_path: str):
        df.columns = ["index", "url"]
        
        f = open(dest_path, "a")
        
        for index, row in df.iterrows():
            url = row["url"]
            
            print(f"{index+1}, url: {url}", flush=True)
            state = self.visit_url(url)
            print(f"->state: {state}", flush=True)
            addendum = ",".join([str(row["index"]), row["url"], state]) + "\n"
            f.write(addendum)
                
        f.close()

    def run(self):
        topsites = pd.read_csv(repo_root + "/q0/step0-topsites.csv", header=None)
        self.process_df(df=topsites.copy(), dest_path="step3-topsites-selenium.csv")
        
        othersites = pd.read_csv(repo_root + "/q0/step0-othersites.csv", header=None)
        self.process_df(df=othersites.copy(), dest_path="step3-othersites-selenium.csv")
        
        self.driver.quit()
        
    
        
    
    
    
if __name__ == "__main__":
    kill_zombies()
    
    display = Display(visible=0, size=(800, 600))
    display.start()

    crawler = Crawler()
    crawler.run()
    
    exit()
    
    
    
    