import json
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException

app = FastAPI()

model = joblib.load("model.pkl")

with open("feature_schema.json") as f:
    FEATURES = json.load(f)

@app.post("/predict")
def predict(data: dict):
    try:
        x = [data.get(f, 0) for f in FEATURES]
        x = np.array(x).reshape(1, -1)

        proba = model.predict_proba(x)[0]

        # 🔑 HANDLE SINGLE-CLASS MODELS
        if len(proba) == 1:
            # Only one class was seen during training
            # Treat it as max confidence in that class
            malicious_prob = float(proba[0])
            benign_prob = 1.0 - malicious_prob
        else:
            benign_prob = float(proba[0])
            malicious_prob = float(proba[1])

        risk_score = malicious_prob
        margin = abs(malicious_prob - benign_prob)

        if margin < 0.15:
            confidence = "low"
        elif margin < 0.35:
            confidence = "medium"
        else:
            confidence = "high"

        return {
            "risk_score": round(risk_score, 3),
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
