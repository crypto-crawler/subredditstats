import json
import logging
import lzma
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

logging.basicConfig(level=logging.INFO)

with open("config.json", "rt") as f:
    SUBREDDIT_LIST = json.loads(f.read())


def read_last_line(file_path: str) -> Optional[str]:
    if not os.path.exists(file_path):
        return None
    with lzma.open(file_path, mode="rt") as f_in:
        last_line = None
        for line in f_in:
            last_line = line
        return last_line


def today_exists(name: str) -> bool:
    file_path = os.path.join("./data", name + ".json.xz")
    last_line = read_last_line(file_path)
    if last_line is None:
        return False
    else:
        obj = json.loads(last_line)
        last_day = datetime.utcfromtimestamp(obj["createdAt"] / 1000.0).isoformat()[:10]
        today = datetime.utcnow().isoformat()[:10]
        return last_day >= today


def get_subredditstats(name: str) -> Optional[Dict[str, Any]]:
    url = f"https://subredditstats.com/api/subreddit?name={name}"
    resp = requests.get(url=url)
    if resp.status_code == 200:
        logging.info(name)
        data = resp.json()
        data["createdAt"] = int(time.time() * 1000)
        return data
    else:
        logging.warning(name)
        logging.warning(resp.status_code)
        logging.warning(resp.text)
        if resp.status_code == 429:
            exit(0)
        return None


if __name__ == "__main__":
    for name in SUBREDDIT_LIST:
        if today_exists(name):
            logging.info(f"Skipping {name} because it is already updated today")
            continue
        info = get_subredditstats(name)
        if info:
            with lzma.open(os.path.join("./data", name + ".json.xz"), "at") as f_out:
                f_out.write(json.dumps(info) + "\n")
        # time.sleep(1)
