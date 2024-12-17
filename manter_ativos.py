import time
import requests

sites = [
    "https://conversorcxrzin.onrender.com/"
]

def manter_sites_ativos():
    while True:
        for site in sites:
            requests.get(site, timeout=10)
            time.sleep(300)

if __name__ == "__main__":
    manter_sites_ativos()