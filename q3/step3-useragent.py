import requests
from enum import Enum
from urllib.parse import urlparse

import pandas as pd
import numpy as np

from tqdm import tqdm
import os


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



customheaders = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
    "Dnt": "0", 
    "Host": "uchicago.org", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
}


def visit_url(dest: str):
    http_reached = False    # http address reachable?
    redirect = False        # http->https redirect? <valid IFF http_access>
    http_accessible = False # http address accessible? 
    http_code = -1
    
    https_accessible = False # https address accessible? 
    
    try:
        http_r = requests.get("http://" + dest, timeout=5, headers=customheaders)
        http_reached = True
        
        scheme = urlparse(http_r.url).scheme
        http_code = http_r.status_code
        match scheme:
            case "http":
                redirect = False
            case "https":
                redirect = True
            case _:
                print(f"Unknown scheme: {scheme}")
                exit(-1)
        
    except:
        http_reached = False
    
    http_accessible = http_reached and not redirect
    
    try:
        https_r = requests.get("https://" + dest, timeout=5, headers=customheaders)
        https_accessible = True
    except:
        https_accessible = False
    
    state = None
    match (http_accessible, https_accessible):
        case (True, True):
            state = "both"
        case (True, False):
            state = "HTTPonly"
        case (False, True):
            state = "HTTPSonly"
        case (False, False):
            state = "neither"
    
    return state, http_code


def process_df(df: pd.DataFrame, dest_path: str):
    df.columns = ["index", "url"]
    num_rows = df.shape[0]
    
    states = []
    codes = []
    for url in tqdm(df["url"]):
        state, http_code = visit_url(url)
        states.append(state)
        codes.append(http_code)
    df["state"] = states
    df["code"] = codes
    
    df.to_csv(dest_path, index=False, header=False)
    
        
    
    
    

    
if __name__ == "__main__":
    topsites = pd.read_csv(repo_root + "/q0/step0-topsites.csv", header=None)
    process_df(df=topsites, dest_path="step3-topsites-useragent.csv")
    
    othersites = pd.read_csv(repo_root + "/q0/step0-othersites.csv", header=None)
    process_df(df=othersites, dest_path="step3-othersites-useragent.csv")