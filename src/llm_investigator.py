import json
import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from google import genai
except ImportError:  # pragma: no cover - handled gracefully at runtime.
    genai = None


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _dotenv_candidates():
    """Return the most likely .env locations for this project."""
    candidates = [
        Path.cwd() / ".env",
        PROJECT_ROOT / ".env",
    ]

    for parent in [Path.cwd(), PROJECT_ROOT]:
        for path in parent.parents:
            candidates.append(path / ".env")

    seen = set()
    ordered = []
    for path in candidates:
        resolved = path.resolve(strict=False)
        if resolved not in seen:
            seen.add(resolved)
            ordered.append(resolved)
    return ordered


def resolve_api_key():
    """Read the project .env reliably, regardless of the current working directory."""
    for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        api_key = os.getenv(key_name)
        if api_key and api_key.strip():
            return api_key.strip()

    # Streamlit Cloud exposes app secrets through st.secrets rather than .env.
    try:
        import streamlit as st

        for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            api_key = st.secrets.get(key_name)
            if api_key and str(api_key).strip():
                return str(api_key).strip()
    except Exception:  # Local runs may not have a Streamlit secrets file.
        pass

    for dotenv_path in _dotenv_candidates():
        load_dotenv(dotenv_path=dotenv_path, override=False)
        for key_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
            api_key = os.getenv(key_name)
            if api_key and api_key.strip():
                return api_key.strip()

    return None


API_KEY = resolve_api_key()


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

    api_key = resolve_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini is unavailable: set GEMINI_API_KEY or GOOGLE_API_KEY in the environment or project .env."
        )

    if genai is None:
        raise RuntimeError("google-genai is not installed in the active environment.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text
