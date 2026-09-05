import os
import pandas as pd
from datetime import datetime


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIT_PATH = os.path.join(PROJECT_ROOT, "data", "audit_log.csv")


def log_investigator_action(
    transaction_id,
    risk_score,
    risk_level,
    ai_recommendation,
    investigator_decision,
    reason=""
):
    """
    Save an investigator decision to the audit log.
    """

    # Create directory if it doesn't exist
    os.makedirs(
        os.path.dirname(AUDIT_PATH),
        exist_ok=True
    )

    new_record = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "transaction_id": transaction_id,

        "risk_score": round(
            float(risk_score),
            2
        ),

        "risk_level": risk_level,

        "ai_recommendation": ai_recommendation,

        "investigator_decision":
            investigator_decision,

        "reason": reason
    }

    new_df = pd.DataFrame(
        [new_record]
    )

    # If audit log already exists, append
    if os.path.exists(AUDIT_PATH):

        new_df.to_csv(
            AUDIT_PATH,
            mode="a",
            header=False,
            index=False
        )

    else:

        new_df.to_csv(
            AUDIT_PATH,
            index=False
        )


def load_audit_log():

    if not os.path.exists(AUDIT_PATH):

        return pd.DataFrame(
            columns=[
                "timestamp",
                "transaction_id",
                "risk_score",
                "risk_level",
                "ai_recommendation",
                "investigator_decision",
                "reason"
            ]
        )

    return pd.read_csv(
        AUDIT_PATH
    )
