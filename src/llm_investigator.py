import os
import json

from google import genai
from dotenv import load_dotenv


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables."
    )


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=API_KEY
)


# ==========================================
# INVESTIGATION REPORT
# ==========================================

def generate_investigation_report(
    transaction,
    risk_result,
    evidence
):

    prompt = f"""
You are an AI payment fraud investigation assistant.

Analyze the transaction and the evidence collected
by the fraud detection system.

IMPORTANT RULES:

1. Do not invent evidence.
2. Only use information provided below.
3. The numerical risk score and recommendation come
   from the risk engine and should not be changed.
4. Explain WHY the transaction received this risk level.
5. Distinguish between strong evidence and weak evidence.
6. Mention signals that reduce suspicion as well.
7. Keep the investigation report concise and professional.

========================================
TRANSACTION
========================================

{json.dumps(transaction, indent=2, default=str)}

========================================
RISK ENGINE RESULT
========================================

Risk Score:
{risk_result.get("risk_score")}

Risk Level:
{risk_result.get("risk_level")}

Recommendation:
{risk_result.get("recommendation")}

ML Fraud Score:
{risk_result.get("ml_score")}

Anomaly Score:
{risk_result.get("anomaly_score")}

Behavior Score:
{risk_result.get("behavioral_score")}

Risk Reasons:
{json.dumps(risk_result.get("risk_reasons", []), indent=2)}

========================================
INVESTIGATION EVIDENCE
========================================

{json.dumps(evidence, indent=2, default=str)}

========================================
OUTPUT FORMAT
========================================

Return the investigation using exactly these sections:

SUMMARY:
A short explanation of the overall risk.

STRONG EVIDENCE:
Bullet points containing the strongest evidence.

WEAK_OR_REDUCING_SIGNALS:
Bullet points containing evidence that reduces suspicion
or is not strongly suspicious.

REASONING:
Explain how the evidence supports the risk assessment.

CONFIDENCE:
HIGH, MEDIUM, or LOW

FINAL_RECOMMENDATION:
Repeat the risk engine recommendation exactly.
"""

    # ==========================================
    # GEMINI REQUEST
    # ==========================================

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text