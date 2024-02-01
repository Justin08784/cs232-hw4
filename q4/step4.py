import ssl
import socket
import OpenSSL
import pandas as pd
import os

from pprint import pprint
from tqdm import tqdm
from collections import namedtuple
import datetime

repo_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

algo_repr = {
    OpenSSL.crypto.TYPE_DSA : "TYPE_DSA",
    OpenSSL.crypto.TYPE_RSA : "TYPE_RSA",
    OpenSSL.crypto.TYPE_EC : "TYPE_EC"
}

ReturnStruct = namedtuple("ReturnStruct", "issuer period crypto_algo key_len rsa_exp sign_algo")

def visit_url(dest: str):
    pd.options.mode.chained_assignment = None  # default='warn'
    
    website = dest
    ctx = ssl.create_default_context()
    null_rv = ReturnStruct(issuer="", period="", crypto_algo="", key_len="", rsa_exp="", sign_algo="")
    
    conn_success = False
    try:
        connection = socket.create_connection((website, 443), timeout=5)
        # connection = socket.create_connection((website, 443), timeout=0.5)
    except:
        # print(f"1fail {dest}")
        return null_rv
    
    try:
        # print("my conn:", connection)
        s = ctx.wrap_socket(connection, server_hostname=website)
    except:
        # print(f"2fail {dest}")
        return null_rv
        
    try:
        cert = s.getpeercert(True)
        s.close()
        cert = ssl.DER_cert_to_PEM_cert(cert)
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert) 
    except:
        s.close()
        return null_rv
        
    issuer = x509.get_issuer().organizationName
    # print(f"Q12 Issuing CA: {issuer}\n")

    start = x509.get_notBefore()
    end = x509.get_notAfter()
    period = ""
    if start != None and end != None:
        start = datetime.datetime.strptime(start.decode("utf-8"), "%Y%m%d%H%M%SZ")
        end = datetime.datetime.strptime(end.decode("utf-8"), "%Y%m%d%H%M%SZ")
        period = (end - start).total_seconds()

    pkey = x509.get_pubkey()

    crypto_algo = algo_repr[pkey.type()]
    # print(f"Q14 Crypto. Algo: {crypto_algo}\n")
    
    key_len = pkey.bits()
    # print(f"Q15 Key Len: {key_len}\n")
    
    # pprint(vars(pkey))
    pub_nums = pkey.to_cryptography_key().public_numbers()
    rsa_exp = ""
    match pkey.type():
        case OpenSSL.crypto.TYPE_DSA:
            pass
        case OpenSSL.crypto.TYPE_RSA:
            rsa_exp = pub_nums.e
            pass
        case OpenSSL.crypto.TYPE_EC:
            pass
    # print(f"Q16 Public Numbers: {rsa_exp}, {pub_nums}\n")

    sign_algo = x509.get_signature_algorithm()
    # print(f"Q17 Sign. Algo: {sign_algo}\n")

    return ReturnStruct(issuer=issuer, period=period, crypto_algo=crypto_algo, key_len=key_len, rsa_exp=rsa_exp, sign_algo=sign_algo)

    
    

def process_df(df: pd.DataFrame, dest_path: str):
    df.columns = ["index", "url"]
    num_rows = df.shape[0]
    
    new_cols = {
        "issuer" : [],
        "period" : [],
        "crypto_algo" : [],
        "key_len" : [],
        "rsa_exp" : [],
        "sign_algo" : []
    }
    for url in tqdm(df["url"]):
    # for url in df["url"]:
        rv = visit_url(url)
        new_cols["issuer"].append(rv.issuer)
        new_cols["period"].append(rv.period)
        new_cols["crypto_algo"].append(rv.crypto_algo)
        new_cols["key_len"].append(rv.key_len)
        new_cols["rsa_exp"].append(rv.rsa_exp)
        new_cols["sign_algo"].append(rv.sign_algo)
    
    for colname in new_cols.keys():
        # df[colname] = new_cols[colname]
        df.loc[:, colname] = new_cols[colname]
    
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #     print(df)
        
    df.to_csv(dest_path, index=False, header=False)


if __name__ == "__main__":
    # df1=pd.read_csv("step4-topsites.csv", header=None)
    # print(df1)
    
    # df2=pd.read_csv("step4-othersites.csv", header=None)
    # print(df2)
    
    
    # exit()
    
    topsites = pd.read_csv(repo_root + "/q0/step0-topsites.csv", header=None)
    process_df(topsites, dest_path="step4-topsites.csv")
    # topsites.columns = ["index", "url"]
    
    othersites = pd.read_csv(repo_root + "/q0/step0-othersites.csv", header=None)
    process_df(othersites, dest_path="step4-othersites.csv")
    
    # i=0
    # for url in topsites["url"][:1]:
    # # for url in tqdm(topsites["url"]):
    #     rv = visit_url(url)
    #     # print(f"{i}: {rv}")
    #     i+=1
        
    # # visit_url("bingbadaboom.tyf")