import os
import pandas as pd
from datetime import datetime


# ============================================================
# INVESTIGATION QUEUE
# ============================================================

QUEUE_PATH = "data/investigation_queue.csv"


QUEUE_COLUMNS = [
    "timestamp",
    "transaction_id",
    "merchant_id",
    "amount",
    "risk_score",
    "risk_level",
    "status",
    "reason"
]


# ============================================================
# ADD TRANSACTION TO QUEUE
# ============================================================

def add_to_investigation_queue(transaction, risk_result):

    os.makedirs(
        os.path.dirname(QUEUE_PATH),
        exist_ok=True
    )

    record = {
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "transaction_id": transaction.get(
            "transaction_id",
            "UNKNOWN"
        ),

        "merchant_id": transaction.get(
            "merchant_id",
            "UNKNOWN"
        ),

        "amount": transaction.get(
            "amount",
            0
        ),

        "risk_score": round(
            float(
                risk_result.get(
                    "risk_score",
                    0
                )
            ),
            2
        ),

        "risk_level": risk_result.get(
            "risk_level",
            "UNKNOWN"
        ),

        "status": "PENDING",

        "reason": "; ".join(
            risk_result.get(
                "reasons",
                []
            )
        )
    }

    new_df = pd.DataFrame(
        [record],
        columns=QUEUE_COLUMNS
    )

    # --------------------------------------------------------
    # If file exists, append
    # --------------------------------------------------------

    if os.path.exists(QUEUE_PATH):

        existing_df = pd.read_csv(
            QUEUE_PATH
        )

        # Make sure existing file has correct columns
        if list(existing_df.columns) != QUEUE_COLUMNS:

            existing_df = pd.DataFrame(
                columns=QUEUE_COLUMNS
            )

        combined_df = pd.concat(
            [
                existing_df,
                new_df
            ],
            ignore_index=True
        )

        combined_df.to_csv(
            QUEUE_PATH,
            index=False
        )

    else:

        new_df.to_csv(
            QUEUE_PATH,
            index=False
        )


# ============================================================
# LOAD INVESTIGATION QUEUE
# ============================================================

def load_investigation_queue():

    if not os.path.exists(QUEUE_PATH):

        return pd.DataFrame(
            columns=QUEUE_COLUMNS
        )

    try:

        df = pd.read_csv(
            QUEUE_PATH
        )

    except Exception:

        return pd.DataFrame(
            columns=QUEUE_COLUMNS
        )

    # --------------------------------------------------------
    # Repair missing columns
    # --------------------------------------------------------

    for column in QUEUE_COLUMNS:

        if column not in df.columns:

            if column == "status":

                df[column] = "PENDING"

            elif column == "risk_score":

                df[column] = 0.0

            elif column == "amount":

                df[column] = 0.0

            else:

                df[column] = ""

    # --------------------------------------------------------
    # Keep only expected columns
    # --------------------------------------------------------

    df = df[
        QUEUE_COLUMNS
    ]

    return df


# ============================================================
# LOAD PENDING INVESTIGATIONS
# ============================================================

def load_pending_investigations():

    df = load_investigation_queue()

    if df.empty:

        return df

    return df[
        df["status"]
        .astype(str)
        .str.upper()
        == "PENDING"
    ].copy()


# ============================================================
# UPDATE INVESTIGATION STATUS
# ============================================================

def update_investigation_status(
    transaction_id,
    status
):

    df = load_investigation_queue()

    if df.empty:

        return False

    valid_statuses = [
        "PENDING",
        "INVESTIGATING",
        "APPROVED",
        "BLOCKED",
        "REVIEW"
    ]

    status = status.upper()

    if status not in valid_statuses:

        raise ValueError(
            f"Invalid status: {status}"
        )

    mask = (
        df["transaction_id"].astype(str)
        == str(transaction_id)
    )

    if not mask.any():

        return False

    df.loc[
        mask,
        "status"
    ] = status

    df.to_csv(
        QUEUE_PATH,
        index=False
    )

    return True


# ============================================================
# REMOVE FROM QUEUE
# ============================================================

def remove_from_investigation_queue(
    transaction_id
):

    df = load_investigation_queue()

    if df.empty:

        return False

    original_length = len(df)

    df = df[
        df["transaction_id"].astype(str)
        != str(transaction_id)
    ]

    if len(df) == original_length:

        return False

    df.to_csv(
        QUEUE_PATH,
        index=False
    )

    return True


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("       INVESTIGATION QUEUE TEST")
    print("==========================================")

    test_transaction = {

        "transaction_id":
            "QUEUE_TEST_001",

        "merchant_id":
            "MERCHANT_001",

        "amount":
            750
    }

    test_risk_result = {

        "risk_score":
            65.5,

        "risk_level":
            "MEDIUM",

        "reasons":
            [
                "High transaction velocity",
                "Multiple behavioral risk signals detected"
            ]
    }

    # --------------------------------------------------------
    # Add transaction
    # --------------------------------------------------------

    add_to_investigation_queue(
        test_transaction,
        test_risk_result
    )

    print(
        "\nTransaction added to queue."
    )

    # --------------------------------------------------------
    # Display queue
    # --------------------------------------------------------

    print(
        "\nCurrent Investigation Queue:"
    )

    print(
        load_investigation_queue()
    )

    # --------------------------------------------------------
    # Display pending
    # --------------------------------------------------------

    print(
        "\nPending Investigations:"
    )

    print(
        load_pending_investigations()
    )

    # --------------------------------------------------------
    # Update status
    # --------------------------------------------------------

    print(
        "\nUpdating transaction status..."
    )

    updated = update_investigation_status(
        "QUEUE_TEST_001",
        "INVESTIGATING"
    )

    if updated:

        print(
            "Status updated successfully."
        )

    else:

        print(
            "Transaction not found."
        )

    # --------------------------------------------------------
    # Display final queue
    # --------------------------------------------------------

    print(
        "\nFinal Investigation Queue:"
    )

    print(
        load_investigation_queue()
    )

    print(
        "\n=========================================="
    )
    print(
        "       QUEUE TEST COMPLETED"
    )
    print(
        "=========================================="
    )