import streamlit as st
import sys
import os

# ============================================================
# CONNECT TO src/
# ============================================================

SRC_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src"
    )
)

if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from payment_gateway import process_payment


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Payment Risk Manager",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "transaction" not in st.session_state:
    st.session_state.transaction = None

if "gateway_result" not in st.session_state:
    st.session_state.gateway_result = None

if "investigation" not in st.session_state:
    st.session_state.investigation = None


# ============================================================
# HEADER
# ============================================================

st.title("🛡️ AI Payment Risk Manager")

st.write(
    "AI-powered fraud detection, payment risk assessment "
    "and automated investigation"
)

st.divider()


# ============================================================
# TRANSACTION DETAILS
# ============================================================

st.subheader("💳 Transaction Details")

col1, col2, col3 = st.columns(3)

with col1:

    amount = st.number_input(
        "Transaction Amount (₹)",
        min_value=1.0,
        value=500.0,
        step=100.0
    )

    failed_attempts = st.number_input(
        "Failed Payment Attempts",
        min_value=0,
        value=0,
        step=1
    )

    payment_method = st.selectbox(
        "Payment Method",
        [
            "UPI",
            "NETBANKING",
            "WALLET",
            "CARD"
        ]
    )


with col2:

    transactions_1min = st.number_input(
        "Transactions in 1 Minute",
        min_value=0,
        value=1,
        step=1
    )

    transactions_5min = st.number_input(
        "Transactions in 5 Minutes",
        min_value=0,
        value=3,
        step=1
    )

    transactions_10min = st.number_input(
        "Transactions in 10 Minutes",
        min_value=0,
        value=5,
        step=1
    )


with col3:

    transactions_1hour = st.number_input(
        "Transactions in 1 Hour",
        min_value=0,
        value=30,
        step=1
    )

    avg_amount_24h = st.number_input(
        "Average Amount (24h)",
        min_value=1.0,
        value=500.0,
        step=50.0
    )

    std_amount_24h = st.number_input(
        "Amount Std Dev (24h)",
        min_value=0.0,
        value=100.0,
        step=10.0
    )


# ============================================================
# DEVICE & NETWORK
# ============================================================

st.divider()

st.subheader("📱 Device & Network Signals")

col1, col2 = st.columns(2)

with col1:

    new_device = st.checkbox(
        "New Device"
    )

    device_id = st.text_input(
        "Device ID",
        value="DEVICE_001"
    )


with col2:

    new_ip = st.checkbox(
        "New IP Address"
    )

    ip_address = st.text_input(
        "IP Address",
        value="192.168.1.10"
    )


# ============================================================
# LOCATION
# ============================================================

st.divider()

st.subheader("📍 Location")

col1, col2 = st.columns(2)

with col1:

    latitude = st.number_input(
        "Current Latitude",
        value=28.61000,
        format="%.5f"
    )

    longitude = st.number_input(
        "Current Longitude",
        value=77.20000,
        format="%.5f"
    )


with col2:

    previous_latitude = st.number_input(
        "Previous Latitude",
        value=28.61000,
        format="%.5f"
    )

    previous_longitude = st.number_input(
        "Previous Longitude",
        value=77.20000,
        format="%.5f"
    )


# ============================================================
# BUILD TRANSACTION
# ============================================================

transaction = {

    "transaction_id": "DASHBOARD_TXN",

    "merchant_id": "MERCHANT_001",

    "amount": amount,

    "payment_method": payment_method,

    "failed_attempts": failed_attempts,

    "transactions_1min": transactions_1min,

    "transactions_5min": transactions_5min,

    "transactions_10min": transactions_10min,

    "transactions_1hour": transactions_1hour,

    "avg_amount_24h": avg_amount_24h,

    "std_amount_24h": std_amount_24h,

    "device_id": device_id,

    "ip_address": ip_address,

    "new_device": int(new_device),

    "new_ip": int(new_ip),

    "latitude": latitude,

    "longitude": longitude,

    "previous_latitude": previous_latitude,

    "previous_longitude": previous_longitude
}


# ============================================================
# PAYMENT RISK GATEWAY
# ============================================================

st.divider()

st.subheader("🚦 Payment Risk Gateway")

if st.button(
    "🔍 Analyze & Process Payment",
    type="primary",
    use_container_width=True
):

    try:

        with st.spinner(
            "Running AI risk engine..."
        ):

            gateway_result = process_payment(
                transaction
            )

        # Save SAME transaction
        st.session_state.transaction = transaction

        # Save gateway result
        st.session_state.gateway_result = gateway_result

        # Clear previous investigation
        st.session_state.investigation = None

    except Exception as e:

        st.error(
            f"❌ Payment gateway error: {e}"
        )


# ============================================================
# DISPLAY GATEWAY RESULT
# ============================================================

gateway_result = st.session_state.gateway_result


if gateway_result:

    st.divider()

    st.subheader("⚠️ Risk Assessment")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Risk Score",
            f"{gateway_result['risk_score']:.2f}/100"
        )

    with col2:

        st.metric(
            "Risk Level",
            gateway_result["risk_level"]
        )

    with col3:

        st.metric(
            "Decision",
            gateway_result["decision"]
        )


    # ========================================================
    # RISK COMPONENTS
    # ========================================================

    st.subheader("🧠 Risk Components")

    # Gateway currently returns only the final risk values.
    # Components are displayed if available.

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "ML Fraud Score",
            f"{gateway_result.get('ml_score', 0):.2f}"
        )

    with col2:

        st.metric(
            "Anomaly Score",
            f"{gateway_result.get('anomaly_score', 0):.2f}"
        )

    with col3:

        st.metric(
            "Behavior Score",
            f"{gateway_result.get('behavioral_score', 0):.2f}"
        )


    # ========================================================
    # REASONS
    # ========================================================

    st.subheader(
        "🚨 Why was this transaction flagged?"
    )

    reasons = gateway_result.get(
        "reasons",
        []
    )

    if reasons:

        for reason in reasons:

            st.warning(
                reason
            )

    else:

        st.success(
            "No major suspicious signals detected."
        )


    # ========================================================
    # PAYMENT STATUS
    # ========================================================

    st.subheader("💰 Payment Status")

    status = gateway_result["status"]

    if status == "APPROVED":

        st.success(
            "✅ Payment approved and Razorpay order created."
        )

        if gateway_result.get(
            "razorpay_order"
        ):

            st.write(
                "**Razorpay Order ID:** "
                + gateway_result[
                    "razorpay_order"
                ]["id"]
            )

    elif status == "BLOCKED":

        st.error(
            "🚨 Payment BLOCKED because of high fraud risk."
        )

    elif status == "REVIEW":

        st.warning(
            "⚠️ Payment requires manual investigation."
        )

    else:

        st.error(
            gateway_result["message"]
        )


# ============================================================
# TRANSACTION INFORMATION
# ============================================================

if st.session_state.transaction:

    current_transaction = (
        st.session_state.transaction
    )

    st.divider()

    st.subheader(
        "💳 Transaction Information"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Transaction ID:** "
            f"{current_transaction['transaction_id']}"
        )

        st.write(
            f"**Merchant ID:** "
            f"{current_transaction['merchant_id']}"
        )

        st.write(
            f"**Amount:** "
            f"₹{current_transaction['amount']:,.2f}"
        )

        st.write(
            f"**Payment Method:** "
            f"{current_transaction['payment_method']}"
        )

    with col2:

        st.write(
            f"**Failed Attempts:** "
            f"{current_transaction['failed_attempts']}"
        )

        st.write(
            f"**New Device:** "
            f"{'Yes' if current_transaction['new_device'] else 'No'}"
        )

        st.write(
            f"**New IP:** "
            f"{'Yes' if current_transaction['new_ip'] else 'No'}"
        )

        st.write(
            f"**Device ID:** "
            f"{current_transaction['device_id']}"
        )


    # ========================================================
    # VELOCITY
    # ========================================================

    st.subheader(
        "⚡ Transaction Velocity"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "1 Minute",
            current_transaction[
                "transactions_1min"
            ]
        )

    with col2:

        st.metric(
            "5 Minutes",
            current_transaction[
                "transactions_5min"
            ]
        )

    with col3:

        st.metric(
            "10 Minutes",
            current_transaction[
                "transactions_10min"
            ]
        )

    with col4:

        st.metric(
            "1 Hour",
            current_transaction[
                "transactions_1hour"
            ]
        )


# ============================================================
# AI INVESTIGATION
# ============================================================

st.divider()

st.subheader("🤖 AI Investigation")

st.write(
    "The investigation agent uses the SAME transaction "
    "that passed through the payment risk gateway."
)


if st.session_state.transaction:

    if st.button(
        "🧠 Run AI Investigation",
        use_container_width=True
    ):

        try:

            from agent import investigate

            with st.spinner(
                "AI agent is investigating the transaction..."
            ):

                investigation = investigate(
                    st.session_state.transaction
                )

            st.session_state.investigation = (
                investigation
            )

            st.success(
                "✅ AI investigation completed."
            )

        except Exception as e:

            st.error(
                f"❌ AI investigation failed: {e}"
            )

else:

    st.info(
        "First analyze a transaction using the Payment Risk Gateway."
    )


# ============================================================
# DISPLAY INVESTIGATION
# ============================================================

investigation = (
    st.session_state.investigation
)


if investigation:

    st.divider()

    st.subheader(
        "📋 AI Investigation Report"
    )


    # ========================================================
    # INVESTIGATION SUMMARY
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Risk Score",
            f"{investigation.get('risk_score', 0):.2f}/100"
        )

    with col2:

        st.metric(
            "Risk Level",
            investigation.get(
                "risk_level",
                "UNKNOWN"
            )
        )

    with col3:

        st.metric(
            "Recommendation",
            investigation.get(
                "recommendation",
                "UNKNOWN"
            )
        )


    # ========================================================
    # TOOLS USED
    # ========================================================

    st.subheader(
        "🔧 Investigation Tools Used"
    )

    tools = investigation.get(
        "tools_used",
        []
    )

    if tools:

        cols = st.columns(
            len(tools)
        )

        for col, tool in zip(
            cols,
            tools
        ):

            with col:

                st.success(
                    f"✓ {tool.upper()}"
                )

    else:

        st.info(
            "No additional investigation tools were required."
        )


    # ========================================================
    # EVIDENCE
    # ========================================================

    st.subheader(
        "🔎 Investigation Evidence"
    )

    evidence = investigation.get(
        "evidence",
        {}
    )

    if evidence:

        for tool, data in evidence.items():

            with st.expander(
                f"📊 {tool.upper()} Evidence"
            ):

                st.json(
                    data
                )

    else:

        st.info(
            "No investigation evidence collected."
        )


    # ========================================================
    # GEMINI REPORT
    # ========================================================

    st.subheader(
        "🧠 Gemini AI Investigation Report"
    )

    ai_report = investigation.get(
        "ai_report"
    )

    if ai_report:

        st.markdown(
            ai_report
        )

    else:

        st.warning(
            "Gemini did not return an investigation report."
        )