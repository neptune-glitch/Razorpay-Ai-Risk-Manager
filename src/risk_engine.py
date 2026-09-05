import os
import joblib
import pandas as pd
import numpy as np

try:
    from src.features import prepare_features
except ModuleNotFoundError:
    from features import prepare_features


# ============================================================
# PROJECT PATHS
# ============================================================

# Get the project root directory.
# risk_engine.py is inside:
# razorpay-ai-risk-manager/src/risk_engine.py
#
# Therefore:
# dirname(__file__)          -> src
# dirname(dirname(__file__)) -> project root

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)


MODELS_DIR = os.path.join(
    PROJECT_ROOT,
    "models"
)


FRAUD_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "fraud_model.pkl"
)


ANOMALY_MODEL_PATH = os.path.join(
    MODELS_DIR,
    "anomaly_model.pkl"
)


# ============================================================
# LOAD MODELS
# ============================================================

def load_models():
    """
    Load the trained fraud detection and anomaly detection
    models.
    """

    if not os.path.exists(FRAUD_MODEL_PATH):
        raise FileNotFoundError(
            f"Fraud model not found:\n{FRAUD_MODEL_PATH}"
        )

    if not os.path.exists(ANOMALY_MODEL_PATH):
        raise FileNotFoundError(
            f"Anomaly model not found:\n{ANOMALY_MODEL_PATH}"
        )

    fraud_model = joblib.load(
        FRAUD_MODEL_PATH
    )

    anomaly_model = joblib.load(
        ANOMALY_MODEL_PATH
    )

    return (
        fraud_model,
        anomaly_model
    )


# ============================================================
# CALCULATE BEHAVIORAL RISK
# ============================================================

def calculate_behavioral_score(transaction):
    """
    Calculate a transparent behavioral risk score.

    Score range:
        0 - 100

    Signals:
        - Amount anomaly
        - Transaction velocity
        - Failed attempts
        - New device
        - New IP
        - Geographic anomaly
    """

    score = 0

    # --------------------------------------------------------
    # Safely read transaction values
    # --------------------------------------------------------

    amount = float(
        transaction.get(
            "amount",
            0
        )
    )

    avg_amount = float(
        transaction.get(
            "avg_amount_24h",
            0
        )
    )

    velocity = int(
        transaction.get(
            "transactions_10min",
            0
        )
    )

    failures = int(
        transaction.get(
            "failed_attempts",
            0
        )
    )

    new_device = int(
        transaction.get(
            "new_device",
            0
        )
    )

    new_ip = int(
        transaction.get(
            "new_ip",
            0
        )
    )

    # ========================================================
    # 1. AMOUNT ANOMALY
    # ========================================================

    amount_ratio = (
        amount
        /
        (avg_amount + 1)
    )

    if amount_ratio >= 5:

        score += 30

    elif amount_ratio >= 3:

        score += 20

    elif amount_ratio >= 2:

        score += 10

    # ========================================================
    # 2. TRANSACTION VELOCITY
    # ========================================================

    if velocity >= 100:

        score += 30

    elif velocity >= 50:

        score += 20

    elif velocity >= 20:

        score += 10

    # ========================================================
    # 3. FAILED ATTEMPTS
    # ========================================================

    if failures >= 5:

        score += 15

    elif failures >= 3:

        score += 10

    elif failures >= 2:

        score += 5

    # ========================================================
    # 4. NEW DEVICE
    # ========================================================

    if new_device == 1:

        score += 10

    # ========================================================
    # 5. NEW IP
    # ========================================================

    if new_ip == 1:

        score += 10

    # ========================================================
    # 6. GEOGRAPHIC ANOMALY
    # ========================================================

    latitude = transaction.get(
        "latitude"
    )

    longitude = transaction.get(
        "longitude"
    )

    previous_latitude = transaction.get(
        "previous_latitude"
    )

    previous_longitude = transaction.get(
        "previous_longitude"
    )

    # Only calculate geographic anomaly if
    # all location values are available.

    if (
        latitude is not None
        and longitude is not None
        and previous_latitude is not None
        and previous_longitude is not None
    ):

        try:

            lat_diff = (
                float(latitude)
                -
                float(previous_latitude)
            )

            lon_diff = (
                float(longitude)
                -
                float(previous_longitude)
            )

            distance = np.sqrt(
                lat_diff ** 2
                +
                lon_diff ** 2
            )

            if distance > 5:

                score += 15

        except (
            ValueError,
            TypeError
        ):

            pass

    return min(
        score,
        100
    )


# ============================================================
# CALCULATE RISK
# ============================================================

def calculate_risk(transaction):
    """
    Calculate complete transaction risk.

    Combines:

        60% ML Fraud Score
        20% Anomaly Score
        20% Behavioral Score

    Returns:

        risk_score
        risk_level
        decision
        ml_score
        anomaly_score
        behavioral_score
        reasons
    """

    # ========================================================
    # 1. CONVERT TRANSACTION TO DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        [transaction]
    )

    # ========================================================
    # 2. FEATURE ENGINEERING
    # ========================================================

    try:

        features = prepare_features(
            df
        )

    except Exception as e:

        raise RuntimeError(
            f"Feature preparation failed: {e}"
        ) from e

    # Remove target column if it exists.

    features = features.drop(
        columns=["is_fraud"],
        errors="ignore"
    )

    # ========================================================
    # 3. LOAD MODELS
    # ========================================================

    fraud_model, anomaly_model = (
        load_models()
    )

    # ========================================================
    # 4. MATCH TRAINING FEATURE ORDER
    # ========================================================

    if hasattr(
        fraud_model,
        "feature_names_in_"
    ):

        training_columns = (
            fraud_model.feature_names_in_
        )

        features = features.reindex(
            columns=training_columns,
            fill_value=0
        )

    # ========================================================
    # 5. RANDOM FOREST FRAUD SCORE
    # ========================================================

    try:

        fraud_probability = (
            fraud_model
            .predict_proba(
                features
            )[0][1]
        )

    except Exception as e:

        raise RuntimeError(
            f"Fraud model prediction failed: {e}"
        ) from e

    ml_score = (
        float(fraud_probability)
        * 100
    )

    ml_score = float(
        np.clip(
            ml_score,
            0,
            100
        )
    )

    # ========================================================
    # 6. ISOLATION FOREST ANOMALY SCORE
    # ========================================================

    try:

        anomaly_raw = (
            anomaly_model
            .decision_function(
                features
            )[0]
        )

    except Exception as e:

        raise RuntimeError(
            f"Anomaly model prediction failed: {e}"
        ) from e

    # Lower decision_function
    # means more anomalous.

    anomaly_score = np.clip(
        (
            0.15
            -
            anomaly_raw
        )
        /
        0.30
        *
        100,
        0,
        100
    )

    anomaly_score = float(
        anomaly_score
    )

    # ========================================================
    # 7. BEHAVIORAL SCORE
    # ========================================================

    behavioral_score = (
        calculate_behavioral_score(
            transaction
        )
    )

    # ========================================================
    # 8. FINAL RISK SCORE
    # ========================================================

    final_score = (

        0.60
        *
        ml_score

        +

        0.20
        *
        anomaly_score

        +

        0.20
        *
        behavioral_score
    )

    final_score = round(
        float(
            np.clip(
                final_score,
                0,
                100
            )
        ),
        2
    )

    # ========================================================
    # 9. RISK LEVEL + DECISION
    # ========================================================

    if final_score >= 80:

        risk_level = "HIGH"

        decision = "BLOCK"

    elif final_score >= 50:

        risk_level = "MEDIUM"

        decision = "MANUAL_REVIEW"

    else:

        risk_level = "LOW"

        decision = "APPROVE"

    # ========================================================
    # 10. EXPLANATION / REASONS
    # ========================================================

    reasons = []

    amount = float(
        transaction.get(
            "amount",
            0
        )
    )

    avg_amount = float(
        transaction.get(
            "avg_amount_24h",
            0
        )
    )

    amount_ratio = (
        amount
        /
        (avg_amount + 1)
    )

    # --------------------------------------------------------
    # Amount
    # --------------------------------------------------------

    if amount_ratio >= 3:

        reasons.append(
            f"Transaction amount is "
            f"{amount_ratio:.1f}× "
            f"the normal average"
        )

    # --------------------------------------------------------
    # Velocity
    # --------------------------------------------------------

    transactions_10min = int(
        transaction.get(
            "transactions_10min",
            0
        )
    )

    if transactions_10min >= 20:

        reasons.append(
            "High transaction velocity"
        )

    # --------------------------------------------------------
    # Failed attempts
    # --------------------------------------------------------

    failed_attempts = int(
        transaction.get(
            "failed_attempts",
            0
        )
    )

    if failed_attempts >= 3:

        reasons.append(
            "Multiple failed payment attempts"
        )

    # --------------------------------------------------------
    # New device
    # --------------------------------------------------------

    if int(
        transaction.get(
            "new_device",
            0
        )
    ) == 1:

        reasons.append(
            "New device detected"
        )

    # --------------------------------------------------------
    # New IP
    # --------------------------------------------------------

    if int(
        transaction.get(
            "new_ip",
            0
        )
    ) == 1:

        reasons.append(
            "New IP address detected"
        )

    # --------------------------------------------------------
    # Behavioral score
    # --------------------------------------------------------

    if behavioral_score >= 50:

        reasons.append(
            "Multiple behavioral risk signals detected"
        )

    # --------------------------------------------------------
    # Anomaly score
    # --------------------------------------------------------

    if anomaly_score >= 70:

        reasons.append(
            "Transaction behavior is highly unusual"
        )

    # --------------------------------------------------------
    # Default explanation
    # --------------------------------------------------------

    if not reasons:

        reasons.append(
            "No major suspicious behavioral "
            "signals detected"
        )

    # ========================================================
    # RETURN COMPLETE RESULT
    # ========================================================

    return {

        "risk_score": final_score,

        "risk_level": risk_level,

        "decision": decision,

        "ml_score": round(
            ml_score,
            2
        ),

        "anomaly_score": round(
            anomaly_score,
            2
        ),

        "behavioral_score": round(
            behavioral_score,
            2
        ),

        "reasons": reasons
    }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    # ========================================================
    # BORDERLINE TRANSACTION
    # ========================================================

    borderline_transaction = {

        "transaction_id":
            "TEST_BORDERLINE",

        "merchant_id":
            "MERCHANT_020",

        "amount":
            1500,

        "payment_method":
            "UPI",

        "failed_attempts":
            2,

        "transactions_1min":
            5,

        "transactions_5min":
            10,

        "transactions_10min":
            18,

        "transactions_1hour":
            60,

        "avg_amount_24h":
            500,

        "std_amount_24h":
            150,

        "device_id":
            "DEVICE_999",

        "ip_address":
            "192.168.50.20",

        "new_device":
            1,

        "new_ip":
            0,

        "latitude":
            28.61,

        "longitude":
            77.20,

        "previous_latitude":
            28.60,

        "previous_longitude":
            77.19
    }

    print(
        "\n=========================================="
    )

    print(
        "       BORDERLINE TRANSACTION TEST"
    )

    print(
        "=========================================="
    )

    try:

        result = calculate_risk(
            borderline_transaction
        )

        print(
            f"\nFinal Risk Score : "
            f"{result['risk_score']}/100"
        )

        print(
            f"Risk Level       : "
            f"{result['risk_level']}"
        )

        print(
            f"Decision         : "
            f"{result['decision']}"
        )

        print(
            f"ML Score         : "
            f"{result['ml_score']}"
        )

        print(
            f"Anomaly Score    : "
            f"{result['anomaly_score']}"
        )

        print(
            f"Behavior Score   : "
            f"{result['behavioral_score']}"
        )

        print(
            "\nReasons:"
        )

        for reason in result["reasons"]:

            print(
                f"- {reason}"
            )

        print(
            "\n=========================================="
        )

        print(
            "             TEST COMPLETED"
        )

        print(
            "=========================================="
        )

    except Exception as e:

        print(
            "\n❌ Risk Engine Error:"
        )

        print(e)