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
Displays three primary evaluation cards:
- **Word Error Rate (%):** Computed as $\frac{\text{Substitutions} + \text{Deletions} + \text{Insertions}}{\text{Reference Word Count}} \times 100\%$.
- **Total Word Errors:** Total count of non-correct edit operations.
- **Reference Word Count:** Total word tokens in the reference transcript.

### 4.2 Word-Level Error Analysis Table
An interactive table displaying token-by-token alignment:
| Status | Description | Reference Word | Recognized Word |
| :--- | :--- | :--- | :--- |
| **Correct** | Word recognized accurately | `നമസ്കാരം` | `നമസ്കാരം` |
| **Substitution** | Word misrecognized | `നല്ലൊരു` | `നല്ല` |
| **Deletion** | Word omitted by speech engine | `ദിവസം` | `—` |
| **Insertion** | Extra word hallucinated by engine | `—` | `ഇന്ന്` |

---

## 5. Input Safety & Defensive Guardrails

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
