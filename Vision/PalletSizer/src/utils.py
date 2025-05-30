# src/utils.py
import json

def save_results(result, out_path):
    with open(out_path, "w") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
