# AI Payment Risk Manager

A Streamlit demo application for scoring payment fraud risk, routing suspicious payments to an investigation queue, collecting evidence, and recording investigator decisions.

## Features

- Random Forest fraud probability, Isolation Forest anomaly detection, and transparent behavioral checks combined into one risk score.
- Automated decisions: `APPROVE`, `MANUAL_REVIEW`, or `BLOCK`.
- Investigation queue with status tracking.
- Evidence gathering for merchant, device, IP, velocity, and location signals.
- Optional Gemini-generated investigation report.
- CSV audit trail for gateway and investigator decisions.
- Optional Razorpay order creation for approved payments.

## Requirements

Use Python **3.12 or 3.13**. The current local Python 3.14 setup does not have a compatible `pandas` distribution available from its configured package index.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Configure credentials

Create a `.env` file in the project root only when using the optional external integrations:

```env
GEMINI_API_KEY=your_gemini_key
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

For Streamlit Cloud, open the app settings, choose **Secrets**, and add the same
values in TOML format. Do not commit these values to Git:

```toml
GEMINI_API_KEY = "your_gemini_key"
RAZORPAY_KEY_ID = "your_razorpay_key_id"
RAZORPAY_KEY_SECRET = "your_razorpay_key_secret"
```

Without a Gemini key, investigations still collect and display evidence; the report states that Gemini is unavailable. Without Razorpay credentials, only an approved payment's order-creation step fails gracefully.

## Run the application

From the project root:

```powershell
streamlit run app/dashboard.py
```

Do not run files in `app/pages/` as separate Streamlit entry points. Streamlit discovers them automatically from the dashboard launch.

## Project layout

```text
app/
  dashboard.py                 Main Streamlit entry point
  pages/investigations.py      Investigation workflow
  pages/risk_monitor.py        Risk monitoring view
  pages/audit_log.py           Audit trail view
src/
  risk_engine.py               ML, anomaly, and behavioral scoring
  payment_gateway.py           Approval/review/block routing
  investigation_queue.py       CSV queue operations
  agent.py                     Evidence-gathering investigation agent
  llm_investigator.py          Optional Gemini report generation
  audit_logger.py              CSV audit logging
data/raw/transactions.csv      Demo transaction data
models/                        Serialized fraud and anomaly models
```

## Architecture

```text
                         Streamlit application
                    app/dashboard.py (entry point)
                                  |
                   +--------------+--------------+
                   |                             |
          Payment Risk Gateway            Investigation pages
        src/payment_gateway.py      app/pages/investigations.py
                   |                             |
                   v                             v
            Risk Engine                  Investigation Agent
         src/risk_engine.py                  src/agent.py
                   |                             |
       +-----------+-----------+       +---------+---------+
       |           |           |       |         |         |
       v           v           v       v         v         v
 Fraud model   Anomaly model  Behavioral   Merchant    Device / IP
  .pkl file     .pkl file      signals     history      history
       \           |           /              |
        +----------+----------+               v
                   |                    Velocity / location
                   v                    investigation tools
         Risk score and decision                  |
     APPROVE | MANUAL_REVIEW | BLOCK              v
                   |                    Optional Gemini report
                   |                 src/llm_investigator.py
       +-----------+-----------+                  |
       |                       |                  v
       v                       v             Investigator action
 Razorpay order       Investigation queue          |
 (approved only)   data/investigation_queue.csv    v
                                             Audit log CSV
                                         data/audit_log.csv
```

The dashboard sends each transaction to the risk engine. A low-risk payment is approved and can create a Razorpay order; a medium-risk payment is placed in the investigation queue; and a high-risk payment is blocked. Every gateway and investigator decision is retained in the audit log.

## Risk decision policy

The final score combines 60% ML fraud score, 20% anomaly score, and 20% behavioral score.

| Score | Level | Decision |
| --- | --- | --- |
| `>= 80` | HIGH | BLOCK |
| `>= 50` | MEDIUM | MANUAL_REVIEW |
| `< 50` | LOW | APPROVE |

## Useful checks

Run these from the project root after dependencies are installed:

```powershell
python -m src.risk_engine
python src/investigation_queue.py
python src/test_audit.py
python src/test_agent.py
python src/test_tools.py
python src/test_llm.py
```

The queue and audit test scripts intentionally add or update demo records in `data/`.

## Deployed Links 
- https://razorpay-ai-risk-manager-2bwwgnqe4sxrvapfmhztzc.streamlit.app/

## Notes

- The model artifacts were trained with scikit-learn 1.9.0; use the version declared in `requirements.txt` to avoid model-serialization warnings.
- This project is a demo workflow, not a production payment-security system. Use secure secret management, authenticated investigators, database storage, monitoring, and formal model validation before production use.
