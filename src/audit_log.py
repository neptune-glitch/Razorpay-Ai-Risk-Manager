import json
import os
from datetime import datetime


AUDIT_FILE = "data/audit_log.json"


def save_action(
    transaction_id,
    action,
    risk_score,
    risk_level,
    reason
):
    os.makedirs(
        "data",
        exist_ok=True
    )

    record = {
        "transaction_id": transaction_id,
        "action": action,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reason": reason,
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        )
    }

    logs = []

    if os.path.exists(AUDIT_FILE):

        try:

            with open(
                AUDIT_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                logs = json.load(file)

        except (json.JSONDecodeError, FileNotFoundError):

            logs = []


    logs.append(record)


    with open(
        AUDIT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            logs,
            file,
            indent=4
        )


def load_actions():

    if not os.path.exists(AUDIT_FILE):

        return []


    try:

        with open(
            AUDIT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, FileNotFoundError):

        return []