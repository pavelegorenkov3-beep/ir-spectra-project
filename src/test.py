import requests
import re 
from bs4 import BeautifulSoup

url = "https://webbook.nist.gov/cgi/cbook.cgi"
headers = {"User-Agent": "Mozilla/5.0 (school project)"}

r = requests.get(url, params={"Formula": "C2H6O", "NoIon": "on", "Units": "SI", "cIR": "on"}, headers=headers, timeout=40)
print("Search", r.status_code, "| lenght" , len(r.text))
print(r.text[:300])
print("----")

r = requests.get(url, params = {"JCAMP": "C64175", "Index": 0, "Type": "IR"}, headers=headers, timeout=40)
print("Spectra : code", r.status_code, "| has #TITLE:", "##TITLE" in r.text)
print(r.text[:300])

r = requests.get(url, params={"Formula": "C2H6O", "NoIon": "on", "Units": "SI", "cIR": "on"}, headers=headers, timeout=40)
soup = BeautifulSoup(r.text, "html.parser")

links = soup.find_all("a", href=True)
print("All links:", len(links))
for link in links[:15]:
    print(link["href"])
print("ID found:", re.findall(r"ID=(C\d+)", r.text)[:10])