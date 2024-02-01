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
    os.system("rm -rf /tmp/.com.google.Chrome.*")
    os.system("rm -rf /tmp/.org.chromium.Chromium.*")
    os.system("pkill chrome")
    os.system("pkill Xvfb")



def visit_url(dest: str):
    http_reached = False    # http address reachable?
    redirect = False        # http->https redirect? <ignore value unless http_reached>
    http_accessible = False # http address accessible? 
    http_code = ""
    
    https_accessible = False # https address accessible? 
    # print("dest", dest)
    
    # time.sleep(2)
    
    # display = Display(visible=0, size=(800, 600))
    # display.start()
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(5)
    
    try:
        driver.get("http://" + dest)
        http_reached = True
        
        scheme = urlparse(driver.current_url).scheme
        # print(f"dest: {dest}, currurl: {driver.current_url}, urlparse: {urlparse(driver.current_url)}")
        match scheme:
            case "http":
                redirect = False
            case "https":
                redirect = True
            case _:
                print(f"Unknown scheme: {scheme}")
                exit(-1)
        

    # except TimeoutException:
    #     http_reached = False
    except:
        http_reached = False
        pass
    finally:
        driver.quit()
    
    http_accessible = http_reached and not redirect
    
    # time.sleep(2)
    
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(5)
    
    try:
        driver.get("https://" + dest)
        https_accessible = True
    # except TimeoutException:
    #     https_accessible = False
    except:
        https_accessible = False
        pass
    finally:
        driver.quit()
    
    state = ""
    # print(http_accessible, https_accessible)
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



def process_df(df: pd.DataFrame, dest_path: str):
    df.columns = ["index", "url"]
    num_rows = df.shape[0]
    
    states = []
    df["state"] = ""
    
    f = open(dest_path, "a")
    
    for index, row in tqdm(df.iterrows()):
        url = row["url"]
        
        state = visit_url(url)
        # df.loc[index, "state"] = state
        print(f"{index+1}, url: {url}, state: {state}")
        states.append(state)
        addendum = ",".join([str(row["index"]), row["url"], state]) + "\n"
        f.write(addendum)
            
    f.close()
    
    return
    df["state"] = states
    
    df.to_csv(dest_path, index=False, header=False)
    
        
    
    
    
if __name__ == "__main__":
    kill_zombies()
    
    display = Display(visible=0, size=(800, 600))
    display.start()

    
    topsites = pd.read_csv(repo_root + "/q0/step0-topsites.csv", header=None)
    process_df(df=topsites[445:], dest_path="2LATESTstep3-topsites-selenium.csv")
    # I had to manually fill in row 446 (speedtest.net), 885 (biblegateway.com), 994 (split.io)
    # second run: row 446 (speedtest.net), 571,merriam-webster.com
    
    othersites = pd.read_csv(repo_root + "/q0/step0-othersites.csv", header=None)
    process_df(df=othersites, dest_path="2LATESTstep3-othersites-selenium.csv")
    # othersites ran without problem