"""Metrik dan penalaran offline atas fixture, bukan sensor jaringan."""
import math
from collections import Counter


def classification(events, detected):
    actual = {row["source"] for row in events if row["attack"]}
    tp, fp, fn = len(detected & actual), len(detected - actual), len(actual - detected)
    return {"TP": tp, "FP": fp, "FN": fn, "precision": round(tp / (tp + fp), 3) if tp + fp else "tidak terdefinisi",
            "recall": round(tp / (tp + fn), 3) if tp + fn else "tidak terdefinisi"}


def entropy(value):
    if not value:
        return 0.0
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in Counter(value).values())


def string_list(obj, key):
    value = obj.get(key, [])
    if not isinstance(value, list) or len(value) > 32 or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{key} harus berupa array teks (maksimal 32 item).")
    return value
