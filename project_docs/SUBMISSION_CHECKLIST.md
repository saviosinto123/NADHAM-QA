# 📋 NADHAM QA 2.0: Challenge Submission Checklist

**Challenge:** Gnani AI Great Indian AI Internship Challenge 2026  
**Submission Deadline:** **November 15, 2026, 6:00 PM IST**  
**Status:** **Ready for User Final Review & Submission**  

---

## 📌 1. Project Information & Public Metadata

- **Public Project Title:**  
  `NADHAM QA: Kerala-First Indian Voice Intelligence Testing Platform`
- **Short Project Description (Elevator Summary):**  
  *NADHAM QA is an enterprise-grade testing and reliability platform built for Indian voice intelligence models, integrating Gnani Prisma STT v2.5. Featuring Malayalam Unicode normalization, Wagner-Fischer Word Error Rate (WER), Character Error Rate (CER) over extended grapheme clusters, two-pass Critical Information Detection, local acoustic signal analysis, and reproducible aggregate batch benchmarking.*
- **Primary Problem Solved:**  
  *Standard Western speech recognition evaluation tools fail on Indian language orthography—penalizing visual-equivalent chillu letters, zero-width joiners, and agglutinative suffixes. NADHAM QA delivers scientific linguistic normalization, fine-grained character evaluation, and domain-critical entity auditing for Indian Voice AI.*
- **Gnani Models & APIs Integrated:**  
  - Engine: **Gnani Prisma STT v2.5**
  - Endpoint: `https://api.vachana.ai/stt/v3`
  - Target Languages: Malayalam (`ml-IN`), English (`en-IN`), Hindi (`hi-IN`)
- **Technology Stack:**  
  Python 3.10+ (tested on Python 3.14.8), Streamlit (v1.67.0), Pandas, NumPy, Unicode Regular Expressions (`regex` \X), Python `wave`.

---

## 🔗 2. Public URLs & Deliverables

| Deliverable | URL / Reference | Status | Action Required |
|---|---|:---:|---|
| **Live Streamlit Application** | https://nadham-voice.streamlit.app/ | ✅ Live & Operational | Test access in incognito |
| **GitHub Source Repository** | https://github.com/saviosinto123/NADHAM-QA | ✅ Codebase Complete | Review repository before push |
| **Project Documentation** | [project_docs/](.) | ✅ 8 Comprehensive Docs | Ready for evaluators |
| **Demo Video Link** | `[USER ACTION REQUIRED: Insert Video URL Here]` | ⏳ Pending Recording | Record 3–5 min video using [DEMO_SCRIPT.md](DEMO_SCRIPT.md) |
| **LinkedIn Post Link** | `[USER ACTION REQUIRED: Insert LinkedIn URL Here]` | ⏳ Pending Post | Copy text from [LINKEDIN_POST.md](LINKEDIN_POST.md) |
| **X / Twitter Post Link** | `[USER ACTION REQUIRED: Insert X Post URL Here]` | ⏳ Pending Post | Copy short text from [LINKEDIN_POST.md](LINKEDIN_POST.md) |

---

## 🛡️ 3. Security & Credential Hygiene Checklist

- [x] **API Key Security:** `GNANI_API_KEY` is never hardcoded in `app.py`, test files, or scripts.
- [x] **Git & Repository Safety:** `.env` is listed in `.gitignore` and has never been committed.
- [x] **Downloadable Reports Safety:** Plain-text (`.txt`) and CSV export generators never write or leak API keys, tokens, or credentials.
- [x] **Streamlit Secrets Support:** The application resolves credentials from `os.getenv` with fallback to `st.secrets["GNANI_API_KEY"]` for cloud deployment.
- [x] **Upload Protection:** 0-byte audio rejected locally to protect API credits. 25 MB file limit enforced.
- [x] **Gateway Sanitization:** Upstream Cloudflare 502/504 gateway timeout HTML pages are intercepted and sanitized.

---

## 🧪 4. Automated Testing & Verification Checklist

- [x] **Pytest Suite:** 101 tests passing (`tests/test_nadham_qa.py`) with 100% pass rate in ~5.04s.
- [x] **Streamlit Headless AppTest:** 100% passed across all 3 UI tabs (`scratch/test_apptest_verification.py`).
- [x] **Unicode Normalization:** Validated atomic vs legacy chillu, ZWJ/ZWSP, decimals, dates, currency.
- [x] **WER Alignment:** Dynamic programming matrix and operation paths (S/D/I) mathematically verified.
- [x] **CER Graphemes:** Unicode UAX #29 extended grapheme clusters (`\X`) and whitespace exclusion verified.
- [x] **Critical Entities:** 7 entity categories and two-pass bipartite alignment verified against edge cases.
- [x] **Audio Quality Analysis:** WAV duration, sample rate, channels, RMS, peak amplitude, clipping %, and silence % verified.
- [x] **Clean vs Noisy Comparison:** Degradation deltas ($\Delta \text{WER}$, $\Delta \text{CER}$, critical retention) verified.
- [x] **Dataset Discovery:** Iterative double extension stripping (`.mp3.mp3` $\to$ `ML_NORMAL_01`) and sample inventory verified (5/5 samples valid).
- [x] **Aggregate Quotient Formulas:** Verified that $\text{Aggregate WER} = \frac{\sum \text{Errors}}{\sum \text{Ref Words}} \times 100$, rejecting arithmetic averages.

---

## 📝 5. Written Submission Form Checklist

When submitting on the Gnani AI application portal, prepare these responses:

- [ ] **Candidate Name:** Savio Sinto
- [ ] **Track / Role:** Indian AI / Voice Intelligence Internship Challenge 2026
- [ ] **Project Name:** NADHAM QA 2.0
- [ ] **Live App Link:** https://nadham-voice.streamlit.app/
- [ ] **GitHub Repository:** https://github.com/saviosinto123/NADHAM-QA
- [ ] **Video Demonstration Link:** *(Paste YouTube / Loom / Google Drive link)*
- [ ] **Social Post Link:** *(Paste LinkedIn or X post link)*
- [ ] **Architecture Document Link:** Link to [ARCHITECTURE.md](ARCHITECTURE.md) in repo
- [ ] **Project Report Link:** Link to [PROJECT_REPORT.md](PROJECT_REPORT.md) in repo
- [ ] **Honest Disclosure Included:** Transparently state upstream Cloudflare 504 status and genuine paired noise unavailability.

---

## ⏰ 6. Submission Deadline Reminder

> [!IMPORTANT]
> **Final Submission Deadline:** **November 15, 2026, at 6:00 PM IST.**  
> Complete your demo video recording and post the announcement before the deadline.
