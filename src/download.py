import time
import requests
from pathlib import Path
import pubchempy as pcp
import pandas as pd

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
    main()  