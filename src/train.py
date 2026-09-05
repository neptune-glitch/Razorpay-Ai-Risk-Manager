import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, IsolationForest

try:
    from .features import load_data, prepare_features
except ImportError:  # Supports `python src/train.py`.
    from features import load_data, prepare_features


# ==========================================
# 1. Load data
# ==========================================

df = load_data()

print(f"Total transactions: {len(df)}")


# ==========================================
# 2. Feature engineering
# ==========================================

df = prepare_features(df)


# ==========================================
# 3. Separate features and target
# ==========================================

X = df.drop(columns=["is_fraud"])
y = df["is_fraud"]

print(f"Features: {X.shape[1]}")
print(f"Fraud cases: {int(y.sum())}")


# ==========================================
# 4. Train / test split
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")


# ==========================================
# 5. Random Forest
# ==========================================

print("\nTraining Random Forest...")

fraud_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

fraud_model.fit(
    X_train,
    y_train
)

joblib.dump(
    fraud_model,
    "models/fraud_model.pkl"
)

print("Random Forest saved.")


# ==========================================
# 6. Isolation Forest
# ==========================================

print("\nTraining Isolation Forest...")

# Isolation Forest learns what NORMAL
# behavior looks like.
#
# We train it only on normal transactions.
normal_data = X_train[
    y_train == 0
]

anomaly_model = IsolationForest(
    n_estimators=300,
    contamination=0.05,
    random_state=42,
    n_jobs=-1
)

anomaly_model.fit(
    normal_data
)

joblib.dump(
    anomaly_model,
    "models/anomaly_model.pkl"
)

print("Isolation Forest saved.")


# ==========================================
# 7. Final output
# ==========================================

print("\n========== TRAINING COMPLETE ==========")

print(
    f"Random Forest features: "
    f"{X.shape[1]}"
)

print(
    f"Normal samples used for "
    f"anomaly training: {len(normal_data)}"
)

print("\nModels:")

print("✓ models/fraud_model.pkl")
print("✓ models/anomaly_model.pkl")
