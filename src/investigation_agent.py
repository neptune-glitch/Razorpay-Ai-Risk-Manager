def investigate_transaction(
    transaction,
    risk_result
):
    """
    Generates an evidence-based investigation summary
    from the transaction and risk-engine results.
    """

    risk_score = risk_result["risk_score"]
    ml_score = risk_result["ml_score"]
    anomaly_score = risk_result["anomaly_score"]
    behavioral_score = risk_result["behavioral_score"]
    reasons = risk_result["reasons"]

    findings = []

    # ==========================================
    # AMOUNT ANALYSIS
    # ==========================================

    amount = transaction.get("amount", 0)
    avg_amount = transaction.get("avg_amount_24h", 0)

    if avg_amount > 0:

        amount_ratio = amount / avg_amount

        if amount_ratio >= 5:

            findings.append(
                f"Transaction amount is extremely high "
                f"relative to the merchant baseline "
                f"({amount_ratio:.1f}×)."
            )

        elif amount_ratio >= 2:

            findings.append(
                f"Transaction amount is significantly above "
                f"the merchant baseline ({amount_ratio:.1f}×)."
            )

        else:

            findings.append(
                "Transaction amount is within the expected range."
            )


    # ==========================================
    # VELOCITY ANALYSIS
    # ==========================================

    transactions_1min = transaction.get(
        "transactions_1min",
        0
    )

    transactions_5min = transaction.get(
        "transactions_5min",
        0
    )

    transactions_10min = transaction.get(
        "transactions_10min",
        0
    )

    if transactions_1min >= 5:

        findings.append(
            f"Very high transaction velocity detected: "
            f"{transactions_1min} transactions in one minute."
        )

    elif transactions_5min >= 10:

        findings.append(
            f"Elevated transaction velocity detected: "
            f"{transactions_5min} transactions in five minutes."
        )

    elif transactions_10min >= 15:

        findings.append(
            f"Elevated transaction velocity detected: "
            f"{transactions_10min} transactions in ten minutes."
        )

    else:

        findings.append(
            "Transaction velocity does not appear unusually high."
        )


    # ==========================================
    # DEVICE ANALYSIS
    # ==========================================

    if transaction.get("new_device", 0) == 1:

        findings.append(
            "Transaction originated from a previously unseen device."
        )

    else:

        findings.append(
            "Device is known to the system."
        )


    # ==========================================
    # IP ANALYSIS
    # ==========================================

    if transaction.get("new_ip", 0) == 1:

        findings.append(
            "Transaction originated from a previously unseen IP address."
        )

    else:

        findings.append(
            "IP address is known to the system."
        )


    # ==========================================
    # FAILED ATTEMPTS
    # ==========================================

    failed_attempts = transaction.get(
        "failed_attempts",
        0
    )

    if failed_attempts >= 3:

        findings.append(
            f"Multiple failed payment attempts detected "
            f"({failed_attempts})."
        )

    elif failed_attempts > 0:

        findings.append(
            f"{failed_attempts} failed payment attempt detected."
        )


    # ==========================================
    # MODEL ANALYSIS
    # ==========================================

    if ml_score >= 80:

        findings.append(
            "The fraud model assigns a high fraud probability."
        )

    elif ml_score >= 50:

        findings.append(
            "The fraud model identifies moderate fraud risk."
        )

    else:

        findings.append(
            "The fraud model does not identify strong fraud signals."
        )


    # ==========================================
    # ANOMALY ANALYSIS
    # ==========================================

    if anomaly_score >= 80:

        findings.append(
            "The transaction is highly unusual compared "
            "with normal transaction behavior."
        )

    elif anomaly_score >= 50:

        findings.append(
            "The transaction shows moderately unusual behavior."
        )

    else:

        findings.append(
            "The transaction is broadly consistent "
            "with normal behavioral patterns."
        )


    # ==========================================
    # FINAL RECOMMENDATION
    # ==========================================

    if risk_score >= 80:

        recommendation = "BLOCK"

        confidence = "HIGH"

        summary = (
            "The transaction presents multiple strong risk "
            "signals and should be blocked."
        )

    elif risk_score >= 50:

        recommendation = "MANUAL_REVIEW"

        confidence = "MEDIUM"

        summary = (
            "The transaction contains suspicious signals "
            "but requires additional human investigation."
        )

    else:

        recommendation = "APPROVE"

        confidence = "LOW"

        summary = (
            "The transaction does not show sufficient evidence "
            "of fraudulent behavior."
        )


    # ==========================================
    # RETURN INVESTIGATION
    # ==========================================

    return {

        "summary": summary,

        "recommendation": recommendation,

        "confidence": confidence,

        "risk_score": risk_score,

        "findings": findings,

        "risk_reasons": reasons
    }