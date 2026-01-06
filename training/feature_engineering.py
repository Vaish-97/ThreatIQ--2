def extract_features(otx):
    pulses = otx.get("pulse_info", {}).get("pulses", [])

    pulse_count = len(pulses)
    malware_count = sum(
        1 for p in pulses if "malware" in [t.lower() for t in p.get("tags", [])]
    )

    return {
        "pulse_count": int(pulse_count),
        "malware_count": int(malware_count),
        "confidence_score": min(pulse_count * 10, 100),
        "is_tor": int("tor" in str(otx).lower()),
        "country_risk": 0.5,      # placeholder (numeric)
        "asn_reputation": 0.5     # placeholder (numeric)
    }
