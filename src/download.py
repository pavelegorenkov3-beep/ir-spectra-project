import time
import requests
from pathlib import Path
import pubchempy as pcp
import pandas as pd
import re
from bs4 import BeautifulSoup

NIST_URL = "https://webbook.nist.gov/cgi/cbook.cgi"

def download_spectrum(cas: str, output_dir: Path):
    print(f"Скачиваю {cas}...")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{cas}.jdx"

    if path.exists():
        print(f"File {cas} already exists. Skipping download.")
        return True

    params = {
        "JCAMP": "C" + cas.replace("-", ""),
        "Index": 0,
        "Type": "IR",
    }

    response = requests.get(NIST_URL, params=params, timeout=40)

    if response.status_code != 200 or "##TITLE" not in response.text:
        print(f"Failed to download spectrum for CAS {cas}.")
        return False

    path.write_text(response.text)
    print(f"Downloaded spectrum for CAS {cas} to {path}.")
    return True

def get_smiles(name):
    compound = pcp.get_compounds(name, "name")
    if compound:
        return compound[0].smiles
    return None

def search_cas_by_formula(formula):
    params = {
        "Formula": formula,
        "NoIon": "on",
        "Units": "SI",
        "cIR": "on", 
    }
    response = requests.get(NIST_URL, params=params, timeout=40)
    soup = BeautifulSoup(response.text, "html.parser")

    ids = set()
    for link in soup.find_all("a", href=True):
        match = re.search(r"ID=(C\d+)", link["href"])
        if match:
            ids.add(match.group(1))
    return list(ids)

def id_to_cas(nist_id):
    d = nist_id[1:]
    return f"{d[:-3]}-{d[-3:-1]}-{d[-1]}"

def make_formula(c, h, o, n, s):
    formula = ""
    for symbol, count in [("C", c), ("H", h), ("N", n), ("O", o), ("S", s)]:
        if count == 0:
            continue
        elif count == 1:
            formula+= symbol
        else:
            formula+= f"{symbol}{count}"
    return formula

def generate_formulas(max_c = 10):
    formulas = []
    for c in range(1, max_c + 1):
        for n in range(0, 2):
            for o in range(0, 3):
                for s in range(0,2):
                    for h in range(0, 2 * c + 2 + n + 1):
                        if (h + n) % 2 != 0:
                            continue
                        formulas.append(make_formula(c, h, o, n, s))    
    return formulas

def main():
    df = pd.read_csv("data/compounds.csv")
    raw_dir = Path("data/raw")

    smiles_list = []
    has_spectrum_list = []

    for name, cas in zip(df["name"], df["cas"]):
        has_spectrum = download_spectrum(cas, raw_dir)
        smiles = get_smiles(name)
        print(f" Name: {name}, {smiles} ")

        has_spectrum_list.append(has_spectrum)
        smiles_list.append(smiles)
        time.sleep(1.5)

    df["smiles"] = smiles_list
    df["has_spectrum"] = has_spectrum_list
    df.to_csv("data/compounds_with_smiles.csv", index=False)

if __name__ == "__main__":
    #main()
    f = generate_formulas()
    print(len(f))
    print("C2H6O" in f, "C6H14" in f, "C2H4O2" in f)