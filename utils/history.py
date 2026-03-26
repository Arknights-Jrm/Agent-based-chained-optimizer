import json

def save_history(history_params, history_perf, filename="optimization_history.json"):
    data = {
        "params": history_params,
        "performance": history_perf
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)