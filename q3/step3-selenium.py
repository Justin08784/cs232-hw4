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
        
        time.sleep(0.5)
        try:
            print("  trying " + dest)
            self.driver.get("http://" + dest)
            print("  try_succ " + dest)
            http_reached = True
            
            print("  parsing " + dest)
            scheme = urlparse(self.driver.current_url).scheme
            print("  parse_succ " + dest)
            # print(f"dest: {dest}, currurl: {self.driver.current_url}, urlparse: {urlparse(self.driver.current_url)}")
            
            print("  matching" + dest)
            match scheme:
                case "http":
                    print("  match 1" + dest)
                    redirect = False
                case "https":
                    print("  match 2" + dest)
                    redirect = True
                case _:
                    print("  match 3 (default)" + dest)
                    print(f"Unknown scheme: {scheme}")
                    exit(-1)
        except:
            print("  error " + dest)
            http_reached = False
            pass
        
        http_accessible = http_reached and not redirect
        
        
        time.sleep(0.5)
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
        num_rows = df.shape[0]
        
        states = []
        df["state"] = ""
        
        f = open(dest_path, "a")
        
        for index, row in df.iterrows():
            url = row["url"]
            
            print(f"{index+1}, url: {url}", end="", flush=True)
            state = self.visit_url(url)
            states.append(state)
            print(f", state: {state}", flush=True)
            addendum = ",".join([str(row["index"]), row["url"], state]) + "\n"
            f.write(addendum)
                
        f.close()
        
        return
        df["state"] = states
        
        df.to_csv(dest_path, index=False, header=False)

    def run(self):
        topsites = pd.read_csv(repo_root + "/q0/step0-topsites.csv", header=None)
        self.process_df(df=topsites[440:].copy(), dest_path="3LATESTstep3-topsites-selenium.csv")
        # I had to manually fill in row 446 (speedtest.net), 885 (biblegateway.com), 994 (split.io)
        # second run: row 446 (speedtest.net), 571,merriam-webster.com
        
        othersites = pd.read_csv(repo_root + "/q0/step0-othersites.csv", header=None)
        self.process_df(df=othersites.copy(), dest_path="3LATESTstep3-othersites-selenium.csv")
        # othersites ran without problem
        
        self.driver.quit()
        
    
        
    
    
    
if __name__ == "__main__":
    kill_zombies()
    
    display = Display(visible=0, size=(800, 600))
    display.start()

    crawler = Crawler()
    crawler.run()
    
    exit()
    
    
    
    