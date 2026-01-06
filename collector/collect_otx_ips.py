import os
import requests
import time

OTX_API_KEY = os.getenv("OTX_API_KEY")
HEADERS = {"X-OTX-API-KEY": OTX_API_KEY}
BASE_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"

def fetch_otx_ips(limit=500):
    ips = set()
    page = 1

    while len(ips) < limit:
        params = {"page": page}
        r = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)

        if r.status_code != 200:
            print(f"[!] OTX error on page {page}")
            break

        results = r.json().get("results", [])
        if not results:
            break

        for pulse in results:
            for ind in pulse.get("indicators", []):
                if ind.get("type") == "IPv4":
                    ips.add(ind["indicator"])
                    if len(ips) >= limit:
                        return list(ips)

        page += 1
        time.sleep(1)  # avoid rate-limit

    return list(ips)
