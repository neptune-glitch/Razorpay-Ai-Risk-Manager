import pandas as pd
import numpy as np


def load_data(path="data/raw/transactions.csv"):
    """Load transaction dataset."""
    return pd.read_csv(path)


def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate approximate geographic distance
    using the Haversine formula.
    """

    earth_radius = 6371

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)

    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(
        np.sqrt(a)
    )

    return earth_radius * c


def prepare_features(df):

    df = df.copy()

    # Queue records can lack fields used by the trained models.  Neutral
    # defaults keep scoring available while model-column alignment handles
    # categorical feature differences.
    numeric_columns = [
        "amount", "avg_amount_24h", "std_amount_24h", "failed_attempts",
        "transactions_1min", "transactions_5min", "transactions_10min",
        "transactions_1hour", "new_device", "new_ip", "latitude",
        "longitude", "previous_latitude", "previous_longitude",
    ]
    for column in numeric_columns:
        if column not in df.columns:
            df[column] = 0
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    if "payment_method" not in df.columns:
        df["payment_method"] = "UNKNOWN"
    df["payment_method"] = df["payment_method"].fillna("UNKNOWN")

    # ==========================================
    # 1. Amount behavior
    # ==========================================

    df["amount_ratio"] = (
        df["amount"]
        /
        (df["avg_amount_24h"] + 1)
    )

    df["amount_zscore"] = (
        (
            df["amount"]
            -
            df["avg_amount_24h"]
        )
        /
        (df["std_amount_24h"] + 1)
    )

    # ==========================================
    # 2. Transaction velocity
    # ==========================================

    # Approximate normal baselines
    df["velocity_1m_ratio"] = (
        df["transactions_1min"] / 1
    )

    df["velocity_5m_ratio"] = (
        df["transactions_5min"] / 4
    )

    df["velocity_10m_ratio"] = (
        df["transactions_10min"] / 7
    )

    df["velocity_1h_ratio"] = (
        df["transactions_1hour"] / 40
    )

    # ==========================================
    # 3. Failure behavior
    # ==========================================

    total_activity = (
        df["transactions_10min"] + 1
    )

    df["failure_rate"] = (
        df["failed_attempts"]
        /
        total_activity
    )

    # ==========================================
    # 4. Device / IP behavior
    # ==========================================

    df["device_risk"] = (
        df["new_device"]
    )

    df["ip_risk"] = (
        df["new_ip"]
    )

    # ==========================================
    # 5. Geographic behavior
    # ==========================================

    df["geo_distance"] = calculate_distance(
        df["previous_latitude"],
        df["previous_longitude"],
        df["latitude"],
        df["longitude"]
    )

    # ==========================================
    # 6. Impossible travel
    # ==========================================

    # We use 500 km as a simple prototype
    # threshold for suspicious movement.
    df["impossible_travel"] = (
        df["geo_distance"] > 500
    ).astype(int)

    # ==========================================
    # 7. Spike intensity
    # ==========================================

    df["spike_intensity"] = (
        df["velocity_10m_ratio"]
    )

    # ==========================================
    # 8. Combined behavioral risk
    # ==========================================

    df["behavioral_risk"] = (

        df["amount_ratio"]

        *

        (1 + df["spike_intensity"])

        *

        (1 + df["failure_rate"])

        *

        (1 + df["device_risk"])

        *

        (1 + df["ip_risk"])

        *

        (1 + df["impossible_travel"])
    )

    # ==========================================
    # 9. Payment method encoding
    # ==========================================

    df = pd.get_dummies(
        df,
        columns=["payment_method"],
        drop_first=True
    )

    # ==========================================
    # 10. Remove non-ML columns
    # ==========================================

    df = df.drop(
        columns=[
            "transaction_id",
            "merchant_id",
            "timestamp",
            "device_id",
            "ip_address",
            "fraud_type"
        ],
        errors="ignore"
    )

    # ==========================================
    # 11. Convert everything to numeric
    # ==========================================

    df = df.astype(float)

    return df


if __name__ == "__main__":

    df = load_data()

    print("Original dataset:")
    print(df.head())

    print("\nOriginal shape:")
    print(df.shape)

    prepared = prepare_features(df)

    print("\nPrepared dataset:")
    print(prepared.head())

    print("\nPrepared shape:")
    print(prepared.shape)

    print("\nFeature columns:")

    for column in prepared.columns:
        print("-", column)
