import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Audit Log | AI Risk Manager",
    page_icon="📜",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📜 Audit Log")

st.write(
    "Complete history of investigator decisions and AI risk assessments."
)

st.divider()


# ============================================================
# LOAD AUDIT LOG
# ============================================================

AUDIT_PATH = "data/audit_log.csv"


if not os.path.exists(AUDIT_PATH):

    st.info(
        "No audit records found yet. "
        "Analyze a transaction and save an investigator decision first."
    )

    st.stop()


df = pd.read_csv(AUDIT_PATH)


# ============================================================
# BASIC STATISTICS
# ============================================================

st.subheader("📊 Audit Overview")


total_records = len(df)

blocked = len(
    df[
        df["investigator_decision"]
        .astype(str)
        .str.upper()
        == "BLOCK"
    ]
)

approved = len(
    df[
        df["investigator_decision"]
        .astype(str)
        .str.upper()
        == "APPROVE"
    ]
)

review = len(
    df[
        df["investigator_decision"]
        .astype(str)
        .str.upper()
        == "REVIEW"
    ]
)


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total Decisions",
        f"{total_records:,}"
    )


with col2:
    st.metric(
        "Blocked",
        f"{blocked:,}"
    )


with col3:
    st.metric(
        "Approved",
        f"{approved:,}"
    )


with col4:
    st.metric(
        "Manual Review",
        f"{review:,}"
    )


st.divider()


# ============================================================
# FILTERS
# ============================================================

st.subheader("🔎 Filter Audit Records")


col1, col2 = st.columns(2)


with col1:

    decisions = [
        "ALL",
        "BLOCK",
        "APPROVE",
        "REVIEW"
    ]

    selected_decision = st.selectbox(
        "Investigator Decision",
        decisions
    )


with col2:

    search_text = st.text_input(
        "Search Transaction ID or Merchant ID"
    )


filtered_df = df.copy()


# ============================================================
# APPLY DECISION FILTER
# ============================================================

if selected_decision != "ALL":

    filtered_df = filtered_df[
        filtered_df["investigator_decision"]
        .astype(str)
        .str.upper()
        == selected_decision
    ]


# ============================================================
# APPLY SEARCH
# ============================================================

if search_text:

    search_text = search_text.lower()

    transaction_match = (
        filtered_df["transaction_id"]
        .astype(str)
        .str.lower()
        .str.contains(
            search_text,
            na=False
        )
    )

    if "merchant_id" in filtered_df.columns:

        merchant_match = (
            filtered_df["merchant_id"]
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

    else:

        filtered_df = filtered_df[
            transaction_match
        ]


st.write(
    f"Showing **{len(filtered_df):,}** audit records"
)


# ============================================================
# AUDIT TABLE
# ============================================================

st.subheader("📋 Decision History")


st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# SELECT TRANSACTION
# ============================================================

st.divider()

st.subheader("🔍 Audit Record Details")


if len(filtered_df) > 0:

    selected_transaction = st.selectbox(
        "Select Transaction",
        filtered_df["transaction_id"]
        .astype(str)
        .tolist()
    )


    selected_row = filtered_df[
        filtered_df["transaction_id"].astype(str)
        == selected_transaction
    ].iloc[0]


    # ========================================================
    # DETAILS
    # ========================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.write(
            f"**Transaction ID:** "
            f"{selected_row.get('transaction_id', 'N/A')}"
        )

        st.write(
            f"**Risk Score:** "
            f"{selected_row.get('risk_score', 'N/A')}"
        )


    with col2:

        st.write(
            f"**AI Recommendation:** "
            f"{selected_row.get('ai_recommendation', 'N/A')}"
        )

        st.write(
            f"**Investigator Decision:** "
            f"{selected_row.get('investigator_decision', 'N/A')}"
        )


    with col3:

        st.write(
            f"**Timestamp:** "
            f"{selected_row.get('timestamp', 'N/A')}"
        )

        st.write(
            f"**Reason:** "
            f"{selected_row.get('reason', 'N/A')}"
        )


    # ========================================================
    # DECISION DISPLAY
    # ========================================================

    decision = str(
        selected_row.get(
            "investigator_decision",
            ""
        )
    ).upper()


    if decision == "BLOCK":

        st.error(
            "🚨 Transaction was BLOCKED by the investigator."
        )

    elif decision == "REVIEW":

        st.warning(
            "⚠️ Transaction was sent for MANUAL REVIEW."
        )

    elif decision == "APPROVE":

        st.success(
            "✅ Transaction was APPROVED by the investigator."
        )

else:

    st.info(
        "No audit records match the selected filters."
    )