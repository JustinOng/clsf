import re
import json
from pathlib import Path
from datetime import datetime
import requests

CTFD_HOST = "http://localhost:8000"
CTFD_ACCESS_TOKEN = "6fd362f67e2135a79f8f137d2174a274e411c5c30e06fd4a981f80de7cfdac92"

# Incorrect flags for challenges are stored here so that we don't retry again
SUBMISSION_FAILURE_STORE = "solve_submissions"

CTFD_HEADERS = {
    "Authorization": f'Token {CTFD_ACCESS_TOKEN}',
    "Content-Type": "application/json"
}


def extract_flag(inp):
    return re.findall(r'CYBERLEAGUE{.+?}', inp)


def submit_flag(challenge_name_regex, flag):
    r = requests.get(CTFD_HOST + "/api/v1/challenges", headers=CTFD_HEADERS)
    r.raise_for_status()

    challs = r.json()["data"]

    for chall in challs:
        if chall["solved_by_me"]:
            continue

        # Check whether we have attempted this chall:flag before
        # Crude solution making use of fs because of possible concurrent access with multiple scripts
        store_folder = Path(
            SUBMISSION_FAILURE_STORE) / f'{chall["id"]}'

        solve_attempted = False
        for p in store_folder.glob("fail_*"):
            with open(p) as f:
                if f.read().strip() == flag:
                    solve_attempted = True
                    break

        if solve_attempted:
            continue

        if re.search(challenge_name_regex, chall["name"]) is not None:
            r = requests.post(CTFD_HOST + "/api/v1/challenges/attempt", json={
                "challenge_id": chall["id"],
                "submission": flag
            }, headers=CTFD_HEADERS)
            r.raise_for_status()

            if r.json()["data"]["status"] == "correct":
                print(
                    f'Solved {chall["category"]}/{chall["name"]} with {flag}')
            else:
                print(
                    f'FAILED to solve {chall["category"]}/{chall["name"]} with {flag}')
                # Store details of this challenge and the failed flag so we do not attempt to
                #   submit this again
                store_folder.mkdir(parents=True, exist_ok=True)
                with open(store_folder / "challenge_info", "w") as f:
                    f.write(json.dumps(chall, indent=4))

                with open(store_folder / f'fail_{int(datetime.now().timestamp())}', "w") as f:
                    f.write(flag)

