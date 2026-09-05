import os
import pandas as pd

try:
    from .risk_engine import calculate_risk
    from .investigation_tools import (
        check_merchant_history, check_device_history, check_ip_history,
        check_transaction_velocity, check_location_anomaly,
    )
    from .llm_investigator import generate_investigation_report
except ImportError:  # Supports `python src/agent.py`.
    from risk_engine import calculate_risk
    from investigation_tools import (
        check_merchant_history, check_device_history, check_ip_history,
        check_transaction_velocity, check_location_anomaly,
    )
    from llm_investigator import generate_investigation_report


# ============================================================
# LOAD DATA
# ============================================================

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "transactions.csv")

df = pd.read_csv(DATA_PATH)


# ============================================================
# INVESTIGATION AGENT
# ============================================================

def investigate(transaction):

    # --------------------------------------------------------
    # STEP 1: RISK ENGINE
    # --------------------------------------------------------

    risk_result = calculate_risk(transaction)

    risk_score = risk_result["risk_score"]
    ml_score = risk_result["ml_score"]
    behavioral_score = risk_result["behavioral_score"]
    anomaly_score = risk_result["anomaly_score"]


    # --------------------------------------------------------
    # STEP 2: SELECT INVESTIGATION TOOLS
    # --------------------------------------------------------

    evidence = {}

    tools_used = []


    # High ML risk → merchant investigation

    if ml_score >= 50:

        evidence["merchant"] = check_merchant_history(
            transaction,
            df
        )

        tools_used.append("merchant")


    # New device → device investigation

    if transaction.get("new_device", 0) == 1:

        evidence["device"] = check_device_history(
            transaction,
            df
        )

        tools_used.append("device")


    # New IP → IP investigation

    if transaction.get("new_ip", 0) == 1:

        evidence["ip"] = check_ip_history(
            transaction,
            df
        )

        tools_used.append("ip")


    # High behavioral risk → velocity investigation

    if behavioral_score >= 25:

        evidence["velocity"] = check_transaction_velocity(
            transaction
        )

        tools_used.append("velocity")


    # High anomaly → location investigation

    if anomaly_score >= 50:

        evidence["location"] = check_location_anomaly(
            transaction
        )

        tools_used.append("location")


    # --------------------------------------------------------
    # STEP 3: FINAL RECOMMENDATION
    # --------------------------------------------------------

    if risk_score >= 80:

        recommendation = "BLOCK"

    elif risk_score >= 50:

        recommendation = "MANUAL_REVIEW"

    else:

        recommendation = "APPROVE"


    # --------------------------------------------------------
    # STEP 4: BUILD INVESTIGATION DATA
    # --------------------------------------------------------

    investigation_data = {

        "transaction": transaction,

        "risk_score": risk_score,

        "risk_level": risk_result["risk_level"],

        "recommendation": recommendation,

        "ml_score": ml_score,

        "anomaly_score": anomaly_score,

        "behavioral_score": behavioral_score,

        "risk_reasons": risk_result["reasons"],

        "tools_used": tools_used,

        "evidence": evidence
    }


    # --------------------------------------------------------
    # STEP 5: GEMINI INVESTIGATION
    # --------------------------------------------------------

    try:

        ai_report = generate_investigation_report(
            transaction,
            investigation_data,
            evidence,
        )

    except Exception as e:

        ai_report = (
            f"Gemini investigation unavailable: {e}"
        )


    # --------------------------------------------------------
    # STEP 6: FINAL RESULT
    # --------------------------------------------------------

    return {

        "transaction_id":
            transaction.get("transaction_id"),

        "risk_score":
            risk_score,

        "risk_level":
            risk_result["risk_level"],

        "recommendation":
            recommendation,

        "ml_score":
            ml_score,

        "anomaly_score":
            anomaly_score,

        "behavioral_score":
            behavioral_score,

        "risk_reasons":
            risk_result["reasons"],

        "tools_used":
            tools_used,

        "evidence":
            evidence,

        "ai_report":
            ai_report
    }


# ============================================================
# TEST AGENT
# ============================================================

if __name__ == "__main__":

    fraud_transactions = df[
        df["is_fraud"] == 1
    ]

    transaction = (
        fraud_transactions
        .iloc[0]
        .to_dict()
    )


    result = investigate(
        transaction
    )


    print("\n==========================================")
    print("          AI INVESTIGATION AGENT")
    print("==========================================")


    print(
        f"\nTransaction ID: "
        f"{result['transaction_id']}"
    )

    print(
        f"Risk Score: "
        f"{result['risk_score']:.2f}/100"
    )

    print(
        f"Risk Level: "
        f"{result['risk_level']}"
    )

    print(
        f"Recommendation: "
        f"{result['recommendation']}"
    )


    print("\nRisk Reasons:")

    for reason in result["risk_reasons"]:

        print(
            f"- {reason}"
        )


    print("\nTools Used:")

    for tool in result["tools_used"]:

        print(
            f"✓ {tool}"
        )


    print("\nEvidence:")

    for tool, data in result["evidence"].items():

        print(
            f"\n--- {tool.upper()} ---"
        )

        print(data)


    print("\n==========================================")
    print("          GEMINI INVESTIGATION")
    print("==========================================")

    print(
        result["ai_report"]
    )
