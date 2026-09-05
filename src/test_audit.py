from audit_logger import (
    log_investigator_action,
    load_audit_log
)


print("\n==========================================")
print("          AUDIT LOG TEST")
print("==========================================")


log_investigator_action(

    transaction_id="TEST_TXN_001",

    risk_score=89.5,

    risk_level="HIGH",

    ai_recommendation="BLOCK",

    investigator_decision="BLOCK",

    reason="Confirmed suspicious transaction"
)


print("\nAudit log created successfully.")

print("\nCurrent Audit Log:")

print(
    load_audit_log()
)