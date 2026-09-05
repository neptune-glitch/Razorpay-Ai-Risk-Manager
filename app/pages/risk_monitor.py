import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Risk Monitor | AI Risk Manager",
    page_icon="📡",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

DATA_PATH = "data/raw/transactions.csv"

if not os.path.exists(DATA_PATH):
    st.error(f"Transaction data not found: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)


# ============================================================
# HEADER
# ============================================================

st.title("📡 Risk Monitor")

st.write(
    "Real-time-style monitoring of transaction risk signals and "
    "fraud activity."
)

st.divider()


# ============================================================
# BASIC COUNTS
# ============================================================

total_transactions = len(df)

fraud_transactions = (
    df["is_fraud"].sum()
    if "is_fraud" in df.columns
    else 0
)

fraud_rate = (
    fraud_transactions / total_transactions * 100
    if total_transactions > 0
    else 0
)


# ============================================================
# RISK DISTRIBUTION
# ============================================================

# We use fraud labels as the main risk indicator here.
# Later we can replace this with stored risk scores.

if "is_fraud" in df.columns:

    high_risk_count = int(
        df["is_fraud"].sum()
    )

    low_risk_count = (
        total_transactions
        - high_risk_count
    )

else:

    high_risk_count = 0
    low_risk_count = total_transactions


# ============================================================
# TOP METRICS
# ============================================================

st.subheader("📊 System Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Transactions",
        f"{total_transactions:,}"
    )


with col2:

    st.metric(
        "High Risk",
        f"{high_risk_count:,}"
    )


with col3:

    st.metric(
        "Low Risk",
        f"{low_risk_count:,}"
    )


with col4:

    st.metric(
        "Fraud Rate",
        f"{fraud_rate:.2f}%"
    )


st.divider()


# ============================================================
# RISK STATUS
# ============================================================

st.subheader("🚦 Risk Status")


if fraud_rate >= 10:

    st.error(
        "🚨 CRITICAL — Fraud activity is significantly elevated."
    )

elif fraud_rate >= 5:

    st.warning(
        "⚠️ ELEVATED — Increased fraud activity detected."
    )

else:

    st.success(
        "✅ NORMAL — Fraud activity is within expected levels."
    )


st.divider()


# ============================================================
# FRAUD TYPE DISTRIBUTION
# ============================================================

st.subheader("🧩 Fraud Pattern Analysis")


if "fraud_type" in df.columns:

    fraud_only = df[
        df["is_fraud"] == 1
    ]

    if len(fraud_only) > 0:

        fraud_type_counts = (
            fraud_only["fraud_type"]
            .value_counts()
        )

        st.bar_chart(
            fraud_type_counts
        )

    else:

        st.info(
            "No fraudulent transactions found."
        )

else:

    st.info(
        "fraud_type column is not available."
    )


st.divider()


# ============================================================
# PAYMENT METHOD ANALYSIS
# ============================================================

st.subheader("💳 Fraud by Payment Method")


if (
    "payment_method" in df.columns
    and "is_fraud" in df.columns
):

    payment_analysis = (
        df.groupby("payment_method")["is_fraud"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    st.bar_chart(
        payment_analysis
    )


st.divider()


# ============================================================
# HIGH-RISK TRANSACTIONS
# ============================================================

st.subheader("🚨 High-Risk Transactions")


if "is_fraud" in df.columns:

    high_risk = df[
        df["is_fraud"] == 1
    ].copy()

    display_columns = [
        "transaction_id",
        "merchant_id",
        "amount",
        "payment_method",
        "failed_attempts",
        "transactions_1min",
        "transactions_5min",
        "new_device",
        "new_ip",
        "fraud_type"
    ]

    available_columns = [
        column
        for column in display_columns
        if column in high_risk.columns
    ]

    st.dataframe(
        high_risk[
            available_columns
        ].head(50),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Fraud information is not available."
    )


st.divider()


# ============================================================
# VELOCITY MONITOR
# ============================================================

st.subheader("⚡ Transaction Velocity Monitor")


if "transactions_1min" in df.columns:

    max_velocity = df[
        "transactions_1min"
    ].max()

    average_velocity = df[
        "transactions_1min"
    ].mean()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Average / 1 Minute",
            f"{average_velocity:.2f}"
        )

    with col2:

        st.metric(
            "Maximum / 1 Minute",
            f"{max_velocity:.0f}"
        )

    with col3:

        high_velocity = len(
            df[
                df["transactions_1min"] >= 20
            ]
        )

        st.metric(
            "High Velocity Transactions",
            f"{high_velocity:,}"
        )


st.divider()


# ============================================================
# SUSPICIOUS VELOCITY TRANSACTIONS
# ============================================================

st.subheader(
    "🔥 Suspicious Velocity Activity"
)


if "transactions_1min" in df.columns:

    velocity_df = df[
        df["transactions_1min"] >= 20
    ].copy()

    velocity_columns = [
        "transaction_id",
        "merchant_id",
        "amount",
        "transactions_1min",
        "transactions_5min",
        "transactions_10min",
        "transactions_1hour",
        "failed_attempts",
        "is_fraud"
    ]

    available_velocity_columns = [
        column
        for column in velocity_columns
        if column in velocity_df.columns
    ]

    st.dataframe(
        velocity_df[
            available_velocity_columns
        ]
        .sort_values(
            "transactions_1min",
            ascending=False
        )
        .head(50),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Payment Risk Manager • Risk monitoring dashboard"
)