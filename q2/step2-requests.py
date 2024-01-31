import requests

destination = "chicagoreader.com"
print("\n\nExample of a site that redirects to HTTPS")
print("Attempting to load: http://" + destination)
r = requests.get("http://" + destination)
print("HTTP status code: " + str(r.status_code))
print("Final URL: " + r.url)
#print(r.text)

destination = "washington.edu"
print("\n\nExample of a site that does not redirect to HTTPS")
print("Attempting to load: http://" + destination)
r = requests.get("http://" + destination)
print("HTTP status code: " + str(r.status_code))
print("Final URL: " + r.url)
#print(r.text)

destination = "uchicago.edu"
print("\n\nExample of a site that returns a different HTTP status code")
print("Attempting to load: http://" + destination)
r = requests.get("http://" + destination)
print("HTTP status code: " + str(r.status_code))
print("Final URL: " + r.url)
#print(r.text)

customheaders = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
    "Accept-Encoding": "gzip, deflate", 
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8", 
    "Dnt": "0", 
    "Host": "uchicago.org", 
    "Upgrade-Insecure-Requests": "1", 
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
}
destination = "uchicago.edu"
print("\n\nA slight variant of the previous example that does something different")
print("Attempting to load: http://" + destination)
r = requests.get("http://" + destination, headers=customheaders)
print("HTTP status code: " + str(r.status_code))
print("Final URL: " + r.url)
#print(r.text)

destination = "itturnsoutgrantdoesnotlikehotdogs.fyi"
print("\n\nExample of an error")
print("Attempting to load: http://" + destination)
try:
    r = requests.get("http://" + destination)
    print("HTTP status code: " + str(r.status_code))
    print("Final URL: " + r.url)
except:
    print(destination + " failed")

destination = "squid-cache.org"
print("\n\nExample of a site that loads in HTTP, but not HTTPS")
print("Try HTTP")
print("Attempting to load: http://" + destination)
r = requests.get("http://" + destination)
print("HTTP status code: " + str(r.status_code))
print("Final URL: " + r.url)
#print(r.text)
print("Try HTTPS")
print("Attempting to load: https://" + destination)
try:
    r = requests.get("https://" + destination)
    print("HTTP status code: " + str(r.status_code))
    print("Final URL: " + r.url)
except:
    print("squid-cache.org failed")