import pandas as pd

from agent import investigate
from llm_investigator import generate_investigation_report


# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    "data/raw/transactions.csv"
)


# ==========================================
# SELECT FRAUD TRANSACTION
# ==========================================

transaction = (
    df[df["is_fraud"] == 1]
    .iloc[0]
    .to_dict()
)


# ==========================================
# RUN INVESTIGATION AGENT
# ==========================================

result = investigate(
    transaction
)


# ==========================================
# GENERATE LLM REPORT
# ==========================================

report = generate_investigation_report(
    transaction,
    result,
    result["evidence"]
)


# ==========================================
# PRINT REPORT
# ==========================================

print("\n==========================================")
print("        AI INVESTIGATION REPORT")
print("==========================================")

print(
    f"\nTransaction: "
    f"{result['transaction_id']}"
)

print(
    f"Risk Score: "
    f"{result['risk_score']}/100"
)

print(
    f"Risk Level: "
    f"{result['risk_level']}"
)

print(
    f"Recommendation: "
    f"{result['recommendation']}"
)

print("\n------------------------------------------")
print("GEMINI INVESTIGATION")
print("------------------------------------------")

print(report)