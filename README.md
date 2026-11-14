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
- **Character Error Rate (CER) Engine:**
  - Segments text using Unicode UAX #29 extended grapheme clusters (`\X` via `regex`) to preserve Indic base consonants with attached matras, viramas, and chillus as single character units.
  - Strict whitespace exclusion policy for unambiguous character evaluation.
- **Critical Information Detection Engine:**
  - Identifies numbers, dates, times, currency amounts, phone numbers, Malayalam/English negations, and named entities.
  - Two-pass alignment prioritizes exact identity matches before checking changed values.
- **Acoustic Quality & Clean/Noisy Degradation Comparison:**
  - Locally analyzes PCM WAV metrics (peak amplitude, RMS dBFS, clipping %, silence %).
  - Computes degradation deltas ($\Delta \text{WER}$, $\Delta \text{CER}$, critical retention) between paired clean and noisy audio.
- **Reproducible Malayalam Benchmark Platform (Tab 3):**
  - Discovers and validates genuine Malayalam benchmark audio (`dataset/normal/`) against ground-truth transcripts (`dataset/transcripts/`).
  - Standardized Aggregate WER & CER computation ($\sum \text{errors} / \sum \text{reference units}$).
  - Full transparency: explicitly reports paired clean/noisy absence without fake noise fabrication.
  - Exports Benchmark Summary TXT, Sample-Level CSV, and Aggregate Metrics CSV.
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
> **API Testing & Verification Status:** During live testing with Gnani Prisma STT (`https://api.vachana.ai/stt/v3`), an earlier request encountered an upstream Cloudflare `HTTP 504 Gateway Time-out`. In a subsequent live evaluation, one live Malayalam speech recording was successfully transcribed with **8/8 words correct and 0% WER**. However, **one successful sample does not establish general Malayalam transcription accuracy** across diverse speakers or regional dialects. Additionally, the benchmark platform contains **five normal Malayalam speech recordings** (`dataset/normal/`) and **does not contain genuine noisy recording pairs**. See [LIMITATIONS.md](LIMITATIONS.md) for full details.

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
git clone https://github.com/saviosinto123/NADHAM-QA.git
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

Run the complete 102-test automated verification suite:
```bash
pytest tests/test_nadham_qa.py -v
```

All 102 tests validate:
- Malayalam chillu normalization and zero-width character handling
- Currency, decimal, and date preservation
- Levenshtein WER computation and edit operation accounting
- Character Error Rate (CER) over Unicode UAX #29 extended grapheme clusters (`\X`)
- Critical Information Detection across 7 high-risk categories and two-pass alignment
- Mocked API interactions, status code exceptions, and HTML error sanitization
- Zero-byte rejection and 25 MB size limits
- Local acoustic signal quality analysis for PCM WAV files (RMS, peak, clipping, silence)
- Clean vs. Noisy speech degradation benchmarking and delta calculations
- Benchmark dataset discovery, double extension stripping, and sample validation
- Global aggregate error quotients ($\sum \text{errors} / \sum \text{units}$)
- Downloadable evidence reports (Summary TXT, Sample CSV, Aggregate CSV)

---

## 📁 Project Structure

```text
NADHAM-QA/
├── app.py                         # Core Streamlit application, NLP engines & evaluation pipeline
├── requirements.txt               # Production Python dependencies
├── .env                           # Local API credentials (git-ignored)
├── .gitignore                     # Git ignore rules (.env, .venv, cache)
├── dataset/                       # Malayalam Benchmark Dataset
│   ├── normal/                    # 5 genuine Malayalam audio recordings (.mp3.mp3)
│   └── transcripts/               # 5 matching ground-truth UTF-8 transcripts (.mp3.txt)
├── tests/
│   └── test_nadham_qa.py          # 101 automated unit & integration tests
├── scratch/
│   ├── test_apptest_verification.py # Streamlit AppTest headless UI verification
│   └── test_step5_logic.py        # Logic verification scripts
├── project_docs/                  # Comprehensive Challenge Documentation
│   ├── README.md                  # Project overview and setup instructions
│   ├── PROJECT_REPORT.md          # 20-section submission report for Gnani AI
│   ├── ARCHITECTURE.md            # System architecture & Mermaid flow diagrams
│   ├── FEATURES.md                # Full feature specification (Steps 1–5)
│   ├── TESTING_REPORT.md          # Automated testing & verification report
│   ├── LIMITATIONS.md             # Transparent upstream API status & limitations
│   ├── DEMO_SCRIPT.md             # 3–5 minute step-by-step video demonstration script
│   ├── INTERVIEW_PREPARATION.md   # Pitches, deep dives & 25 interview Q&As
│   ├── SUBMISSION_CHECKLIST.md    # Challenge submission checklist & deadline tracking
│   └── LINKEDIN_POST.md           # Social media announcement copy (LinkedIn & X)
└── .venv/                         # Local Python virtual environment
```
