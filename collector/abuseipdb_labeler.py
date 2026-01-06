import os
import requests

API_KEY = os.getenv("ABUSEIPDB_API_KEY")

def get_abuse_score(ip):
    if not API_KEY:
        return None

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": API_KEY,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    r = requests.get(url, headers=headers, params=params, timeout=15)

    if r.status_code != 200:
        return None

    return r.json().get("data", {}).get("abuseConfidenceScore")
