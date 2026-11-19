import requests
from pathlib import Path

NIST_URL = "https://webbook.nist.gov/cgi/cbook.cgi"

def download_spectrum(cas: str, output_dir: Path):
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

if __name__ == "__main__":
    download_spectrum("64-19-7", Path("data/raw"))
    
