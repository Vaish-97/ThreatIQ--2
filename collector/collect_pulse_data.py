import os
import json
import time
import requests
from pathlib import Path
from requests.exceptions import ReadTimeout, RequestException

OTX_API_KEY = os.getenv("OTX_API_KEY")
HEADERS = {"X-OTX-API-KEY": OTX_API_KEY}
URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"

DATASET_PATH = Path("../dataset/pulse_dataset.jsonl")
DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)

MAX_RETRIES = 3
BASE_SLEEP = 5  # seconds


def load_existing_ips():
    if not DATASET_PATH.exists():
        return set()

    ips = set()
    with open(DATASET_PATH, "r") as f:
        for line in f:
            ips.add(json.loads(line)["ip"])
    return ips


def extract_features_from_pulse(pulse):
    tags = [t.lower() for t in pulse.get("tags", [])]

    return {
        "pulse_count": 1,
        "malware_count": int("malware" in tags),
        "confidence_score": min(len(tags) * 10, 100),
        "is_tor": int("tor" in tags),
        "country_risk": 0.5,
        "asn_reputation": 0.5
    }


def fetch_page(page):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return requests.get(
                URL,
                headers=HEADERS,
                params={"page": page},
                timeout=15
            )
        except ReadTimeout:
            print(f"[!] Timeout on page {page} (attempt {attempt})")
            time.sleep(BASE_SLEEP * attempt)
        except RequestException as e:
            print(f"[!] Request error on page {page}: {e}")
            return None

    return None


def collect(limit=50):
    existing_ips = load_existing_ips()
    collected = 0
    page = 1

    print(f"[+] Existing IPs in dataset: {len(existing_ips)}")

    while collected < limit:
        response = fetch_page(page)

        if response is None or response.status_code != 200:
            print("[!] Stopping collection due to repeated failures")
            break

        results = response.json().get("results", [])
        if not results:
            print("[!] No more pulses available")
            break

        with open(DATASET_PATH, "a") as out:
            for pulse in results:
                for ind in pulse.get("indicators", []):
                    if ind.get("type") != "IPv4":
                        continue

                    ip = ind["indicator"]
                    if ip in existing_ips:
                        continue

                    features = extract_features_from_pulse(pulse)
                    label = 1 if features["malware_count"] else 0

                    out.write(json.dumps({
                        "ip": ip,
                        "features": features,
                        "label": label
                    }) + "\n")

                    existing_ips.add(ip)
                    collected += 1

                    if collected >= limit:
                        break

        page += 1
        time.sleep(3)  # polite pacing

    print(f"[✓] Collected {collected} new samples")


if __name__ == "__main__":
    collect(limit=50)
