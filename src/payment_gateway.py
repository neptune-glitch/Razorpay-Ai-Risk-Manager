try:
    from .risk_engine import calculate_risk
    from .razorpay_client import create_order
    from .audit_logger import log_investigator_action
    from .investigation_queue import add_to_investigation_queue
except ImportError:  # Supports `python src/payment_gateway.py`.
    from risk_engine import calculate_risk
    from razorpay_client import create_order
    from audit_logger import log_investigator_action
    from investigation_queue import add_to_investigation_queue


# ============================================================
# PAYMENT RISK GATEWAY
# ============================================================

def process_payment(transaction):
    """
    Process a payment through the AI risk engine.

    Flow:

        Transaction
             ↓
        Risk Engine
             ↓
      ┌──────┼─────────┐
      ↓      ↓         ↓
    APPROVE  REVIEW   BLOCK
      ↓      ↓         ↓
   Razorpay Queue    Audit
      ↓      ↓
     Audit  Audit
    """

    # --------------------------------------------------------
    # STEP 1: Calculate Risk
    # --------------------------------------------------------

    risk_result = calculate_risk(transaction)

    risk_score = risk_result["risk_score"]
    risk_level = risk_result["risk_level"]
    decision = risk_result["decision"]
    reasons = risk_result["reasons"]

    transaction_id = transaction.get(
        "transaction_id",
        "UNKNOWN"
    )

    # --------------------------------------------------------
    # STEP 2: BLOCK
    # --------------------------------------------------------

    if decision == "BLOCK":

        log_investigator_action(
            transaction_id=transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            ai_recommendation=decision,
            investigator_decision="BLOCK",
            reason="; ".join(reasons)
        )

        return {
            "status": "BLOCKED",
            "message": "Payment blocked due to high fraud risk.",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "decision": decision,
            "razorpay_order": None,
            "reasons": reasons
        }

    # --------------------------------------------------------
    # STEP 3: MANUAL REVIEW
    # --------------------------------------------------------

    if decision == "MANUAL_REVIEW":

        # Add transaction to investigation queue
        add_to_investigation_queue(
            transaction,
            risk_result
        )

        # Record gateway decision
        log_investigator_action(
            transaction_id=transaction_id,
            risk_score=risk_score,
            risk_level=risk_level,
            ai_recommendation=decision,
            investigator_decision="REVIEW",
            reason="; ".join(reasons)
        )

        return {
            "status": "REVIEW",
            "message": "Payment sent to AI investigation queue.",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "decision": decision,
            "ml_score": risk_result["ml_score"],
            "anomaly_score": risk_result["anomaly_score"],
            "behavioral_score": risk_result["behavioral_score"],
            "razorpay_order": None,
            "reasons": reasons
        }

    # --------------------------------------------------------
    # STEP 4: APPROVE
    # --------------------------------------------------------

    if decision == "APPROVE":

        try:

            # Create Razorpay order
            order = create_order(
                transaction["amount"]
            )

            # Record approval
            log_investigator_action(
                transaction_id=transaction_id,
                risk_score=risk_score,
                risk_level=risk_level,
                ai_recommendation=decision,
                investigator_decision="APPROVE",
                reason="Payment approved by risk engine"
            )

            return {
                "status": "APPROVED",
                "message": "Payment approved and Razorpay order created.",
                "risk_score": risk_score,
                "risk_level": risk_level,
                "decision": decision,
                "ml_score": risk_result["ml_score"],
                "anomaly_score": risk_result["anomaly_score"],
                "behavioral_score": risk_result["behavioral_score"],
                "razorpay_order": order,
                "reasons": reasons
            }

        except Exception as e:

            # Record gateway failure
            log_investigator_action(
                transaction_id=transaction_id,
                risk_score=risk_score,
                risk_level=risk_level,
                ai_recommendation=decision,
                investigator_decision="ERROR",
                reason=f"Razorpay order creation failed: {e}"
            )

            return {
                "status": "ERROR",
                "message": f"Razorpay order creation failed: {e}",
                "risk_score": risk_score,
                "risk_level": risk_level,
                "decision": decision,
                "ml_score": risk_result["ml_score"],
                "anomaly_score": risk_result["anomaly_score"],
                "behavioral_score": risk_result["behavioral_score"],
                "razorpay_order": None,
                "reasons": reasons
            }

    # --------------------------------------------------------
    # SAFETY FALLBACK
    # --------------------------------------------------------

    return {
        "status": "ERROR",
        "message": f"Unknown risk decision: {decision}",
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "ml_score": risk_result["ml_score"],
        "anomaly_score": risk_result["anomaly_score"],
        "behavioral_score": risk_result["behavioral_score"],
        "razorpay_order": None,
        "reasons": reasons
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        PAYMENT RISK GATEWAY TEST")
    print("==========================================")

    transaction = {

        "transaction_id":
            "GATEWAY_TEST_001",

        "merchant_id":
            "MERCHANT_001",

        "amount":
            12000,

        "payment_method":
            "CARD",

        "failed_attempts":
            7,

        "transactions_1min":
            33,

        "transactions_5min":
            47,

        "transactions_10min":
            119,

        "transactions_1hour":
            217,

        "avg_amount_24h":
            341.32,

        "std_amount_24h":
            109.6,

        "new_device":
            0,

        "new_ip":
            1,

        "device_id":
            "DEVICE_001",

        "ip_address":
            "192.168.1.10",

        "latitude":
            28.61000,

        "longitude":
            77.20000,

        "previous_latitude":
            28.61000,

        "previous_longitude":
            77.20000
    }

    # --------------------------------------------------------
    # PROCESS PAYMENT
    # --------------------------------------------------------

    result = process_payment(
        transaction
    )

    # --------------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------------

    print("\nStatus:")
    print(result["status"])

    print("\nMessage:")
    print(result["message"])

    print("\nRisk Score:")
    print(
        f"{result['risk_score']:.2f}/100"
    )

    print("\nRisk Level:")
    print(result["risk_level"])

    print("\nDecision:")
    print(result["decision"])

    print("\nReasons:")

    for reason in result["reasons"]:
        print(f"- {reason}")

    # --------------------------------------------------------
    # RAZORPAY ORDER
    # --------------------------------------------------------

    if result["razorpay_order"]:

        print("\nRazorpay Order:")

        print(
            result["razorpay_order"]
        )

    print("\n==========================================")
    print("       AUDIT LOG UPDATED")
    print("==========================================")
