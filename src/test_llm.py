import pandas as pd

try:
    from .agent import investigate
except ImportError:  # Supports `python src/test_llm.py`.
    from agent import investigate


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

report = result["ai_report"]


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
