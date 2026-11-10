# 🎙️ NADHAM QA

**Kerala-first. India-ready.**  
*Indian Voice Intelligence & Speech Recognition Testing Platform*

---

## 📌 Overview

**NADHAM QA** is an enterprise-grade evaluation and quality assurance platform built to benchmark Indian speech recognition models, specifically integrating the **Gnani Prisma STT (v2.5)** engine via the Vachana STT v3 API. 

Designed with a Kerala-first approach, NADHAM QA addresses linguistic complexities unique to Malayalam and Indic languages—including Unicode chillu character variations, zero-width joiners, complex ligatures, and domain-critical entities (currency values, dates, and decimals). It pairs Levenshtein-based Word Error Rate (WER) computation with word-level error classification and multi-format reporting.

---

## ✨ Key Capabilities

- **Indic & Malayalam Normalization Engine:**
  - Standardizes modern atomic chillu characters (`ൺ`, `ൻ`, `ർ`, `ൽ`, `ൾ`, `ൿ`) and legacy consonant + virama + ZWJ sequences into canonical Unicode forms.
  - Resolves Zero-Width Spaces (`\u200B`) and non-breaking spaces to avoid artificial word-gluing.
  - Strips isolated zero-width format controls (`\u200C`, `\u200D`).
  - Preserves critical decimal numbers (e.g., `3.14`) and standard date formats (e.g., `15/08/1947`).
  - Normalizes currency symbols (`₹`, `$`, `€`, `£`) while retaining numerical values.
- **Wagner-Fischer Alignment & Detailed Diagnostics:**
  - Implements dynamic programming Levenshtein alignment at the word level.
  - Accurately tracks **Substitutions**, **Insertions**, and **Deletions** alongside overall Word Error Rate (WER).
- **Audio Verification & Safety Guardrails:**
  - Embedded audio playback (`st.audio`) for direct audio auditioning.
  - Client-side rejection of 0-byte (empty) audio files to protect API quotas.
  - Enforced 25 MB upload ceiling to mitigate memory exhaustion (DoS).
  - Validation against punctuation-only or empty reference transcripts.
- **Robust Session State & Error Sanitization:**
  - Immediate state invalidation on new test runs to eliminate stale metrics.
  - Automatic error sanitization converting upstream proxy/gateway HTML (e.g. Cloudflare 502/504) into clean, human-readable notifications.
- **Comprehensive Reporting:**
  - Instant word-level error inspection via interactive tables.
  - Downloadable comprehensive plain-text reports (`.txt`) featuring execution timestamps, source audio metadata, transcripts, and aligned error tables.
  - Structured CSV export (`.csv`) for programmatic analysis.

> [!NOTE]
> **Upstream API Status Disclosure:** During real-world verification, requests to the live Gnani Prisma endpoint (`https://api.vachana.ai/stt/v3`) returned an upstream Cloudflare `HTTP 504 Gateway Time-out`. Client-side request formatting and HTML error sanitization are fully verified, but live transcription accuracy on spoken audio remains unverified until the upstream service latency is resolved. See [LIMITATIONS.md](LIMITATIONS.md) for full details.

---

## 🛠️ Technology Stack

- **Core Language:** Python 3.10+ (Tested on Python 3.14)
- **Web Interface:** Streamlit (>= 1.30.0)
- **Data & Normalization:** Pandas, Unicode Character Database (`unicodedata`), Regex (`re`)
- **HTTP Client:** Requests (>= 2.28.0)
- **Environment Management:** `python-dotenv`
- **Testing & Verification:** Pytest (>= 8.0.0), Streamlit `AppTest`

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- Python 3.10 or higher installed.
- Git installed.

### 2. Clone the Repository
```bash
git clone https://github.com/your-repo/NADHAM-QA.git
cd NADHAM-QA
```

### 3. Create and Activate Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

On Windows (Command Prompt):
```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
```

On Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Configuration
Create a `.env` file in the root directory:
```env
GNANI_API_KEY=your_gnani_prisma_api_key_here
```
> [!IMPORTANT]
> Never commit your `.env` file to version control. The `.gitignore` file is configured to exclude it automatically.

---

## 💻 Running the Application

Launch the Streamlit dashboard:
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the complete 32-test Pytest test suite:
```bash
pytest tests/test_nadham_qa.py -v
```

All 32 tests validate:
- Malayalam chillu normalization and zero-width character handling
- Currency, decimal, and date preservation
- Levenshtein WER computation and edit operation accounting
- Mocked API interactions, status code exceptions, and error sanitization
- Zero-byte rejection and 25 MB size limits
- Report generation and CSV formatting

---

## 📁 Project Structure

```text
NADHAM-QA/
├── app.py                      # Core Streamlit application & evaluation pipeline
├── requirements.txt            # Project dependencies
├── .env                        # Local API credentials (git-ignored)
├── .gitignore                  # Git ignore rules (.env, .venv, cache)
├── tests/
│   └── test_nadham_qa.py       # 32 automated unit & integration tests
├── project_docs/               # Technical & evaluation documentation
│   ├── README.md               # Project overview and setup instructions
│   ├── PROJECT_REPORT.md       # Comprehensive submission report for Gnani AI
│   ├── ARCHITECTURE.md         # System architecture & Mermaid flow diagrams
│   ├── FEATURES.md             # Full feature documentation
│   ├── TESTING_REPORT.md       # Detailed test execution & verification report
│   ├── LIMITATIONS.md          # Upstream API status & verification notes
│   └── DEMO_SCRIPT.md          # 3-minute presentation script
└── .venv/                      # Python virtual environment (local only)
```
