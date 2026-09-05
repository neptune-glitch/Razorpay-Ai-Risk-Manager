import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)

from features import load_data, prepare_features


# ==========================================
# 1. Load dataset
# ==========================================

df = load_data()

print(f"Total transactions: {len(df)}")


# ==========================================
# 2. Feature engineering
# ==========================================

df = prepare_features(df)


# ==========================================
# 3. Features / target
# ==========================================

X = df.drop(columns=["is_fraud"])
y = df["is_fraud"]

print(f"Features: {X.shape[1]}")
print(f"Fraud cases: {int(y.sum())}")


# ==========================================
# 4. Same test split used during training
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==========================================
# 5. Load models
# ==========================================

fraud_model = joblib.load(
    "models/fraud_model.pkl"
)

anomaly_model = joblib.load(
    "models/anomaly_model.pkl"
)


# ==========================================
# 6. Random Forest predictions
# ==========================================

fraud_predictions = fraud_model.predict(
    X_test
)


# ==========================================
# 7. Evaluate Random Forest
# ==========================================

print("\n==========================================")
print("       RANDOM FOREST PERFORMANCE")
print("==========================================")

print(
    f"\nPrecision : "
    f"{precision_score(y_test, fraud_predictions):.4f}"
)

print(
    f"Recall    : "
    f"{recall_score(y_test, fraud_predictions):.4f}"
)

print(
    f"F1 Score  : "
    f"{f1_score(y_test, fraud_predictions):.4f}"
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        fraud_predictions
    )
)


# ==========================================
# 8. Isolation Forest predictions
# ==========================================

anomaly_predictions = anomaly_model.predict(
    X_test
)

# Isolation Forest:
#   1  = normal
#  -1  = anomaly
#
# Convert to our fraud format:
#   0  = normal
#   1  = suspicious

anomaly_predictions = (
    anomaly_predictions == -1
).astype(int)


# ==========================================
# 9. Evaluate Isolation Forest
# ==========================================

print("\n==========================================")
print("       ISOLATION FOREST PERFORMANCE")
print("==========================================")

print(
    f"\nPrecision : "
    f"{precision_score(y_test, anomaly_predictions):.4f}"
)

print(
    f"Recall    : "
    f"{recall_score(y_test, anomaly_predictions):.4f}"
)

print(
    f"F1 Score  : "
    f"{f1_score(y_test, anomaly_predictions):.4f}"
)

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        anomaly_predictions
    )
)


# ==========================================
# 10. Classification report
# ==========================================

print("\n==========================================")
print("       ISOLATION FOREST REPORT")
print("==========================================")

print(
    classification_report(
        y_test,
        anomaly_predictions,
        target_names=[
            "Normal",
            "Suspicious"
        ]
    )
)