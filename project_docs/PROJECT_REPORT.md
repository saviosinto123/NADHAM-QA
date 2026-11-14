# 🎙️ NADHAM QA 2.0: Comprehensive Project Report
**Gnani AI Great Indian AI Internship Challenge 2026 Submission**  
**Project:** Indian Speech Recognition Evaluation Platform (Kerala-First)  
**Author:** Savio Sinto  
**Live Application:** https://nadham-voice.streamlit.app/  
**GitHub Repository:** https://github.com/saviosinto123/NADHAM-QA  
**Date:** November 14, 2026  

---

## 1. Title Page

```
========================================================================================
                                     NADHAM QA 2.0
                  Kerala-First Indian Voice Intelligence Testing Platform
========================================================================================

Challenge Track   : Gnani AI Great Indian AI Internship Challenge 2026
ASR Integration   : Gnani Prisma STT v2.5 (Vachana STT v3 API)
Target Language   : Malayalam (ml-IN), with English (en-IN) & Hindi (hi-IN) support
Methodology       : Dynamic Programming Levenshtein WER, Unicode Grapheme CER (UAX #29),
                    Two-Pass Critical Entity Alignment, Local Acoustic Signal Analysis,
                    and Standardized Global Aggregate Batch Benchmarking
Author            : Savio Sinto
Submission Date   : November 14, 2026
========================================================================================
```

---

## 2. Executive Summary

Automatic Speech Recognition (ASR) benchmarking in India suffers from a critical regional language blind spot. Standard Western speech evaluation toolkits (e.g., Kaldi, JiWER, Hugging Face evaluate) assume simple whitespace tokenization and ASCII or Latin character models. When applied directly to Indic scripts—and Malayalam in particular—they fail to account for unique orthographic structures such as chillu characters, zero-width format controls, complex ligatures, and agglutinative suffixes. Consequently, standard evaluation yields artificially inflated error rates that penalize models for orthographically valid transcriptions.

**NADHAM QA 2.0** is an enterprise-grade evaluation and reliability platform developed to address this challenge. Tailored specifically for **Gnani Prisma STT (v2.5)** via the Vachana STT v3 endpoint, NADHAM QA provides:
1. **Indic & Malayalam Text Normalization:** Standardizes atomic vs. legacy decomposed chillu letters, handles Zero-Width Joiners (ZWJ) and Spaces (ZWSP), and protects decimal numbers and dates.
2. **Dual-Granularity Error Evaluation:** Implements Wagner-Fischer Dynamic Programming for word-level Word Error Rate (WER) and character-level Character Error Rate (CER) over Unicode UAX #29 extended grapheme clusters.
3. **Critical Information Detection:** Identifies numbers, dates, times, currency, phone numbers, negations, and named entities using a two-pass bipartite alignment algorithm.
4. **Local Acoustic Signal Quality Analysis:** Evaluates PCM WAV recordings locally (RMS level, peak amplitude, digital clipping, silence percentage) to examine acoustic degradation.
5. **Clean vs. Noisy Comparison Lab:** Empirically quantifies speech recognition degradation between paired recordings against a shared reference transcript.
6. **Reproducible Malayalam Benchmark Platform:** Evaluates genuine Malayalam speech datasets, calculates exact aggregate error quotients ($\sum \text{errors} / \sum \text{units}$), and transparently discloses acoustic conditions.
7. **Comprehensive Evidence Reporting:** Generates audit-ready plain text (`.txt`) and tabular (`.csv`) reports for individual runs, comparative tests, and batch benchmarks.

The application achieves **100% test pass rate across 102 automated Pytest unit and integration tests** and has completed full headless verification via Streamlit `AppTest`.

---

## 3. Problem Statement

Evaluating Indic speech recognition models presents five foundational challenges:

1. **Chillu Ambiguity:** Modern Unicode represents Malayalam chillu letters atomically (`ൺ`, `ൻ`, `ർ`, `ൽ`, `ൾ`, `ൿ`), whereas legacy keyboards emit decomposed consonant + virama (`്`) + Zero-Width Joiner (ZWJ `\u200D`). Although visually identical, standard string comparisons treat them as completely different words, artificially inflating WER.
2. **Agglutination & Word-Level WER Limitations:** In Malayalam, postpositions, suffixes, and case markers bind directly to root nouns and verbs (e.g., `കേരളത്തിൽ` vs `കേരളം` + `ൽ`). Minor transcription variations at word boundaries result in 100% word error penalties despite high acoustic fidelity.
3. **Punctuation Stripping vs. Critical Data Loss:** Standard NLP tokenizers naively delete all punctuation marks, corrupting decimal numbers (`3.14` $\to$ `314`), dates (`15/08/1947` $\to$ `15081947`), and currency symbols (`₹500` $\to$ `500`).
4. **Failure to Isolate Domain-Critical Entities:** An ASR system that transcribes 9 out of 10 words correctly but alters a numerical quantity (e.g., ₹500 to ₹5,000) or misses a negation word (`അല്ല` / `ഇല്ല`) achieves a deceptively low 10% WER while failing catastrophically in production banking, legal, or medical contexts.
5. **Lack of Acoustic Signal Correlation:** QA evaluators often observe degraded ASR transcripts without knowing whether the failure stemmed from low acoustic energy, extreme digital clipping, or ambient silence.

---

## 4. Motivation

Kerala is leading digital adoption in banking, e-governance, and mobile citizen services. Voice intelligence powered by high-quality models such as Gnani Prisma STT represents the primary interface for millions of Malayalam speakers. However, without a dedicated, linguistically aware testing and reliability platform, voice AI deployment carries significant risk. Building NADHAM QA provides developers, QA teams, and evaluators with a scientific, transparent, and reproducible evaluation harness.

---

## 5. Objectives

1. **Linguistic Fidelity:** Implement normalization rules preserving Malayalam chillu characters, zero-width controls, numbers, dates, and currency.
2. **Dual Metric Implementation:** Provide exact Levenshtein Word Error Rate (WER) alongside Character Error Rate (CER) calculated over extended grapheme clusters.
3. **Domain-Critical Entity Auditing:** Build a deterministic rule-based extractor and two-pass bipartite matcher across 7 high-risk entity categories.
4. **Acoustic Quality Measurement:** Measure fundamental audio signal properties locally without external cloud dependencies.
5. **Noise Degradation Benchmarking:** Provide comparative analysis between clean and degraded audio against a shared ground truth.
6. **Reproducible Batch Benchmarking:** Ingest dataset recordings, calculate true aggregate error quotients, and produce exportable evidence reports.
7. **Production Guardrails & Security:** Protect API keys, reject 0-byte files, enforce 25 MB upload limits, and sanitize upstream gateway errors.

---

## 6. Proposed Solution

NADHAM QA 2.0 delivers an interactive, single-page analytical platform organized into three distinct tabs:

| Tab | Feature Area | Primary Capabilities |
|---|---|---|
| **Tab 1** | `🎙️ Single Evaluation` | Audio upload & playback, Ground-truth text input, WER & CER calculation, Detailed edit operations breakdown (S/D/I), Critical entity detection, Individual TXT/CSV reports. |
| **Tab 2** | `🔬 Clean vs. Noisy Comparison` | Paired clean & noisy audio evaluation, Local acoustic signal analysis (RMS, peak, clipping, silence), Speech degradation deltas ($\Delta \text{WER}$, $\Delta \text{CER}$, Critical retention), Comparative TXT/CSV reports. |
| **Tab 3** | `📊 Malayalam Benchmark & Reliability Evidence` | Automated dataset discovery & validation, Batch evaluation runner with progress tracking, Standardized global aggregate metric calculation, Transparent acoustic condition callout, 3 downloadable evidence reports. |

---

## 7. Technology Stack

- **Application & UI:** Python 3.10+ (Tested on Python 3.14.8), Streamlit (v1.67.0)
- **Speech Recognition Engine:** Gnani Prisma STT v2.5 via Vachana STT v3 REST endpoint
- **Text Normalization & NLP:** Unicode Character Database (`unicodedata`), Python Standard `re`, Unicode Regular Expressions (`regex` v2026.1.17 for UAX #29 `\X` grapheme cluster segmentation)
- **Acoustic Signal Processing:** Python standard `wave`, `numpy` (v2.5.4)
- **Data Handling & Exports:** Pandas, `io`, `csv`
- **Configuration & Security:** `python-dotenv`, Streamlit Secrets Management
- **Automated Testing:** Pytest (v9.2.0), Streamlit `AppTest`

---

## 8. System Architecture

The platform architecture follows a modular, pipeline-driven design:

```
[ Client Browser (Streamlit UI) ]
         │
         ├── Tab 1: Single Audio Evaluation Lab
         ├── Tab 2: Clean vs. Noisy Comparison Lab
         └── Tab 3: Malayalam Benchmark & Reliability Platform
         │
[ Safety & Validation Guard ]
         │ (0-Byte Check, 25MB File Cap, Punctuation-Only Text Check)
         ▼
[ Secure API Client (call_gnani) ] ──► POST /stt/v3 ──► [ Gnani Prisma STT v2.5 ]
         │                                              (api.vachana.ai)
         ▼ (JSON Response / Cloudflare HTML Sanitizer)
[ Text Normalization Pipeline (words()) ]
         ├── Canonical Chillu Mapping (Legacy ZWJ → Atomic)
         ├── Zero-Width Joiner/Space Standardization
         ├── Boundary Punctuation Filtering (Decimals & Dates Preserved)
         └── Currency & Indian Comma Normalization
         │
         ├──► [ Wagner-Fischer Word DP Engine ] ──► WER & Edit Operations (S, D, I)
         │
         ├──► [ Unicode Grapheme Engine (regex \X) ] ──► CER & Char Operations
         │
         ├──► [ Critical Entity Engine (7 Categories) ] ──► Two-Pass Alignment
         │
         ├──► [ Local Acoustic Analyzer (wave & numpy) ] ──► RMS, Peak, Clipping, Silence
         │
         └──► [ Benchmark Aggregator ] ──► Global Aggregate Error Quotients
```

---

## 9. Implementation Details

### 9.1 Secure Gnani Prisma Integration
- Endpoint: `https://api.vachana.ai/stt/v3`
- Method: `POST` multipart/form-data
- Headers: `X-API-Key-ID: <GNANI_API_KEY>`
- Language mapping: Malayalam (`ml-IN`), English (`en-IN`), Hindi (`hi-IN`)
- Formatting: `format="verbatim"`

### 9.2 Text Normalization Engine (`words()`)
Text normalization is implemented in `words()`:
1. Replaces legacy chillu combinations (`ൺ`, `ൻ`, `ർ`, `ൽ`, `ൾ`, `ൿ` via virama + ZWJ) with canonical atomic code points.
2. Replaces Zero-Width Spaces (`\u200B`) and Non-Breaking Spaces (`\u00A0`) with ASCII spaces.
3. Strips isolated format controls (`\u200C`, `\u200D`).
4. Normalizes currency symbols (`₹`, `$`, `€`, `£`, `Rs`, `INR`).
5. Strips internal commas in Indian numbers (`1,00,000` $\to$ `100000`) while preserving decimal dots (`3.14`).
6. Strips sentence-boundary punctuation while keeping internal hyphens.

---

## 10. WER and CER Methodology

### 10.1 Word Error Rate (WER)
Calculated using the Wagner-Fischer dynamic programming algorithm over normalized word lists:
$$\text{WER} = \frac{S + D + I}{N_{\text{ref}}} \times 100\%$$
- Matrix size: $(N_{\text{ref}} + 1) \times (N_{\text{hyp}} + 1)$
- Operations are backtraced to label each token as **Correct**, **Substitution**, **Deletion**, or **Insertion**.
- Exact mathematical property: $S + D + I = \text{Total Errors}$.

### 10.2 Character Error Rate (CER)
In Malayalam, characters are grapheme clusters rather than standalone code points. For example, `കി` consists of `ക` (U+0D15) and `ി` (U+0D3F).
- **Segmentation:** Uses Unicode UAX #29 extended grapheme clusters via Python `regex` pattern `\X`.
- **Policy:** Whitespace and punctuation characters are excluded from the character list so that spacing differences do not artificially depress or inflate the error rate.
- **Formula:**
  $$\text{CER} = \frac{S_{\text{char}} + D_{\text{char}} + I_{\text{char}}}{N_{\text{graphemes}}} \times 100\%$$

---

## 11. Critical Information Detection

To verify whether numbers, dates, and high-impact terms are transcribed accurately, the platform implements a rule-based engine across 7 categories:
1. **Numbers:** Decimal numbers, integers, and Indian grouped numbers.
2. **Dates:** Standard slash/hyphen dates (`DD/MM/YYYY`, `DD-MM-YYYY`).
3. **Times:** 12-hour and 24-hour time expressions (`10:30 AM`, `18:00`).
4. **Currency:** Symbols and currency codes with amounts (`₹500`, `Rs 1000`).
5. **Phone Numbers:** 10-digit Indian mobile numbers and standard sequences.
6. **Negations:** Explicit Malayalam negation words (`അല്ല`, `ഇല്ല`, `പാടില്ല`, `വേണ്ട`, `അരുത്`) and English negations (`not`, `no`, `never`, `cannot`).
7. **Known Named Entities:** Major Kerala district centers (`തിരുവനന്തപുരം`, `കൊച്ചി`, `തൃശ്ശൂർ`, `കോഴിക്കോട്`) and person names.

### Two-Pass Bipartite Alignment
- **Pass 1:** Exact identity match (same entity category and normalized text).
- **Pass 2:** Category match with changed value (e.g., reference `500` vs recognized `5000` $\to$ `Changed`).
- Unpaired reference items are recorded as `Missing`; unpaired hypothesis items as `Extra`.
- Match rate: $\frac{\text{Matched Items}}{\text{Expected Items}} \times 100\%$.

---

## 12. Audio Quality Analysis

The platform implements local acoustic signal processing for PCM WAV audio without external command-line tools:
- **Duration & Channel Count:** Extracted directly from WAV RIFF headers.
- **RMS Energy Level:** Calculated across all PCM samples and expressed in dBFS:
  $$\text{RMS}_{\text{dBFS}} = 20 \log_{10}\left(\sqrt{\frac{1}{N}\sum x[i]^2} + 10^{-9}\right)$$
- **Peak Amplitude:** Absolute maximum sample value expressed in dBFS.
- **Digital Clipping Percentage:** Proportion of samples exceeding $\pm 0.999$ full scale.
- **Silence Percentage:** 20ms sliding windows evaluated against a $-40\text{ dBFS}$ threshold.
- Non-WAV formats (MP3, M4A) cleanly report `supported=False` rather than inventing synthetic metrics.

---

## 13. Benchmark Methodology

### 13.1 Automated Dataset Discovery
Discovers paired audio files in `dataset/normal/` and transcripts in `dataset/transcripts/`.
`extract_sample_id()` iteratively strips double extensions (such as `.mp3.mp3` and `.mp3.txt`), mapping both cleanly to `ML_NORMAL_01`.

### 13.2 Exact Aggregate Metric Calculation
To adhere to scientific benchmark standards, aggregate metrics are computed as exact global error quotients:
$$\text{Aggregate WER} = \frac{\sum_{i=1}^{K} \text{Word Errors}_i}{\sum_{i=1}^{K} \text{Reference Words}_i} \times 100$$
$$\text{Aggregate CER} = \frac{\sum_{i=1}^{K} \text{Char Errors}_i}{\sum_{i=1}^{K} \text{Reference Graphemes}_i} \times 100$$
- **Rejection of Arithmetic Mean:** The arithmetic mean of sample percentages is strictly rejected because it falsely weights short and long utterances equally.
- **Fault Isolation:** Failed API requests are marked with status `Failed`, recorded with their error message, and excluded from successful aggregate calculations.

---

## 14. Results and Evaluation Evidence

### 14.1 Verified Dataset Inventory
The repository contains exactly five genuine Malayalam speech recordings:

| Sample ID | Audio Filename | Reference Transcript | Verified Words | Evaluated Graphemes | Raw Unicode Code Points |
|---|---|---|:---:|:---:|:---:|
| `ML_NORMAL_01` | `ML_NORMAL_01.mp3.mp3` | `ML_NORMAL_01.mp3.txt` | 8 | 29 | 59 |
| `ML_NORMAL_02` | `ML_NORMAL_02.mp3.mp3` | `ML_NORMAL_02.mp3.txt` | 10 | 38 | 80 |
| `ML_NORMAL_03` | `ML_NORMAL_03.mp3.mp3` | `ML_NORMAL_03.mp3.txt` | 9 | 32 | 67 |
| `ML_NORMAL_04` | `ML_NORMAL_04.mp3.mp3` | `ML_NORMAL_04.mp3.txt` | 10 | 32 | 65 |
| `ML_NORMAL_05` | `ML_NORMAL_05.mp3.mp3` | `ML_NORMAL_05.mp3.txt` | 8 | 50 | 93 |
| **Total** | **5 Audio Recordings** | **5 Ground-Truth Files** | **45 Words** | **181 Graphemes** | **364 Code Points** |

### 14.2 Clarification of Reference Word & Grapheme Discrepancies
An initial preliminary inspection noted "47 words and 326 graphemes". Rigorous programmatic verification clarifies this difference:
1. **Reference Words:** Both raw whitespace splitting (`text.split()`) and normalized tokenization (`words(text)`) across all 5 ground-truth files produce exactly **45 words** ($8 + 10 + 9 + 10 + 8 = 45$). The earlier figure of 47 was an unverified manual estimate.
2. **Grapheme Clusters vs. Code Points:**
   - Raw Unicode scalar values (code points, `len(text)`): **364 code points** total (or 326 when excluding spaces and terminal periods). In Indic scripts, combining characters (consonant + virama + matra) occupy multiple Unicode code points.
   - Raw grapheme clusters (`\X` including spaces/punctuation): **228 graphemes**.
   - **Evaluated CER Graphemes (`characters()`):** **181 grapheme clusters**. In accordance with standard ASR CER methodology, spaces and punctuation are excluded from CER calculation so that spacing discrepancies do not artificially dilute error rates.
   - All reports, test suites, and dashboard metrics use the verified value: **181 reference graphemes**.

### 14.3 Genuine Clean/Noisy Paired Audio Reality
The repository contains recordings captured under normal/clean conditions. **Genuine paired clean-versus-noisy recordings do not exist in the current dataset** (`dataset/noisy/` is absent). NADHAM QA explicitly discloses this reality on the benchmark dashboard and within all generated reports rather than fabricating artificial noise.

---

## 15. Testing and Validation

### 15.1 Automated Pytest Suite: 102 / 102 Tests Passing (100% Pass Rate)

| Test Module / Class | Tests | Status | Scope |
|---|:---:|:---:|---|
| `TestNormalization` | 10 | **PASSED** | Atomic vs legacy chillu, ZWJ/ZWSP, decimals, dates, currencies |
| `TestWERCAlculation` | 10 | **PASSED** | Exact match, substitutions, deletions, insertions, invariants |
| `TestCERCalculation` | 12 | **PASSED** | Grapheme cluster segmentation, combining signs, whitespace exclusion |
| `TestCriticalInformation` | 21 | **PASSED** | 7 entity classes, two-pass alignment, changed vs missing vs extra |
| `TestGnaniAPI` | 10 | **PASSED** | Dual-source keys, zero-byte rejection, 25MB cap, HTML error sanitization |
| `TestReportGeneration` | 2 | **PASSED** | Single-run TXT report and CSV export schema |
| `TestAudioQualityAnalysis` | 8 | **PASSED** | WAV header parsing, RMS, peak amplitude, clipping, silence percentage |
| `TestCleanNoisyComparison` | 11 | **PASSED** | Degradation deltas, outcome determination, comparative reporting |
| `TestBenchmarkDatasetDiscovery` | 7 | **PASSED** | Sample ID extraction, repository discovery, missing/empty file guards |
| `TestBenchmarkBatchEvaluation` | 6 | **PASSED** | Global aggregate error quotients, partial failure isolation, callbacks |
| `TestBenchmarkReporting` | 4 | **PASSED** | Benchmark summary TXT, sample CSV, aggregate CSV, zero-leak check |
| **Total Test Suite** | **101** | **PASSED** | **Execution Time: ~5.04 seconds** |
| `scratch/test_apptest_verification.py` | 1 | **PASSED** | Full Headless Streamlit AppTest across all 3 UI Tabs |

---

## 16. Security Considerations

1. **Dual-Source Secret Management:** The application accesses API keys via `os.getenv("GNANI_API_KEY")` with fallback to `st.secrets["GNANI_API_KEY"]`. Keys are never committed to version control, logged, or included in generated reports.
2. **Pre-Dispatch Quota Protection:** Rejects 0-byte audio uploads locally, preventing unnecessary consumption of API credits.
3. **Denial-of-Service Defense:** Rejects uploads exceeding 25 MB to protect server memory.
4. **HTML Error Sanitization:** Traps Cloudflare 502/504 gateway timeout markup and extracts clean text, preventing UI layout disruption.
5. **Session Isolation:** Previous evaluation keys are cleared upon starting a new test run, eliminating stale metrics.

---

## 17. Limitations

1. **Live Transcription Testing & Statistical Scope:**
   - During live API testing with Gnani Prisma STT (`https://api.vachana.ai/stt/v3`), an earlier API request encountered an upstream Cloudflare `HTTP 504 Gateway Time-out` due to temporary server latency.
   - In a subsequent live evaluation, one live Malayalam speech recording was successfully transcribed with **8/8 words correct and 0% WER** against ground truth.
   - However, in adherence to scientific reporting standards, **one successful sample does not establish general Malayalam transcription accuracy** across diverse speakers, regional accents, or extensive vocabularies.
2. **Benchmark Dataset Scope & Acoustic Reality:**
   - The reproducible benchmark platform contains **five normal Malayalam speech recordings** (`dataset/normal/`) with verified ground truth (45 reference words, 181 grapheme clusters).
   - The benchmark **does not contain genuine noisy recording pairs**. NADHAM QA transparently discloses this condition across the UI and in all reports rather than synthesizing artificial noise or claiming unverified noise robustness.
3. **Small Benchmark Sample Size:** While five samples validate the reproducible mechanics of automated discovery, alignment, quotient calculation, and reporting, a five-sample dataset is insufficient to establish broad statistical benchmarks across all dialects of Kerala.
4. **Local Acoustic Analysis Format Scope:** Local acoustic signal measurement is implemented for PCM WAV files. Compressed formats (MP3, M4A) pass directly to Gnani ASR while reporting `supported=False` for local acoustic metrics.
5. **Rule-Based Entity Scope:** Critical entity detection relies on deterministic pattern matching and regional dictionaries; complex semantic paraphrases require human review.

---

## 18. Future Improvements

1. **Inverse Text Normalization (ITN):** Implement a dedicated Indic ITN module to map spelled-out spoken numbers (`രണ്ടായിരത്തി ഇരുപത്തിയാറ്`) to written digits (`2026`) prior to alignment.
2. **Dialectal Malayalam Expansion:** Expand benchmark recordings across North Malabar, Central Kerala, and Travancore regional dialects.
3. **Synthetic Acoustic Degradation Pipeline:** Add calibrated, simulated acoustic noise profiles (babble, street, reverberation) with precise SNR control.
4. **Multi-Speaker Diarization Evaluation:** Benchmark speaker separation and speaker turn attribution.
5. **Pan-Indic Expansion:** Extend rule-based entity detection and normalization to Tamil, Telugu, Kannada, Bengali, and Marathi.

---

## 19. Conclusion

NADHAM QA 2.0 demonstrates that evaluating speech recognition models for Indian languages requires linguistic depth, orthographic precision, and defensive software engineering. By combining Wagner-Fischer Word Error Rate with Unicode UAX #29 Character Error Rate, two-pass critical entity auditing, local acoustic signal processing, and a reproducible batch benchmark harness, NADHAM QA transforms speech AI testing from simple text comparison into an audit-ready reliability platform.

---

## 20. Project Links

- **Live Streamlit Application:** https://nadham-voice.streamlit.app/
- **GitHub Source Code Repository:** https://github.com/saviosinto123/NADHAM-QA
- **Comprehensive Architecture Document:** [project_docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Feature Specification:** [project_docs/FEATURES.md](FEATURES.md)
- **Testing & Verification Report:** [project_docs/TESTING_REPORT.md](TESTING_REPORT.md)
- **Limitations & Verification Status:** [project_docs/LIMITATIONS.md](LIMITATIONS.md)
- **Demonstration Script:** [project_docs/DEMO_SCRIPT.md](DEMO_SCRIPT.md)
- **Interview Preparation Guide:** [project_docs/INTERVIEW_PREPARATION.md](INTERVIEW_PREPARATION.md)
- **Submission Checklist:** [project_docs/SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)
