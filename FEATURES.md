# 🌟 NADHAM QA: Feature Specification

This document provides a comprehensive overview of all features implemented in **NADHAM QA**.

---

## 1. Speech Recognition Lab & Audio Upload

### 1.1 Multi-Format Audio Support
- **Supported Formats:** `.wav`, `.mp3`, `.ogg`, `.flac`, `.aac`, `.m4a`.
- **Target Recording Duration:** Recommended for 10–30 second audio samples.
- **Upload File Size Limit:** Enforces a 25 MB ceiling to prevent server memory saturation.

### 1.2 Embedded Audio Playback
- **Feature:** Instant in-browser audio playback widget (`st.audio`).
- **Benefit:** Allows evaluators and QA testers to listen to the exact recording while inspecting word-level substitutions, deletions, and insertions.

---

## 2. Multi-Language Intelligence

### 2.1 Supported Languages & API Language Codes
| Language | UI Selector | Gnani API Language Code |
| :--- | :--- | :--- |
| **Malayalam** | `Malayalam` | `ml-IN` |
| **English** | `English` | `en-IN` |
| **Hindi** | `Hindi` | `hi-IN` |

> [!NOTE]
> For details on current upstream Gnani Prisma STT API behavior (HTTP 504 Gateway Timeout during live verification), see [LIMITATIONS.md](LIMITATIONS.md).

---

## 3. Indic & Malayalam Normalization Engine

The `words()` normalization pipeline provides dedicated support for Indic linguistic edge cases:

### 3.1 Malayalam Chillu Canonicalization
Translates legacy decomposed chillu sequences (consonant + virama `\u0D4D` + ZWJ `\u200D`) into modern atomic Unicode 5.1 chillu characters:
- ൺ (`U+0D7A`) — Chillu N
- ൻ (`U+0D7B`) — Chillu NN
- ർ (`U+0D7C`) — Chillu RR
- ൽ (`U+0D7D`) — Chillu L
- ൾ (`U+0D7E`) — Chillu LL
- ൿ (`U+0D7F`) — Chillu K

### 3.2 Invisible Control Character Handling
- **Zero-Width Space (`\u200B`):** Converted to standard ASCII space, ensuring words separated by ZWSP split correctly into individual tokens.
- **Non-Breaking Space (`\u00A0`):** Converted to standard space.
- **Isolated ZWJ (`\u200D`) & ZWNJ (`\u200C`):** Safely removed to eliminate invisible byte mismatches.

### 3.3 Domain-Critical Entity Preservation
- **Decimal Numbers:** Patterns like `3.14` or `10.50` retain their decimal period instead of being converted into `314` or `1050`.
- **Date Formats:** Formats like `15/08/1947` and `15-08-1947` retain internal delimiters instead of collapsing into `15081947`.
- **Currency Symbols:** Symbols (`₹`, `$`, `€`, `£`) belonging to Unicode category `Sc` are stripped while retaining numeric values (`₹500` → `500`).
- **Indian Numbering Commas:** Grouping commas in Indian notation (`1,00,000` → `100000`) are normalized.

---

## 4. Evaluation & Error Classification

### 4.1 Word Error Rate (WER) Metrics
Displays primary word-level evaluation cards:
- **Word Error Rate (%):** Computed as $\frac{\text{Substitutions} + \text{Deletions} + \text{Insertions}}{\text{Reference Word Count}} \times 100\%$.
- **Total Word Errors:** Total count of non-correct edit operations.
- **Reference Word Count:** Total word tokens in the reference transcript.

### 4.2 Character Error Rate (CER) Metrics
Computes fine-grained character edit distance using Unicode UAX #29 extended grapheme clusters (`\X` via Python `regex`):
- Base consonants with attached matras, viramas, and chillus are treated as single perceptual grapheme units.
- Whitespace is excluded from the edit distance matrix to avoid penalizing word-boundary segmentation variance in agglutinative Indic phrases.
- **CER Formula:** $\frac{\text{Char Substitutions} + \text{Char Deletions} + \text{Char Insertions}}{\text{Reference Grapheme Count}} \times 100\%$.

### 4.3 Word-Level Error Analysis Table
An interactive table displaying token-by-token alignment:
| Status | Description | Reference Word | Recognized Word |
| :--- | :--- | :--- | :--- |
| **Correct** | Word recognized accurately | `നമസ്കാരം` | `നമസ്കാരം` |
| **Substitution** | Word misrecognized | `നല്ലൊരു` | `നല്ല` |
| **Deletion** | Word omitted by speech engine | `ദിവസം` | `—` |
| **Insertion** | Extra word hallucinated by engine | `—` | `ഇന്ന്` |

---

## 5. Domain-Critical Information Detection (Rule-Based)

Rule-based extraction and two-pass bipartite entity matching across 7 mission-critical categories:
1. **Numbers:** Integers, decimals, and Indian notation (`1,00,000`).
2. **Currency & Amounts:** `₹`, `Rs`, `INR`, `$`, `€`, `£`, and Malayalam `രൂപ`. Prevents double-counting amounts as generic numbers.
3. **Dates:** `DD/MM/YYYY`, `DD-MM-YYYY`, and `YYYY-MM-DD`. Delimiters preserved.
4. **Times:** `10:30 AM`, `18:00`. Case-insensitive 12h/24h formats.
5. **Phone Numbers:** 10-digit Indian mobile sequences (`+91`, leading `0`, 6-9 prefix).
6. **Negation Patterns:** English negation keywords (`not`, `never`, `cannot`, etc.) and Malayalam verbal suffixes (`അല്ല`, `ഇല്ല`, `വേണ്ട`, `പാടില്ല`, `അരുത്`, `ശരിയല്ല`, `പോയില്ല`).
7. **Named Entities:** Known proper nouns from benchmark datasets.

Entities are matched via **Two-Pass Bipartite Alignment**:
- **Pass 1:** Exact value matches claim pairs first.
- **Pass 2:** Unmatched items of the same category are paired as `Changed`.
- **Passes 3 & 4:** Remaining unpaired reference entities are `Missing`; remaining hypothesis entities are `Extra`.

---

## 6. Local Audio Quality Analysis

Provides objective physical acoustic signal measurements for uncompressed PCM WAV recordings:
- **Audio Duration:** Exact recording length in seconds.
- **Sample Rate:** Sampling frequency in Hz (e.g. 16,000 Hz, 44,100 Hz).
- **Channels:** Mono, Stereo, or multi-channel count.
- **Peak Amplitude:** Highest absolute signal peak in dBFS.
- **RMS Energy Level:** Root-Mean-Square signal power in dBFS.
- **Clipping Percentage:** Percentage of samples reaching or exceeding digital saturation ($\ge 0.999$).
- **Silence Percentage:** Percentage of 20ms audio frames with RMS energy below $-40\text{ dBFS}$.

> [!NOTE]
> Compressed formats (`.mp3`, `.m4a`, `.ogg`, `.flac`, `.aac`) are passed directly to Gnani ASR without local decoding. Audio quality analysis clearly identifies unsupported formats without rejecting valid audio.

---

## 7. Clean vs. Noisy Speech Recognition Benchmark

A dedicated dual-recording comparison laboratory to evaluate ASR robustness against background noise:
- **Dual Audio Uploads:** Side-by-side uploads for Clean Audio and Noisy Audio with audio players.
- **Shared Reference:** Single ground-truth transcript evaluated against both transcriptions.
- **Credit & Quota Safety:** Explicit button click required; transparent notice that 2 API transactions are initiated.
- **Objective Comparison:**
  - Clean vs Noisy WER and CER.
  - $\Delta \text{WER}$ ($\text{Noisy WER} - \text{Clean WER}$) and $\Delta \text{CER}$.
  - Word error difference (substitutions, deletions, insertions).
  - Critical entity retention differences.
  - Acoustic signal property comparison (RMS energy, peak level, clipping, silence).
  - Data-driven outcome determination (Clean better, Noisy better, or Tie) without assuming noisy audio always degrades.
- **Diagnostic Exports:** Dedicated Comparison Report (`.txt`) and Comparison Metrics Table (`.csv`).

---

## 8. Input Safety & Defensive Guardrails

### 5.1 Empty Audio & 0-Byte Protection
- Blocks submissions with no audio uploaded (`Please upload an audio file.`).
- Checks `len(audio.getvalue()) == 0` and rejects empty files before making network calls.

### 5.2 Reference Text Quality Checks
- Blocks empty reference text (`Please enter the reference transcript.`).
- Checks `words(reference)` and alerts if the input contains only punctuation (`Reference transcript contains only punctuation or no valid words. Please enter meaningful text.`).

### 5.3 Stale Session Invalidation
- When a user starts a new test run, all previous session state keys (`transcript`, `reference`, `request_id`, `language`, `audio_name`) are purged.
- Ensures that failed runs or network timeouts never display old metrics beneath an error message.

### 5.4 HTML Error Sanitization
- Catches HTTP gateway errors (such as Cloudflare 502/504).
- Replaces raw HTML markup with a clean notification: *"Gnani API gateway error (HTTP 504). The upstream speech service is temporarily unavailable or timed out. Please retry shortly."*

---

## 6. Multi-Format Diagnostic Reports

### 6.1 Downloadable Plain Text Report (`.txt`)
Includes:
- Timestamp (YYYY-MM-DD HH:MM:SS)
- Source audio filename
- Recording language and Gnani Request ID
- Reference and predicted transcripts
- Summary metrics (WER, errors, word counts)
- Complete word-level operations table

### 6.2 Structured CSV Export (`.csv`)
- Exports all rows from the word-level error table (`Status`, `Reference Word`, `Recognized Word`).
- Ready for automated ingestion into QA dashboards, analytics spreadsheets, and CI/CD pipelines.

---

## 7. Audio Quality Analysis & Clean vs. Noisy Comparison (Step 4)

### 7.1 Local Acoustic Signal Analysis
- Evaluates PCM WAV recordings locally without external dependencies or cloud calls:
  - Duration, sample rate, and channel configuration (mono/stereo).
  - Peak amplitude and RMS energy (in dBFS).
  - Digital clipping percentage (samples hitting $\pm 1.0$).
  - Silence percentage across 20ms sliding windows ($< -40\text{ dBFS}$).
- Compressed audio formats (`.mp3`, `.m4a`, etc.) safely report `supported=False` to prevent misleading acoustic statistics.

### 7.2 Clean vs. Noisy Degradation Engine
- Evaluates paired clean and noisy audio against a shared reference transcript.
- Computes Degradation Deltas: $\Delta \text{WER}$, $\Delta \text{CER}$, and Critical Entity Retention rate.
- Deterministic outcome determination: `Clean better`, `Noisy better`, or `Tie`.
- Dedicated export formats: Dual-recording Comparison TXT report and Comparison CSV.

---

## 8. Reproducible Malayalam Benchmark & Reliability Evidence (Step 5)

### 8.1 Automated Benchmark Dataset Discovery
- **Genuine Inventory:** Discovers all verified Malayalam speech samples in `dataset/normal/` and matching ground-truth transcripts in `dataset/transcripts/`.
- **Iterative Suffix Stripping:** Canonical sample ID resolution (`extract_sample_id`) cleanly handles double extensions such as `ML_NORMAL_01.mp3.mp3` and `ML_NORMAL_01.mp3.txt`.
- **Integrity Validation:** Detects missing audio, missing transcripts, empty transcript files, and 0-byte corrupt audio prior to execution.
- **Acoustic Reality Disclosure:** Automatically checks for `dataset/noisy/` and transparently reports when paired clean/noisy audio is unavailable.

### 8.2 Standardized Aggregate Evaluation Methodology
- **Global Error Quotients:** Computes Aggregate WER and Aggregate CER strictly as total errors divided by total reference units:
  $$\text{Aggregate WER} = \frac{\sum_{\text{success}} \text{Word Errors}}{\sum_{\text{success}} \text{Reference Words}} \times 100$$
  $$\text{Aggregate CER} = \frac{\sum_{\text{success}} \text{Char Errors}}{\sum_{\text{success}} \text{Reference Graphemes}} \times 100$$
- **No Percentage Averaging:** Never computes the unweighted arithmetic mean of sample percentages, preventing short sentences from distorting overall platform accuracy.
- **Partial Failure Resilience:** Failed or skipped samples are isolated with explicit error messages and excluded from successful aggregate metric sums.
- **Aggregate Critical Information Retention:** Sums expected vs. matched entities across all evaluated samples to calculate overall entity preservation accuracy.

### 8.3 Benchmark Execution & Safety Controls
- **Interactive Multi-Sample Selection:** Allows evaluators to select specific subsets or execute the full 5-sample benchmark suite.
- **Planned Request Counter & Credit Notice:** Explicitly warns users of the exact number of API transactions to be consumed prior to execution.
- **Real-Time Progress Tracking:** Step-by-step progress bar and sample ID status updates.

### 8.4 Multi-Format Benchmark Evidence Export
- **Benchmark Summary TXT Report:** High-level executive summary, aggregate metrics, sample-level overview, detailed transcripts with error breakdown, and formal methodology/limitations disclosures.
- **Sample-Level Results CSV:** Complete per-sample metrics (WER, CER, word/char substitutions, deletions, insertions, latency, request IDs, transcripts).
- **Aggregate Metrics CSV:** Standardized machine-readable table with metric names, values, units, and descriptions.
