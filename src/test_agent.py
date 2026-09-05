import pandas as pd

from risk_engine import calculate_risk

from investigation_agent import investigate_transaction


# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    "data/raw/transactions.csv"
)


# ==========================================
# SELECT A FRAUD TRANSACTION
# ==========================================

fraud_transactions = df[
    df["is_fraud"] == 1
]


transaction = (
    fraud_transactions
    .iloc[0]
    .to_dict()
)


# ==========================================
# RUN RISK ENGINE
# ==========================================

risk_result = calculate_risk(
    transaction
)


# ==========================================
# RUN INVESTIGATION AGENT
# ==========================================

investigation = investigate_transaction(
    transaction,
    risk_result
)


# ==========================================
# DISPLAY
# ==========================================

print("\n==========================================")
print("       AI INVESTIGATION REPORT")
print("==========================================")

print(
    f"\nRisk Score: "
    f"{investigation['risk_score']}/100"
)

print(
    f"Recommendation: "
    f"{investigation['recommendation']}"
)

print(
    f"Confidence: "
    f"{investigation['confidence']}"
)


print("\nSummary:")

print(
    investigation["summary"]
)


print("\nEvidence:")

for finding in investigation["findings"]:

    print(
        f"- {finding}"
    )