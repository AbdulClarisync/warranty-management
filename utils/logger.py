import json
import os
from datetime import datetime

def save_log(file_name, task_type, tokens, duration, parsed_result):
    log = {
        "timestamp": datetime.now().isoformat(),
        "file": file_name,
        "task": task_type,
        "tokens": tokens,
        "duration_sec": round(duration, 2),
        "output_summary": parsed_result
    }

    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_log.json", "w") as f:
        json.dump(log, f, indent=2)
