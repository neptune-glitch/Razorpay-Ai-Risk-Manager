import pandas as pd
import math


# ==========================================
# 1. MERCHANT HISTORY
# ==========================================

def check_merchant_history(transaction, df):

    merchant_id = transaction.get("merchant_id")

    merchant_data = df[
        df["merchant_id"] == merchant_id
    ]

    total_transactions = len(merchant_data)

    fraud_transactions = int(
        merchant_data["is_fraud"].sum()
    )

    fraud_rate = (
        fraud_transactions / total_transactions * 100
        if total_transactions > 0
        else 0
    )

    return {
        "merchant_id": merchant_id,
        "total_transactions": total_transactions,
        "fraud_transactions": fraud_transactions,
        "fraud_rate": round(fraud_rate, 2)
    }


# ==========================================
# 2. DEVICE HISTORY
# ==========================================

def check_device_history(transaction, df):

    device_id = transaction.get("device_id")

    if "device_id" not in df.columns:
        return {
            "error": "device_id column not available"
        }

    device_data = df[
        df["device_id"] == device_id
    ]

    total_transactions = len(device_data)

    fraud_transactions = int(
        device_data["is_fraud"].sum()
    )

    return {
        "device_id": device_id,
        "transactions": total_transactions,
        "fraud_transactions": fraud_transactions
    }


# ==========================================
# 3. IP HISTORY
# ==========================================

def check_ip_history(transaction, df):

    ip_address = transaction.get("ip_address")

    if "ip_address" not in df.columns:
        return {
            "error": "ip_address column not available"
        }

    ip_data = df[
        df["ip_address"] == ip_address
    ]

    total_transactions = len(ip_data)

    fraud_transactions = int(
        ip_data["is_fraud"].sum()
    )

    return {
        "ip_address": ip_address,
        "transactions": total_transactions,
        "fraud_transactions": fraud_transactions
    }


# ==========================================
# 4. TRANSACTION VELOCITY
# ==========================================

def check_transaction_velocity(transaction):

    return {
        "transactions_1min": transaction.get(
            "transactions_1min", 0
        ),

        "transactions_5min": transaction.get(
            "transactions_5min", 0
        ),

        "transactions_10min": transaction.get(
            "transactions_10min", 0
        ),

        "transactions_1hour": transaction.get(
            "transactions_1hour", 0
        )
    }


# ==========================================
# 5. LOCATION ANOMALY
# ==========================================

def check_location_anomaly(transaction):

    lat1 = transaction.get("latitude")
    lon1 = transaction.get("longitude")

    lat2 = transaction.get("previous_latitude")
    lon2 = transaction.get("previous_longitude")

    if any(
        value is None
        for value in [lat1, lon1, lat2, lon2]
    ):
        return {
            "error": "Location information unavailable"
        }

    # Approximate distance using Haversine formula

    R = 6371

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))

    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    distance_km = R * c

    return {
        "distance_km": round(distance_km, 2),
        "impossible_travel": (
            True
            if distance_km > 500
            else False
        )
    }