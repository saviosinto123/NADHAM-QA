# ⚠️ NADHAM QA: Limitations & Verification Status

In adherence to strict engineering integrity and scientific reporting standards, this document details known limitations, the current upstream API status, and items requiring downstream verification.

---

## 1. Upstream Gnani Prisma API (HTTP 504 Gateway Timeout)

### 1.1 Observed Live Behavior
During live application testing using the local environment credentials (`GNANI_API_KEY`) and valid 16kHz PCM audio (`clean_sample.wav`), requests dispatched to the live endpoint:
```text
POST https://api.vachana.ai/stt/v3
```
returned:
```text
HTTP 504 Gateway Time-out
Cloudflare / Upstream Server Latency
```

### 1.2 Impact on Verification
- **What Was Verified:**
  - Header structure (`X-API-Key-ID: <KEY>`) and request dispatch are implemented correctly.
  - Multipart payload construction (`audio_file`, `language_code`, `format: "verbatim"`) is fully functional.
  - The client-side HTML error sanitizer successfully intercepted the Cloudflare HTML error and prevented UI breakage.
- **What Remains Unverified:**
  - **End-to-End Transcription Accuracy:** Live transcription accuracy on a real spoken voice sample cannot be verified until the upstream Gnani/Vachana gateway resolves its latency.
  - **No Live Claim Made:** We do not claim successful live transcription on this endpoint until a 200 OK response with real transcribed text is achieved.

---

## 2. Indic Speech Recognition Limitations

### 2.1 Spoken vs. Written Form Discrepancy (Numbers & Dates)
Standard Automatic Speech Recognition (ASR) engines frequently produce written digits (`2026`) or spelled-out words (`രണ്ടായിരത്തി ഇരുപത്തിയാറ്`) depending on formatting modes.
- Standard Levenshtein WER compares surface word tokens.
- If a human reference uses digits (`വർഷം 2026`) and the speech engine outputs words (`വർഷം രണ്ടായിരത്തി ഇരുപത്തിയാറ്`), standard WER penalizes this as a substitution + insertion error despite 100% semantic accuracy.
- **Resolution Path:** Future releases should incorporate an Inverse Text Normalization (ITN) module to map numbers and dates into comparable canonical forms prior to alignment.

### 2.2 Agglutination in Malayalam
Malayalam is an agglutinative language where suffixes, postpositions, and case markers attach directly to nouns and verbs (e.g., `കേരളത്തിൽ` vs `കേരളം` + `ഇൽ`).
- If an ASR model splits or joins compound phrases differently than the human transcriber, word-level WER records multiple errors.
- **Resolution Path:** Character Error Rate (CER) or subword-level evaluation should be presented alongside WER for agglutinative Indian languages.

---

## 3. Application Interface Limitations

### 3.1 Single Audio Processing
- The current interface evaluates one audio file at a time.
- Comparative evaluations (e.g. testing clean audio vs. background-noise audio side-by-side) currently require sequential runs rather than a dual-file comparison screen.

### 3.2 Unweighted Entity Error Rate
- In domain-specific applications (e.g. medical, banking, legal), a misrecognized proper name, phone number, or dosage is far more critical than a missed filler word.
- The current system applies equal unit weight ($cost = 1$) to all words.

---

## 4. Verification Checklist When API Restores

To complete final end-to-end verification once the Gnani Prisma service endpoint is reachable:
1. Ensure `GNANI_API_KEY` is present in `.env`.
2. Start the application: `streamlit run app.py`.
3. Upload a 10–20 second clean Malayalam voice recording.
4. Paste the ground-truth reference transcript.
5. Click **Run NADHAM QA Test** and verify:
   - Spinner displays *"Gnani Prisma is analysing your speech..."*.
   - Predicted transcript renders in the green column.
   - Word Error Rate and metrics update dynamically.
   - Word-level alignment table displays correct classifications.
   - TXT and CSV export files download with matching data.
