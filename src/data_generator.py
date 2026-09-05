import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

NUM_TRANSACTIONS = 10000
NUM_MERCHANTS = 100
NUM_DEVICES = 500

merchants = [
    f"MERCHANT_{i:03d}"
    for i in range(1, NUM_MERCHANTS + 1)
]

devices = [
    f"DEVICE_{i:04d}"
    for i in range(1, NUM_DEVICES + 1)
]

payment_methods = [
    "UPI",
    "CARD",
    "NETBANKING",
    "WALLET"
]

transactions = []

start_time = datetime(2026, 9, 1, 0, 0, 0)


for i in range(NUM_TRANSACTIONS):

    transaction_id = f"TXN_{i + 1:06d}"

    merchant_id = np.random.choice(merchants)

    timestamp = (
        start_time
        + timedelta(
            seconds=int(np.random.randint(0, 7 * 24 * 60 * 60))
        )
    )

    # ------------------------------------------------
    # Merchant baseline
    # ------------------------------------------------

    merchant_avg = np.random.uniform(200, 1000)

    merchant_std = np.random.uniform(50, 250)

    amount = max(
        10,
        np.random.normal(
            merchant_avg,
            merchant_std
        )
    )

    amount = round(amount, 2)

    # ------------------------------------------------
    # Normal transaction velocity
    # ------------------------------------------------

    transactions_1min = np.random.poisson(1)

    transactions_5min = max(
        transactions_1min,
        np.random.poisson(4)
    )

    transactions_10min = max(
        transactions_5min,
        np.random.poisson(7)
    )

    transactions_1hour = max(
        transactions_10min,
        np.random.poisson(40)
    )

    failed_attempts = np.random.poisson(0.5)

    # ------------------------------------------------
    # Device / IP
    # ------------------------------------------------

    device_id = np.random.choice(devices)

    ip_address = (
        f"192.168."
        f"{np.random.randint(0, 255)}."
        f"{np.random.randint(1, 255)}"
    )

    new_device = np.random.choice(
        [0, 1],
        p=[0.92, 0.08]
    )

    new_ip = np.random.choice(
        [0, 1],
        p=[0.90, 0.10]
    )

    # ------------------------------------------------
    # Location
    # ------------------------------------------------

    latitude = np.random.uniform(8, 35)

    longitude = np.random.uniform(68, 90)

    previous_latitude = latitude + np.random.normal(0, 0.05)

    previous_longitude = longitude + np.random.normal(0, 0.05)

    # ------------------------------------------------
    # Merchant behavior attack types
    # ------------------------------------------------

    attack_roll = np.random.random()

    fraud_type = "NORMAL"

    # 1. Velocity spike
    if attack_roll < 0.015:

        transactions_1min = np.random.randint(15, 40)
        transactions_5min = np.random.randint(40, 100)
        transactions_10min = np.random.randint(80, 180)
        transactions_1hour = np.random.randint(200, 500)

        failed_attempts = np.random.randint(3, 10)

        fraud_type = "VELOCITY_SPIKE"

    # 2. Amount anomaly
    elif attack_roll < 0.025:

        amount = round(
            merchant_avg
            * np.random.uniform(5, 12),
            2
        )

        fraud_type = "AMOUNT_ANOMALY"

    # 3. Device attack
    elif attack_roll < 0.035:

        new_device = 1
        new_ip = 1

        device_id = (
            f"ATTACK_DEVICE_{np.random.randint(1, 1000)}"
        )

        failed_attempts = np.random.randint(2, 7)

        fraud_type = "DEVICE_ATTACK"

    # 4. Location anomaly
    elif attack_roll < 0.045:

        # Simulate large geographic movement
        previous_latitude = np.random.uniform(8, 35)
        previous_longitude = np.random.uniform(68, 90)

        latitude = np.random.uniform(8, 35)
        longitude = np.random.uniform(68, 90)

        fraud_type = "LOCATION_ANOMALY"

    # 5. Combined attack
    elif attack_roll < 0.055:

        transactions_1min = np.random.randint(20, 50)
        transactions_5min = np.random.randint(60, 120)
        transactions_10min = np.random.randint(100, 200)

        amount = round(
            merchant_avg
            * np.random.uniform(4, 10),
            2
        )

        failed_attempts = np.random.randint(4, 10)

        new_device = 1
        new_ip = 1

        fraud_type = "COMBINED_ATTACK"

    # ------------------------------------------------
    # Fraud label
    # ------------------------------------------------

    is_fraud = 0

    if fraud_type != "NORMAL":
        is_fraud = 1

    transactions.append({

        "transaction_id": transaction_id,

        "merchant_id": merchant_id,

        "timestamp": timestamp,

        "amount": amount,

        "payment_method": np.random.choice(
            payment_methods
        ),

        "failed_attempts": failed_attempts,

        "transactions_1min": transactions_1min,

        "transactions_5min": transactions_5min,

        "transactions_10min": transactions_10min,

        "transactions_1hour": transactions_1hour,

        "avg_amount_24h": round(
            merchant_avg,
            2
        ),

        "std_amount_24h": round(
            merchant_std,
            2
        ),

        "device_id": device_id,

        "ip_address": ip_address,

        "new_device": new_device,

        "new_ip": new_ip,

        "latitude": round(
            latitude,
            5
        ),

        "longitude": round(
            longitude,
            5
        ),

        "previous_latitude": round(
            previous_latitude,
            5
        ),

        "previous_longitude": round(
            previous_longitude,
            5
        ),

        "is_fraud": is_fraud,

        "fraud_type": fraud_type
    })


# ------------------------------------------------
# Create DataFrame
# ------------------------------------------------

df = pd.DataFrame(transactions)

df = df.sort_values(
    "timestamp"
).reset_index(drop=True)


# ------------------------------------------------
# Save
# ------------------------------------------------

output_path = "data/raw/transactions.csv"

df.to_csv(
    output_path,
    index=False
)


# ------------------------------------------------
# Summary
# ------------------------------------------------

print("Advanced fraud dataset generated successfully!")

print(f"Total transactions: {len(df)}")

print(
    f"Fraudulent transactions: "
    f"{df['is_fraud'].sum()}"
)

print(
    f"Normal transactions: "
    f"{(df['is_fraud'] == 0).sum()}"
)

print(
    f"Fraud percentage: "
    f"{df['is_fraud'].mean() * 100:.2f}%"
)

print("\nFraud types:")

print(
    df["fraud_type"]
    .value_counts()
)

print(
    f"\nSaved to: {output_path}"
)