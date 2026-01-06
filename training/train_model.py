import json
import joblib
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier

# 🚫 NO API IMPORTS
# 🚫 NO NETWORK CALLS

DATASET_PATH = Path("../dataset/pulse_dataset.jsonl")

FEATURE_SCHEMA = [
    "pulse_count",
    "malware_count",
    "confidence_score",
    "is_tor",
    "country_risk",
    "asn_reputation"
]

X, y = [], []

if not DATASET_PATH.exists():
    raise RuntimeError("Dataset not found. Run collector first.")

with open(DATASET_PATH, "r") as f:
    for line in f:
        row = json.loads(line)
        features = row["features"]
        label = row["label"]

        X.append([features[f] for f in FEATURE_SCHEMA])
        y.append(label)

X = np.array(X)
y = np.array(y)

print(f"[+] Training samples loaded: {len(X)}")

if len(X) == 0:
    raise RuntimeError("Dataset is empty. Cannot train.")

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    class_weight="balanced",
    random_state=42
)

model.fit(X, y)

joblib.dump(model, "model.pkl")

with open("feature_schema.json", "w") as f:
    json.dump(FEATURE_SCHEMA, f, indent=2)

print("[✓] Model trained successfully (offline)")
