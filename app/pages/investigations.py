import streamlit as st
import pandas as pd
import os
import sys


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# IMPORTS
# ============================================================

from src.risk_engine import calculate_risk

from src.investigation_queue import (
    load_investigation_queue,
    load_pending_investigations,
    update_investigation_status
)

from src.agent import investigate

from src.llm_investigator import (
    generate_investigation_report
)

from src.audit_logger import (
    log_investigator_action,
    load_audit_log
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Investigations | AI Risk Manager",
    page_icon="🚨",
    layout="wide"
)


# ============================================================
# DATA PATHS
# ============================================================

DATA_PATH = "data/raw/transactions.csv"
QUEUE_PATH = "data/investigation_queue.csv"


# ============================================================
# LOAD ORIGINAL TRANSACTIONS
# ============================================================

try:

    original_df = pd.read_csv(
        DATA_PATH
    )

except Exception as e:

    st.error(
        f"Could not load transactions.csv: {e}"
    )

    st.stop()


# ============================================================
# LOAD INVESTIGATION QUEUE
# ============================================================

queue_df = load_investigation_queue()


# ============================================================
# PREPARE INVESTIGATION DATA
# ============================================================

# We primarily investigate transactions
# that exist in the original transaction dataset.

df = original_df.copy()


# ------------------------------------------------------------
# Add queue information if available
# ------------------------------------------------------------

if not queue_df.empty:

    queue_info = queue_df[
        [
            "transaction_id",
            "risk_score",
            "risk_level",
            "status",
            "reason"
        ]
    ].copy()

    # Remove duplicate transaction IDs
    queue_info = queue_info.drop_duplicates(
        subset=["transaction_id"],
        keep="last"
    )

    # Merge gateway investigation information
    df = df.merge(
        queue_info,
        on="transaction_id",
        how="left"
    )


# ============================================================
# PAGE HEADER
# ============================================================

st.title(
    "🚨 Fraud Investigations"
)

st.write(
    "Review suspicious transactions detected by the AI risk system."
)


# ============================================================
# BASIC STATISTICS
# ============================================================

if "is_fraud" in df.columns:

    high_risk = df[
        df["is_fraud"] == 1
    ].copy()

else:

    high_risk = df.copy()


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total Transactions",
        f"{len(df):,}"
    )


with col2:

    st.metric(
        "Fraud Detected",
        f"{len(high_risk):,}"
    )


with col3:

    if len(df) > 0:

        fraud_rate = (
            len(high_risk)
            / len(df)
            * 100
        )

    else:

        fraud_rate = 0

    st.metric(
        "Fraud Rate",
        f"{fraud_rate:.2f}%"
    )


st.divider()


# ============================================================
# INVESTIGATION QUEUE
# ============================================================

st.subheader(
    "🔎 Investigation Queue"
)


# ============================================================
# QUEUE STATUS SUMMARY
# ============================================================

if not queue_df.empty:

    pending_count = len(
        queue_df[
            queue_df["status"]
            .astype(str)
            .str.upper()
            == "PENDING"
        ]
    )

    investigating_count = len(
        queue_df[
            queue_df["status"]
            .astype(str)
            .str.upper()
            == "INVESTIGATING"
        ]
    )

    completed_count = len(
        queue_df[
            queue_df["status"]
            .astype(str)
            .str.upper()
            .isin(
                [
                    "APPROVED",
                    "BLOCKED",
                    "REVIEW"
                ]
            )
        ]
    )

else:

    pending_count = 0
    investigating_count = 0
    completed_count = 0


status_col1, status_col2, status_col3 = st.columns(3)


with status_col1:

    st.metric(
        "Pending",
        pending_count
    )


with status_col2:

    st.metric(
        "Investigating",
        investigating_count
    )


with status_col3:

    st.metric(
        "Completed",
        completed_count
    )


# ============================================================
# FILTERS
# ============================================================

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)


# ------------------------------------------------------------
# Fraud Type
# ------------------------------------------------------------

with filter_col1:

    fraud_types = ["ALL"]

    if "fraud_type" in high_risk.columns:

        fraud_values = (
            high_risk["fraud_type"]
            .dropna()
            .unique()
            .tolist()
        )

        fraud_types += sorted(
            fraud_values
        )

    selected_fraud_type = st.selectbox(
        "Fraud Type",
        fraud_types
    )


# ------------------------------------------------------------
# Minimum Amount
# ------------------------------------------------------------

with filter_col2:

    minimum_amount = st.number_input(
        "Minimum Amount (₹)",
        min_value=0.0,
        value=0.0,
        step=500.0
    )


# ------------------------------------------------------------
# New Device
# ------------------------------------------------------------

with filter_col3:

    device_filter = st.selectbox(
        "New Device",
        [
            "ALL",
            "YES",
            "NO"
        ]
    )


# ------------------------------------------------------------
# New IP
# ------------------------------------------------------------

with filter_col4:

    ip_filter = st.selectbox(
        "New IP",
        [
            "ALL",
            "YES",
            "NO"
        ]
    )


# ============================================================
# SEARCH
# ============================================================

search_text = st.text_input(
    "🔍 Search Transaction ID or Merchant ID"
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = high_risk.copy()


# ------------------------------------------------------------
# Fraud Type
# ------------------------------------------------------------

if (
    selected_fraud_type != "ALL"
    and "fraud_type" in filtered_df.columns
):

    filtered_df = filtered_df[
        filtered_df["fraud_type"]
        == selected_fraud_type
    ]


# ------------------------------------------------------------
# Minimum Amount
# ------------------------------------------------------------

if "amount" in filtered_df.columns:

    filtered_df = filtered_df[
        pd.to_numeric(
            filtered_df["amount"],
            errors="coerce"
        ).fillna(0)
        >= minimum_amount
    ]


# ------------------------------------------------------------
# New Device
# ------------------------------------------------------------

if "new_device" in filtered_df.columns:

    if device_filter == "YES":

        filtered_df = filtered_df[
            pd.to_numeric(
                filtered_df["new_device"],
                errors="coerce"
            ).fillna(0)
            == 1
        ]

    elif device_filter == "NO":

        filtered_df = filtered_df[
            pd.to_numeric(
                filtered_df["new_device"],
                errors="coerce"
            ).fillna(0)
            == 0
        ]


# ------------------------------------------------------------
# New IP
# ------------------------------------------------------------

if "new_ip" in filtered_df.columns:

    if ip_filter == "YES":

        filtered_df = filtered_df[
            pd.to_numeric(
                filtered_df["new_ip"],
                errors="coerce"
            ).fillna(0)
            == 1
        ]

    elif ip_filter == "NO":

        filtered_df = filtered_df[
            pd.to_numeric(
                filtered_df["new_ip"],
                errors="coerce"
            ).fillna(0)
            == 0
        ]


# ------------------------------------------------------------
# Search
# ------------------------------------------------------------

if search_text:

    search_text = search_text.lower()

    transaction_match = (
        filtered_df[
            "transaction_id"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            search_text,
            na=False
        )
    )

    merchant_match = (
        filtered_df[
            "merchant_id"
        ]
        .astype(str)
        .str.lower()
        .str.contains(
            search_text,
            na=False
        )
    )

    filtered_df = filtered_df[
        transaction_match
        | merchant_match
    ]


# ============================================================
# DISPLAY QUEUE
# ============================================================

st.write(
    f"Showing **{len(filtered_df)}** suspicious transactions"
)


queue_columns = [

    "transaction_id",

    "merchant_id",

    "amount",

    "payment_method",

    "failed_attempts",

    "transactions_1min",

    "transactions_5min",

    "transactions_10min",

    "transactions_1hour",

    "new_device",

    "new_ip",

    "fraud_type",

    "risk_score",

    "risk_level",

    "status"

]


available_queue_columns = [

    column

    for column in queue_columns

    if column in filtered_df.columns

]


if available_queue_columns:

    st.dataframe(
        filtered_df[
            available_queue_columns
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "No transaction information available."
    )


# ============================================================
# INVESTIGATION DETAIL
# ============================================================

st.divider()

st.subheader(
    "🔎 Investigate Transaction"
)


if filtered_df.empty:

    st.warning(
        "No transactions match the selected filters."
    )

    st.stop()


# ============================================================
# TRANSACTION SELECTOR
# ============================================================

transaction_ids = (
    filtered_df[
        "transaction_id"
    ]
    .astype(str)
    .tolist()
)


selected_id = st.selectbox(
    "Select a suspicious transaction",
    transaction_ids
)


selected_transaction = (
    filtered_df[
        filtered_df[
            "transaction_id"
        ].astype(str)
        == str(selected_id)
    ]
    .iloc[0]
    .to_dict()
)


# ============================================================
# RUN RISK ENGINE
# ============================================================

try:

    result = calculate_risk(
        selected_transaction
    )

except Exception as e:

    st.error(
        f"Risk engine error: {e}"
    )

    st.stop()


# ============================================================
# RISK ASSESSMENT
# ============================================================

st.divider()

st.subheader(
    "⚠️ Risk Assessment"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Risk Score",
        f"{result['risk_score']:.2f}/100"
    )


with col2:

    st.metric(
        "Risk Level",
        result["risk_level"]
    )


with col3:

    st.metric(
        "Decision",
        result["decision"]
    )


# ============================================================
# RISK COMPONENTS
# ============================================================

st.subheader(
    "🧠 Risk Components"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "ML Fraud Score",
        result.get(
            "ml_score",
            0
        )
    )


with col2:

    st.metric(
        "Anomaly Score",
        result.get(
            "anomaly_score",
            0
        )
    )


with col3:

    st.metric(
        "Behavior Score",
        result.get(
            "behavioral_score",
            0
        )
    )


# ============================================================
# RISK REASONS
# ============================================================

st.subheader(
    "🚨 Why was this transaction flagged?"
)


for reason in result.get(
    "reasons",
    []
):

    st.warning(
        reason
    )


# ============================================================
# TRANSACTION INFORMATION
# ============================================================

st.subheader(
    "💳 Transaction Information"
)


info_col1, info_col2 = st.columns(2)


with info_col1:

    st.write(
        f"**Transaction ID:** "
        f"{selected_transaction.get('transaction_id', 'N/A')}"
    )

    st.write(
        f"**Merchant ID:** "
        f"{selected_transaction.get('merchant_id', 'N/A')}"
    )

    st.write(
        f"**Amount:** "
        f"₹{float(selected_transaction.get('amount', 0)):,.2f}"
    )

    st.write(
        f"**Payment Method:** "
        f"{selected_transaction.get('payment_method', 'N/A')}"
    )


with info_col2:

    st.write(
        f"**Fraud Type:** "
        f"{selected_transaction.get('fraud_type', 'N/A')}"
    )

    st.write(
        f"**Failed Attempts:** "
        f"{selected_transaction.get('failed_attempts', 0)}"
    )

    st.write(
        f"**New Device:** "
        f"{'Yes' if selected_transaction.get('new_device', 0) else 'No'}"
    )

    st.write(
        f"**New IP:** "
        f"{'Yes' if selected_transaction.get('new_ip', 0) else 'No'}"
    )


# ============================================================
# TRANSACTION VELOCITY
# ============================================================

st.subheader(
    "⚡ Transaction Velocity"
)


velocity_col1, velocity_col2, velocity_col3, velocity_col4 = st.columns(4)


with velocity_col1:

    st.metric(
        "1 Minute",
        selected_transaction.get(
            "transactions_1min",
            0
        )
    )


with velocity_col2:

    st.metric(
        "5 Minutes",
        selected_transaction.get(
            "transactions_5min",
            0
        )
    )


with velocity_col3:

    st.metric(
        "10 Minutes",
        selected_transaction.get(
            "transactions_10min",
            0
        )
    )


with velocity_col4:

    st.metric(
        "1 Hour",
        selected_transaction.get(
            "transactions_1hour",
            0
        )
    )


# ============================================================
# LOCATION
# ============================================================

st.subheader(
    "📍 Location Information"
)


location_col1, location_col2 = st.columns(2)


with location_col1:

    st.write(
        f"**Current Latitude:** "
        f"{selected_transaction.get('latitude', 'N/A')}"
    )

    st.write(
        f"**Current Longitude:** "
        f"{selected_transaction.get('longitude', 'N/A')}"
    )


with location_col2:

    st.write(
        f"**Previous Latitude:** "
        f"{selected_transaction.get('previous_latitude', 'N/A')}"
    )

    st.write(
        f"**Previous Longitude:** "
        f"{selected_transaction.get('previous_longitude', 'N/A')}"
    )


# ============================================================
# AI RECOMMENDATION
# ============================================================

st.divider()

st.subheader(
    "🤖 AI Recommendation"
)


if result["risk_level"] == "HIGH":

    st.error(
        "HIGH RISK — Transaction should be BLOCKED."
    )

elif result["risk_level"] == "MEDIUM":

    st.warning(
        "MEDIUM RISK — Transaction requires MANUAL REVIEW."
    )

else:

    st.success(
        "LOW RISK — Transaction can be APPROVED."
    )


# ============================================================
# AI INVESTIGATION
# ============================================================

st.divider()

st.subheader(
    "🧠 AI Investigation"
)


st.write(
    "The investigation agent collects merchant, "
    "device, IP, velocity and location evidence. "
    "Gemini then generates an investigation report."
)


# ============================================================
# SESSION STATE
# ============================================================

if "investigation_result" not in st.session_state:

    st.session_state.investigation_result = None


if "investigation_report" not in st.session_state:

    st.session_state.investigation_report = None


if "investigation_transaction_id" not in st.session_state:

    st.session_state.investigation_transaction_id = None


# ============================================================
# GENERATE AI INVESTIGATION
# ============================================================

if st.button(
    "🧠 Generate AI Investigation",
    use_container_width=True
):

    # --------------------------------------------------------
    # Mark transaction as INVESTIGATING
    # --------------------------------------------------------

    update_investigation_status(
        selected_id,
        "INVESTIGATING"
    )


    # --------------------------------------------------------
    # Investigation Agent
    # --------------------------------------------------------

    with st.spinner(
        "Investigation agent is collecting evidence..."
    ):

        try:

            investigation_result = investigate(
                selected_transaction
            )

        except Exception as e:

            st.error(
                f"Investigation agent error: {e}"
            )

            st.stop()


    evidence = investigation_result.get(
        "evidence",
        {}
    )


    # --------------------------------------------------------
    # Gemini Investigation
    # --------------------------------------------------------

    with st.spinner(
        "Gemini is analyzing investigation evidence..."
    ):

        try:

            report = generate_investigation_report(
                selected_transaction,
                investigation_result,
                evidence
            )

        except Exception as e:

            st.error(
                f"Gemini investigation error: {e}"
            )

            st.stop()


    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    st.session_state.investigation_result = (
        investigation_result
    )

    st.session_state.investigation_report = (
        report
    )

    st.session_state.investigation_transaction_id = (
        selected_id
    )


    st.success(
        "AI investigation completed."
    )


# ============================================================
# DISPLAY INVESTIGATION
# ============================================================

if (
    st.session_state.investigation_result
    is not None

    and

    st.session_state.investigation_transaction_id
    == selected_id
):

    investigation_result = (
        st.session_state.investigation_result
    )

    report = (
        st.session_state.investigation_report
    )

    evidence = investigation_result.get(
        "evidence",
        {}
    )


    st.success(
        "AI investigation completed."
    )


    # ========================================================
    # TOOLS USED
    # ========================================================

    if evidence:

        st.write(
            "**Investigation tools used:**"
        )

        tool_text = "\n".join(
            f"✓ {tool}"
            for tool in evidence.keys()
        )

        st.code(
            tool_text
        )


    # ========================================================
    # AI REPORT
    # ========================================================

    st.subheader(
        "📋 AI Investigation Report"
    )

    st.markdown(
        report
    )


    # ========================================================
    # EVIDENCE
    # ========================================================

    with st.expander(
        "🔍 View Investigation Evidence"
    ):

        st.json(
            evidence
        )


    # ========================================================
    # INVESTIGATOR ACTION
    # ========================================================

    st.divider()

    st.subheader(
        "👨‍💻 Investigator Action"
    )

    st.write(
        "Review the AI investigation and record "
        "the final investigator decision."
    )


    decision = st.radio(
        "Investigator Decision",

        [
            "APPROVE",
            "MANUAL_REVIEW",
            "BLOCK"
        ],

        horizontal=True
    )


    reason = st.text_area(
        "Investigator Reason",

        placeholder=(
            "Enter why you approved, blocked, "
            "or sent this transaction for review..."
        )
    )


    # ========================================================
    # RECORD DECISION
    # ========================================================

    if st.button(
        "💾 Record Investigator Decision",
        type="primary",
        use_container_width=True
    ):

        if not reason.strip():

            st.warning(
                "Please provide an investigator reason."
            )

        else:

            try:

                # --------------------------------------------
                # Update investigation queue
                # --------------------------------------------

                queue_status = decision

                if decision == "MANUAL_REVIEW":

                    queue_status = "REVIEW"


                update_investigation_status(
                    selected_id,
                    queue_status
                )


                # --------------------------------------------
                # Write audit log
                # --------------------------------------------

                log_investigator_action(

                    transaction_id=selected_id,

                    risk_score=result[
                        "risk_score"
                    ],

                    risk_level=result[
                        "risk_level"
                    ],

                    ai_recommendation=result[
                        "decision"
                    ],

                    investigator_decision=decision,

                    reason=reason
                )


                st.success(
                    f"✅ Transaction marked as "
                    f"{decision} and recorded in "
                    f"the audit trail."
                )


                # --------------------------------------------
                # Clear investigation state
                # --------------------------------------------

                st.session_state.investigation_result = None

                st.session_state.investigation_report = None

                st.session_state.investigation_transaction_id = None


                st.rerun()


            except Exception as e:

                st.error(
                    f"Could not save investigator decision: {e}"
                )


# ============================================================
# AUDIT TRAIL
# ============================================================

st.divider()

st.subheader(
    "📜 Investigator Audit Trail"
)


audit_df = load_audit_log()


if audit_df is not None and not audit_df.empty:

    st.dataframe(
        audit_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No investigator actions recorded yet."
    )