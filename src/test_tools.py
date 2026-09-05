import pandas as pd

from investigation_tools import (
    check_merchant_history,
    check_device_history,
    check_ip_history,
    check_transaction_velocity,
    check_location_anomaly
)


# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    "data/raw/transactions.csv"
)


# ==========================================
# SELECT TRANSACTION
# ==========================================

transaction = (
    df[df["is_fraud"] == 1]
    .iloc[0]
    .to_dict()
)


print("\n==========================================")
print("       INVESTIGATION TOOL TEST")
print("==========================================")


print("\nTransaction:")
print(transaction["transaction_id"])


# ==========================================
# MERCHANT
# ==========================================

print("\n--- MERCHANT HISTORY ---")

print(
    check_merchant_history(
        transaction,
        df
    )
)


# ==========================================
# DEVICE
# ==========================================

print("\n--- DEVICE HISTORY ---")

print(
    check_device_history(
        transaction,
        df
    )
)


# ==========================================
# IP
# ==========================================

print("\n--- IP HISTORY ---")

print(
    check_ip_history(
        transaction,
        df
    )
)


# ==========================================
# VELOCITY
# ==========================================

print("\n--- VELOCITY ---")

print(
    check_transaction_velocity(
        transaction
    )
)


# ==========================================
# LOCATION
# ==========================================

print("\n--- LOCATION ---")

print(
    check_location_anomaly(
        transaction
    )
)