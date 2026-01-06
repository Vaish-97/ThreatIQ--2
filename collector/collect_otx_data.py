import os
import requests

OTX_API_KEY = os.getenv("OTX_API_KEY")
HEADERS = {"X-OTX-API-KEY": OTX_API_KEY}

BASE_URL = "https://otx.alienvault.com/api/v1/indicators/IPv4"

def fetch_ip_data(ip):
    url = f"{BASE_URL}/{ip}/general"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()
