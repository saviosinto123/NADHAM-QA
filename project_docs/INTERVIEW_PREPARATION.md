# 🎓 NADHAM QA 2.0: Technical Interview & Evaluator Q&A Guide

This guide prepares the developer for technical interviews, evaluator questions, and live defense of **NADHAM QA 2.0** for the **Gnani AI Great Indian AI Internship Challenge 2026**.

---

## ⚡ Elevator Pitches

### ⏱️ The 30-Second Introduction
> *"NADHAM QA is a Kerala-first Indian voice intelligence testing and reliability platform built for Gnani Prisma STT v2.5. Standard speech recognition evaluation tools fail on Indic languages because they treat visually identical chillu letters, zero-width joiners, and agglutinative suffixes as errors. NADHAM QA solves this with Indic-aware Unicode normalization, dual Word and Character Error Rate evaluation over grapheme clusters, two-pass critical entity auditing, and a reproducible batch benchmark platform backed by 102 automated tests."*

---

### ⏱️ The 1-Minute Project Overview
> *"Evaluating Automatic Speech Recognition (ASR) in Indian languages requires more than just translating Western evaluation tools. In Malayalam, unique orthographic structures like atomic versus decomposed chillu letters falsely inflate Word Error Rates even when the spoken audio was transcribed accurately.*
>
> *NADHAM QA addresses this with four core systems:*
> *First, an Indic Text Normalizer that canonicalizes chillus, resolves zero-width controls, and protects numbers and dates.*
> *Second, a dual evaluation engine computing both Levenshtein WER and Unicode UAX #29 extended grapheme CER, excluding whitespace to ensure fair character accuracy.*
> *Third, a Critical Information Detection engine that audits numbers, currency, dates, negations, and names.*
> *And fourth, a Reproducible Malayalam Benchmark that evaluates genuine speech recordings, computes exact global error quotients, and exports audit-ready evidence reports.*
>
> *The entire codebase is verified with 102 passing tests and zero credential leakage."*

---

### ⏱️ The 2-Minute Deep Technical Explanation
> *"Under the hood, NADHAM QA is designed around linguistic precision, dynamic programming, and defensive software engineering.*
>
> *When an evaluator uploads Malayalam audio, our client authenticates with Gnani Prisma STT via the Vachana v3 API. The client enforces a 25 MB file limit, rejects 0-byte audio locally to conserve API quota, and sanitizes upstream Cloudflare 502/504 gateway timeouts.*
>
> *Once transcribed, both the reference and hypothesis pass through our normalization pipeline. In Malayalam, chillu letters were historically encoded as a consonant plus virama plus Zero-Width Joiner. Modern Unicode assigns them atomic scalar values. Visually they are identical, but naive string equality marks them as 100% substitution errors. Our normalizer maps legacy sequences to canonical atomic code points, replaces Zero-Width Spaces with standard whitespace, and strips internal grouping commas from Indian numbers like 1,00,000 while preserving decimal points and dates.*
>
> *For evaluation, we implement the Wagner-Fischer algorithm at both word and character levels. Word-level WER alone is inadequate for Malayalam because of agglutination—suffixes attach directly to root words. Therefore, we implement Character Error Rate using Unicode UAX #29 extended grapheme clusters via Python regex with `\X`. This ensures combining vowel signs and viramas remain bound to their base consonants as single perceptual units.*
>
> *Beyond acoustic overlap, we audit semantic reliability: our two-pass alignment engine checks seven domain-critical entity classes—numbers, dates, times, currency amounts, phone numbers, negations, and regional named entities. Pass 1 matches exact entities; Pass 2 identifies changed values, alerting evaluators if ₹500 was transcribed as ₹5,000.*
>
> *Finally, our benchmark module discovers genuine audio and ground-truth pairs, resolves double file extensions, and calculates exact global error quotients rather than arithmetic averages of percentages. The platform is open-source, fully tested with 102 unit tests, and ready for enterprise evaluation."*

---

## 🔬 Core Conceptual Deep-Dives

### 1. WER vs. CER: Why Both Are Essential for Indic Languages
- **Word Error Rate (WER):** Measures complete word token replacements:
  $$\text{WER} = \frac{S + D + I}{N_{\text{ref}}} \times 100\%$$
  In English, words are separated by spaces and morphological inflection is light. In Malayalam, words are heavily **agglutinative**: case markers, postpositions, and conjunctions attach to root words (e.g., `കേരളത്തിൽ` = `കേരളം` + `ൽ`). If an ASR engine transcribes `കേരളത്തിൽ` as `കേരളത്തിൽത്തന്നെ`, a word-level metric records an entire word substitution or deletion error, even though 85% of the phonetic information was captured accurately.
- **Character Error Rate (CER):** Measures fine-grained phonetic and character preservation:
  $$\text{CER} = \frac{S_{\text{char}} + D_{\text{char}} + I_{\text{char}}}{N_{\text{graphemes}}} \times 100\%$$
- **The Spacing Policy:** In NADHAM QA, whitespace and punctuation are excluded from the CER character list. Including spaces artificially inflates or deflates CER based merely on token spacing conventions. Evaluating over non-whitespace grapheme clusters provides the true acoustic-phonetic fidelity of the ASR engine.

---

### 2. Unicode Normalization & Extended Grapheme Clusters
- **Code Points vs. Grapheme Clusters:** In Unicode, a code point is a single scalar value (e.g., `U+0D15` for `ക`). But in Indian scripts, a written character often consists of a base consonant followed by virama (`്`), vowel signs/matras (e.g., `ി`), or modifier marks.
- For example, the Malayalam syllable `കി` consists of two Unicode code points:
  - `U+0D15` (`ക` - Letter Ka)
  - `U+0D3F` (`ി` - Vowel Sign I)
- If an algorithm evaluates CER by simply doing `list(text)`, it splits `കി` into two disconnected tokens. If the model predicted `കു` (`ക` + `ു`), naive code point matching would claim that `ക` was correct and only `ി` was substituted. In reality, the entire syllable was altered.
- **Solution:** NADHAM QA uses Unicode Standard Annex #29 (UAX #29) Extended Grapheme Cluster segmentation (`\X` via `regex`). This groups `[Consonant + Matra / Virama]` into an indivisible unit.

---

### 3. Critical Information Detection & Two-Pass Alignment
- **The Business Reality:** A speech model can achieve a 95% word accuracy rate but still fail catastrophically in banking if it changes an account number, drops a currency digit (`500` $\to$ `5000`), or drops a negation word (`അല്ല` / `no`).
- **Why Two Passes?**
  - **Pass 1 (Greedy Exact Match):** If the reference has `₹500` and the recognition has `₹500`, Pass 1 pairs them immediately.
  - **Pass 2 (Type-Consistent Changed Pairing):** If the reference has `₹500` and the hypothesis has `₹5,000`, both are `CURRENCY` entities located in corresponding positions. Pass 2 pairs them and flags `₹500` $\to$ `₹5,000` as a **Changed Item**.
  - Without a two-pass approach, the engine would record `₹500` as `Missing` and `₹5,000` as `Extra`, obscuring the fact that a number was altered.

---

### 4. Why Five Benchmark Samples Are Insufficient for General Accuracy Claims
- **Statistical Significance:** Five speech recordings (totaling 45 reference words and 181 grapheme clusters) represent a targeted verification dataset, not an exhaustive linguistic corpus.
- **Acoustic & Dialectal Diversity:** Malayalam has distinct regional dialects (Travancore, Central Kerala, North Malabar/Kasaragod) and sociolinguistic variations. Five recordings cannot represent all demographic age groups, accents, or background acoustic environments.
- **Engineering Integrity:** In NADHAM QA, the benchmark exists to validate the **mechanics of reproducible evaluation** (automated discovery, error tracking, quotient calculation, reporting). We explicitly refrain from claiming general model accuracy based on five samples.

---

### 5. Indic Expansion Strategy
- **Text Normalization:** Apply similar chillu and virama canonicalization to Bengali (has similar hasant/hosonto controls) and Devanagari (half-forms and nuktas).
- **Grapheme Clusters:** The `regex` `\X` engine already works across all Unicode Indic blocks (Tamil, Telugu, Kannada, Gujarati, Bengali, Devanagari).
- **Critical Entities:** Replace the Malayalam negation list (`അല്ല`, `ഇല്ല`) and district dictionary with language-specific lookup tables for Tamil (`இல்லை`), Hindi (`नहीं`, `मत`), etc.

---

## ❓ 15 Likely Technical Interview Questions & Answers

### Q1: What algorithm did you use to calculate WER and CER?
> *"We implemented the Wagner-Fischer dynamic programming algorithm to compute the Levenshtein edit distance matrix. For WER, the matrix dimensions are $(N_{\text{words}} + 1) \times (M_{\text{words}} + 1)$. For CER, the dimensions are $(N_{\text{graphemes}} + 1) \times (M_{\text{graphemes}} + 1)$. We then backtrace from the bottom-right corner to $(0,0)$ to reconstruct the exact sequence of substitutions, deletions, insertions, and correct alignments."*

### Q2: What is the time and space complexity of your evaluation algorithm?
> *"For a reference of length $N$ and hypothesis of length $M$, the time complexity is $O(N \times M)$ because every cell in the DP table is computed once in constant time. The space complexity is $O(N \times M)$ to store the dynamic programming matrix for backtracing operation paths. For sentence-level evaluation where $N, M < 100$, this executes in under a millisecond in pure Python."*

### Q3: Why didn't you just use `len(text)` for character count in CER?
> *"Because in Malayalam, `len(text)` counts UTF-8 code points, not characters. A consonant with a vowel sign like `കി` consists of two code points (`U+0D15` and `U+0D3F`), but is a single perceptual grapheme cluster. Furthermore, `len(text)` counts spaces and punctuation, which distorts character accuracy. We use Unicode UAX #29 `\X` clusters and exclude whitespace to get true phonetic character counts."*

### Q4: How did you calculate Aggregate WER and CER across multiple files?
> *"In accordance with international speech recognition standards, we compute Aggregate WER and CER as global error quotients:
> $$\text{Aggregate WER} = \frac{\sum \text{Word Errors}}{\sum \text{Reference Words}} \times 100$$
> We strictly avoid taking the arithmetic average of sample WER percentages because doing so gives equal weight to a 2-word sentence and a 20-word sentence, producing statistically invalid numbers."*

### Q5: How do you handle failed API calls during batch evaluation?
> *"Failed calls are isolated and marked with `status='Failed'` along with their error message. Crucially, they are excluded from the successful aggregate word and grapheme denominators so that a network timeout does not contaminate the accuracy statistics of successful runs. The failure rate is tracked separately in the Benchmark Success Rate metric."*

### Q6: How does your audio quality analyzer work without ffmpeg or librosa?
> *"We use Python's standard `wave` library to read raw 16-bit PCM WAV headers and frames, convert the byte stream into a `numpy` array, normalize it to the range $[-1.0, 1.0]$, and compute root-mean-square energy (RMS dBFS), peak amplitude, digital clipping percentage ($|x| \ge 0.999$), and silence percentage across 20ms sliding windows using a $-40\text{ dBFS}$ threshold."*

### Q7: Why did you report `supported=False` for MP3 audio quality analysis?
> *"MP3 is a lossy compressed format. Decoding MP3 into raw PCM samples in pure Python without C-libraries like ffmpeg is unreliable. Rather than fabricating synthetic or approximate acoustic numbers, our system honestly reports `supported=False` for compressed files while still passing them cleanly to Gnani Prisma STT for speech recognition."*

### Q8: What security guardrails are implemented for the API key?
> *"We implement dual-source resolution: `os.getenv('GNANI_API_KEY')` with fallback to `st.secrets['GNANI_API_KEY']`. The key is never logged, never printed to the terminal, never rendered in the UI, and never included in downloadable TXT reports or CSV exports."*

### Q9: How do you prevent wasted API credits on bad uploads?
> *"We implement pre-flight client-side validation: if a user uploads a 0-byte file, or an audio file exceeding 25 MB, or submits reference text consisting solely of punctuation or whitespace, the request is intercepted locally with a clear warning and no network call is dispatched."*

### Q10: How do you handle upstream gateway timeouts like Cloudflare 504?
> *"When Cloudflare or an upstream proxy times out, it returns an HTTP 504 error formatted as an HTML page. Standard JSON parsers crash with a JSONDecodeError, dumping raw HTML markup into the UI. Our client inspects response status codes, strips HTML tags using regex, and presents a clean, human-readable service unavailable notification."*

### Q11: Why does `extract_sample_id()` strip extensions iteratively?
> *"In our dataset, audio files are named `ML_NORMAL_01.mp3.mp3` due to double extension naming, while transcripts are named `ML_NORMAL_01.mp3.txt`. A single `os.path.splitext()` would yield `ML_NORMAL_01.mp3`, which still has an extension. Our helper runs in a loop until all known media and text extensions (`.mp3`, `.wav`, `.txt`, `.ogg`, `.flac`, `.m4a`) are removed, cleanly resolving both to `ML_NORMAL_01`."*

### Q12: Why did the initial inspection report 47 words and 326 graphemes?
> *"47 words was a preliminary unnormalized estimate. When evaluated through `words()` and whitespace splitting, the 5 ground-truth transcripts contain exactly 45 words (8, 10, 9, 10, 8). For graphemes, 326 was the count of non-whitespace Unicode code points. Under our CER policy (`characters()`), which excludes whitespace and punctuation per UAX #29, the actual evaluated grapheme denominator is exactly 181 grapheme clusters."*

### Q13: What happens if both reference and hypothesis are empty?
> *"If both are empty, our evaluation functions return `None` or safe 0.0 metrics rather than raising a ZeroDivisionError."*

### Q14: How does your UI prevent stale metrics from showing after an error?
> *"Streamlit retains session state between reruns. If a previous test succeeded and a subsequent test fails due to a network timeout, naive apps keep the old metrics on screen. In NADHAM QA, clicking any evaluation button immediately invalidates and purges all previous evaluation session state keys before dispatching the request."*

### Q15: How did you test the application?
> *"We wrote 102 automated Pytest unit and integration tests covering normalization, WER, CER, Critical Entities, audio analysis, clean/noisy comparison, dataset discovery, batch evaluation, and report generation. We also verified the full headless UI across all three tabs using Streamlit's official `AppTest` framework."*

---

## ⚖️ 10 Questions on Design Decisions & Honest Limitations

### Q16: Why did you build a rule-based Critical Information Detector instead of using an LLM or NER model?
> *"For speech recognition evaluation, deterministic reproducibility is vital. LLMs introduce non-deterministic outputs, API latency, token costs, and hallucination risks. A regex and dictionary-based pipeline runs in microseconds, is 100% reproducible across benchmark runs, and requires zero external cloud API credits."*

### Q17: Why is the Clean vs. Noisy feature marked as having unavailable paired samples?
> *"Because genuine paired recordings (the same speaker uttering the exact same sentence once in silence and once in background noise) do not exist in the repository dataset. Rather than synthetically mixing artificial white noise or fabricating results, we explicitly report that paired noisy audio is unavailable. This transparency demonstrates scientific integrity."*

### Q18: What is the current status of live transcription with Gnani Prisma?
> *"During our live API testing with Gnani Prisma STT (`https://api.vachana.ai/stt/v3`), an earlier API request encountered an upstream Cloudflare `HTTP 504 Gateway Time-out` due to temporary server latency. In a subsequent live evaluation, one live Malayalam speech recording was successfully transcribed with **8/8 words correct and 0% WER**. However, as a matter of scientific integrity, **one successful sample does not establish general Malayalam transcription accuracy**. Furthermore, our benchmark contains **five normal Malayalam speech recordings** and **does not contain genuine noisy recording pairs**—a condition we transparently disclose across the UI and all reports."*

### Q19: Why did you implement three separate tabs instead of one long page?
> *"Evaluation tasks have distinct cognitive goals: Tab 1 is for ad-hoc single sample testing; Tab 2 is for acoustic degradation experiments; Tab 3 is for formal, multi-file benchmark verification. Separating them into tabs keeps the user interface clean, uncluttered, and intuitive."*

### Q20: Why did you use Wagner-Fischer instead of an external library like JiWER?
> *"Implementing Wagner-Fischer natively in pure Python gives us complete control over token normalization, Unicode chillu handling, custom cost weights, and direct access to backtraced operation paths (Substitutions, Deletions, Insertions) for our interactive alignment table and export reports."*

### Q21: What is the purpose of the 3 separate export reports in Tab 3?
> *"Different stakeholders need different formats: executives and human auditors need the human-readable TXT summary; data analysts need the granular Sample-Level CSV for spreadsheet pivot tables; and MLOps / DevOps engineers need the Aggregate Metrics CSV for automated CI/CD gating."*

### Q22: Why did you choose Streamlit over React or FastAPI?
> *"For an AI and machine learning evaluation platform, Streamlit enables rapid, pythonic reactive UI development, native file uploading and audio playback, seamless integration with Pandas dataframes, and automated headless testing via Streamlit `AppTest`."*

### Q23: How would you implement Inverse Text Normalization (ITN) in the future?
> *"We would create a mapping engine that parses Malayalam number words (e.g., `രണ്ടായിരത്തി ഇരുപത്തിയാറ്`) into numeric digits (`2026`) prior to Levenshtein alignment, ensuring that speech engines aren't unfairly penalized for outputting words instead of digits."*

### Q24: What makes this project 'Kerala-First'?
> *"The text normalization rules are specifically designed for Malayalam Unicode nuances: canonical chillu resolution, zero-width joiners, chandrakkala (virama) behavior, Malayalam negation words (`അല്ല`, `ഇല്ല`, `പാടില്ല`), and Kerala geographical entities (`തിരുവനന്തപുരം`, `കൊച്ചി`, `തൃശ്ശൂർ`, `കോഴിക്കോട്`)."*

### Q25: If you had another week, what would you add next?
> *"I would implement Inverse Text Normalization (ITN) for Malayalam numbers, add calibrated SNR-controlled acoustic noise injection for synthetic degradation testing, and expand our benchmark dataset to include all 14 districts of Kerala."*
