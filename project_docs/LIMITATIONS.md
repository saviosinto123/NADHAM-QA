# ⚠️ NADHAM QA: Limitations & Verification Status

In adherence to strict engineering integrity and scientific reporting standards, this document details known limitations, the current upstream API status, and items requiring downstream verification.

---

## 1. Upstream Gnani Prisma API Testing & Verification Status

### 1.1 Observed Live API Behavior
During testing of the live Gnani Prisma endpoint (`https://api.vachana.ai/stt/v3`):
- **Earlier HTTP 504 Timeout:** An earlier API request encountered an upstream Cloudflare `HTTP 504 Gateway Time-out` due to temporary server latency. The client-side HTML error sanitizer successfully intercepted the response, shielding the user interface from raw HTML error pages.
- **Successful Live Test:** In a subsequent live evaluation, one live Malayalam speech recording was successfully transcribed by Gnani Prisma STT with **8/8 words correct (0% WER)** against ground truth.

### 1.2 Evaluation Scope & Statistical Limits
- **Single-Sample Scope:** While the successful live test confirms that endpoint connectivity, authentication (`X-API-Key-ID`), audio payload streaming, and transcription work end-to-end, **one successful sample does not establish general Malayalam transcription accuracy across diverse speakers, accents, or vocabularies**.
- **Benchmark Scope:** The reproducible benchmark platform contains **five normal Malayalam speech recordings** (`dataset/normal/`) with verified ground-truth transcripts.
- **Absence of Paired Noisy Samples:** The benchmark dataset **does not contain genuine noisy recording pairs**. NADHAM QA transparently discloses this absence on the benchmark dashboard and in generated evidence reports rather than synthesizing artificial noise or claiming unverified noise robustness.

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

## 3. Application Interface & Audio Analysis Limitations

### 3.1 Local Acoustic Analysis Format Scope
- **PCM WAV Only:** Local acoustic signal measurement (duration, sample rate, channels, RMS energy, peak amplitude, clipping percentage, and silence percentage) relies on Python standard library `wave` and `numpy`.
- **Compressed Audio Passthrough:** Compressed formats (`.mp3`, `.m4a`, `.ogg`, `.flac`, `.aac`) are accepted for Gnani ASR without local decoding, but acoustic metric computation reports `supported=False` rather than inventing synthetic numbers.
- **Noise Robustness Scope:** Clean vs. Noisy comparisons are empirical benchmarks of the uploaded paired files. They do not constitute an abstract theoretical claim of noise immunity across all acoustic environments.

### 3.2 Dual-File Benchmark Scope
- Dual-file comparison supports 1 Clean audio file and 1 Noisy audio file against a shared reference transcript.
- Multi-speaker diarization and full batch multi-file sweeps are planned for subsequent milestones.

### 3.3 Rule-Based Entity Extraction Scope
- Domain-critical entity detection uses deterministic pattern matching. Complex semantic paraphrases or rare regional names outside the benchmark dictionary require human verification.

### 3.4 Benchmark Dataset Inventory & Genuine Paired Noise Status
- **Verified Dataset Scope:** The repository contains exactly 5 genuine Malayalam speech recordings in `dataset/normal/` (`ML_NORMAL_01.mp3.mp3` through `ML_NORMAL_05.mp3.mp3`) with verified reference transcripts in `dataset/transcripts/`.
- **Paired Noise Reality:** Genuine paired clean-versus-noisy audio files are unavailable in the current benchmark dataset (`dataset/noisy/` is absent).
- **Engineering Integrity Policy:** NADHAM QA refuses to fabricate simulated background noise, inject synthetic noise artifacts, or generate unverified comparative statistics. The platform transparently discloses this condition on the benchmark dashboard and within all generated evidence reports.

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
