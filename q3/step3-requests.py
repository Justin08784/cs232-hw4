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

def code_success(code: int):
    return 200 <= code and code <= 299

def visit_url(dest: str):
    http_success = False        # http address reachable AND return code is a success?
    redirect = False            # http->https redirect? <valid IFF http_access>
    http_code = ""
    http_accessible = False     # http address accessible? 
    
    https_success = False       # https address reachable AND return code is a success?
    https_accessible = False    # https address accessible? 
    
    try:
        http_r = requests.get("http://" + dest, timeout=5)
        
        scheme = urlparse(http_r.url).scheme
        http_code = http_r.status_code
        
        http_success = code_success(http_code)
        match scheme:
            case "http":
                redirect = False
            case "https":
                redirect = True
            case _:
                print(f"Unknown scheme: {scheme}")
                exit(-1)
        
    except:
        http_success = False
    
    http_accessible = http_success and not redirect
    
    try:
        https_r = requests.get("https://" + dest, timeout=5)
        https_code = https_r.status_code
        
        https_success = code_success(https_code)
    except:
        https_success = False
    
    https_accessible = https_success
    
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
    process_df(df=topsites[:10], dest_path="Zstep3-topsites-requests.csv")
    
    othersites = pd.read_csv(repo_root + "/q0/step0-othersites.csv", header=None)
    process_df(df=othersites[:10], dest_path="Zstep3-othersites-requests.csv")