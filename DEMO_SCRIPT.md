# 🎬 NADHAM QA 2.0: 3–5 Minute Video Demonstration Script

**Project:** NADHAM QA — Kerala-First Indian Voice Intelligence Testing Platform  
**Target Audience:** Gnani AI Internship Challenge Evaluators & Technical Leadership  
**Presenter:** Intern Candidate  
**Total Duration:** Approximately 4 minutes 30 seconds  
**Live Application URL:** https://nadham-voice.streamlit.app/  

---

## 📋 Demonstration Overview & Pre-Flight Setup

### Preparation Before Recording:
1. Open the live application in your browser: `https://nadham-voice.streamlit.app/`.
2. Ensure browser zoom is at 100% and dark/analytics theme renders cleanly.
3. Have sample files accessible:
   - Sample Audio: `dataset/normal/ML_NORMAL_01.mp3.mp3`
   - Sample Ground Truth: Content of `dataset/transcripts/ML_NORMAL_01.mp3.txt` (`എൻ്റെ പേര് സാവിയോ എന്നാണ്. ഞാൻ കേരളത്തിൽ നിന്നാണ് വരുന്നത്.`)
4. **API Call Notice:** To protect API credits and avoid live Cloudflare 504 gateway delays during recording, point out the pre-validated features or run the batch benchmark on Tab 3 where all mock and verification behaviors are transparent.

---

## ⏱️ Step-by-Step Demonstration Timeline

### Step 1: Introduction & The Malayalam Speech Problem (0:00 – 0:25)
- **What to Click / Show:**  
  Start on the application header showing `🎙️ NADHAM QA | Kerala-first. India-ready.`. Show the three top navigation tabs (`Single Evaluation`, `Clean vs. Noisy Comparison`, `Malayalam Benchmark & Reliability Evidence`).
- **What Should Appear:**  
  Clean, professional dark navy header, subtitle, and navigation tabs.
- **What to Say:**  
  *"Hello everyone. I'm presenting NADHAM QA 2.0, a testing and reliability platform built for Indian voice intelligence, with a special focus on Malayalam.*  
  *Evaluating speech recognition in Indian languages has a major blind spot: standard tools use ASCII whitespace splitting and Latin character models. In Malayalam, unique orthographic structures—like chillu characters and zero-width joiners—cause standard tools to falsely inflate error rates. NADHAM QA was built to give Indian voice AI the scientific, linguistically aware testing it truly requires."*
- **What Evaluator Should Understand:**  
  Candidate understands regional language orthography and why Western NLP evaluation tools fail on Indian scripts.

---

### Step 2: Gnani Prisma STT v2.5 Integration Architecture (0:25 – 0:55)
- **What to Click / Show:**  
  Point to the API status pill and the language selector dropdown showing `Malayalam (ml-IN)`, `English (en-IN)`, and `Hindi (hi-IN)`.
- **What Should Appear:**  
  Language selector widget and API integration badges.
- **What to Say:**  
  *"Under the hood, NADHAM QA is powered by Gnani Prisma STT v2.5 via the Vachana STT v3 REST endpoint. The client handles dual-source authentication via environment variables or Streamlit secrets, enforces a 25 MB upload limit, and features client-side guards that reject 0-byte audio to protect API quotas. Crucially, it includes an upstream HTML sanitizer that catches Cloudflare 502 and 504 gateway timeouts without breaking the UI layout."*
- **What Evaluator Should Understand:**  
  Integration is production-grade, secure, defensive, and respectful of API quotas.

---

### Step 3: Single Audio Evaluation Demonstration (0:55 – 1:35)
- **What to Click / Show:**  
  Stay on `🎙️ Single Evaluation`.  
  1. Upload `ML_NORMAL_01.mp3.mp3` to the audio uploader.
  2. Play the embedded audio preview using `st.audio`.
  3. Paste ground-truth transcript: `എൻ്റെ പേര് സാവിയോ എന്നാണ്. ഞാൻ കേരളത്തിൽ നിന്നാണ് വരുന്നത്.`
  4. Point to the primary action button: `🚀 Run NADHAM QA Test`.
- **What Should Appear:**  
  Audio waveform player renders. Reference text is displayed in the input area.
- **What to Say:**  
  *"Let's look at Tab 1: Single Audio Evaluation. I upload a genuine Malayalam speech recording from our dataset and paste the verified human transcript. Evaluators can listen directly via the embedded audio player.*  
  *When we run the test, the audio is transcribed by Gnani Prisma, and both transcripts pass through our Indic Normalization Engine. The engine standardizes legacy consonant-virama-joiner chillu sequences into atomic Unicode characters and resolves zero-width controls so orthographic variations aren't falsely counted as speech recognition errors."*
- **What Evaluator Should Understand:**  
  Normalization solves real linguistic issues in Malayalam without altering semantic content.

---

### Step 4: Explaining WER vs. CER Results (1:35 – 2:10)
- **What to Click / Show:**  
  Scroll to the Metric Cards (`Word Error Rate`, `Character Error Rate`) and the interactive Word-Level Operations Table.
- **What Should Appear:**  
  WER and CER metric cards side-by-side, followed by the table with color-coded status pills (Correct, Substitution, Deletion, Insertion).
- **What to Say:**  
  *"Here are the results. We provide both Word Error Rate and Character Error Rate.*  
  *In an agglutinative language like Malayalam where suffixes attach to root words, word-level WER can be overly harsh. A single missing case marker penalizes the entire word. That's why we implemented Character Error Rate using Unicode UAX #29 extended grapheme clusters via the regex package.*  
  *Instead of counting raw code points—which breaks combining vowel signs—we treat the consonant and its attached matras as a single perceptual unit. Spaces and punctuation are excluded from CER so spacing differences don't distort character accuracy."*
- **What Evaluator Should Understand:**  
  Candidate deeply understands the mathematical and linguistic difference between WER and CER in Indic languages.

---

### Step 5: Critical Information Detection (2:10 – 2:40)
- **What to Click / Show:**  
  Scroll to the `Critical Information Detection & Entity Comparison` table.
- **What Should Appear:**  
  Two-column table comparing detected entities (numbers, currency, dates, negations) with Match/Changed/Missing status badges.
- **What to Say:**  
  *"A speech model might achieve a 10% WER, but if the one error is changing ₹500 to ₹5,000, or dropping the Malayalam negation 'ഇല്ല', the transcription fails in banking or healthcare.*  
  *NADHAM QA implements a deterministic two-pass alignment algorithm across seven critical categories: numbers, dates, times, currency amounts, phone numbers, negations, and named entities. Pass 1 locks in exact matches; Pass 2 detects changed amounts and values, alerting QA engineers to semantic risks."*
- **What Evaluator Should Understand:**  
  The platform moves beyond academic ASR metrics into real-world business reliability.

---

### Step 6: Audio Quality Analysis & Clean vs. Noisy Interface (2:40 – 3:10)
- **What to Click / Show:**  
  Click on Tab 2: `🔬 Clean vs. Noisy Comparison`. Scroll to the Acoustic Quality cards and the comparative metrics table.
- **What Should Appear:**  
  Dual audio uploaders, acoustic measurement cards (RMS dBFS, Peak Amplitude, Clipping %, Silence %), and $\Delta \text{WER}$ / $\Delta \text{CER}$ degradation deltas.
- **What to Say:**  
  *"Now let's switch to Tab 2: Clean vs. Noisy Comparison. This feature measures speech recognition degradation under background noise.*  
  *For PCM WAV files, our local acoustic analyzer measures duration, sample rate, peak amplitude, RMS energy, digital clipping percentage, and silence percentage using Python's standard wave and numpy libraries—with zero external cloud dependencies.*  
  *The engine compares clean and noisy recordings against a shared ground truth and computes degradation deltas: Delta WER and Delta CER."*
- **What Evaluator Should Understand:**  
  The candidate understands audio signal engineering and how acoustic degradation affects ASR accuracy.

---

### Step 7: Reproducible Malayalam Benchmark & Dataset Verification (3:10 – 3:45)
- **What to Click / Show:**  
  Click on Tab 3: `📊 Malayalam Benchmark & Reliability Evidence`.  
  Point to the 4 Overview Metric Cards (`Discovered Samples: 5`, `Verified Valid: 5`, `Acoustic Condition: Normal/Clean (5)`, `Paired Noise Status: Unavailable (0 pairs)`).  
  Highlight the informational callout alert regarding paired noise.
- **What Should Appear:**  
  Dataset inventory metrics, paired noise transparency callout, sample selection multiselect, and Credit Notice warning.
- **What to Say:**  
  *"Now to Tab 3: our Reproducible Malayalam Benchmark Platform. Here we transform individual testing into systematic evaluation.*  
  *The discovery engine automatically validates all five genuine Malayalam recordings in our dataset, resolving double file extensions like .mp3.mp3 and .mp3.txt.*  
  *Notice our engineering transparency: the dashboard explicitly states that genuine clean-versus-noisy paired recordings are not present in the current dataset. We refuse to fabricate synthetic noise or claim unverified degradation numbers.*  
  *When we execute the benchmark, aggregate metrics are computed strictly as global error quotients—sum of errors divided by sum of reference units—never as an arithmetic average of percentages."*
- **What Evaluator Should Understand:**  
  The candidate exhibits uncompromising scientific and engineering integrity.

---

### Step 8: Multi-Format Evidence Reports (3:45 – 4:15)
- **What to Click / Show:**  
  Point to the three export download buttons:
  1. `📥 Benchmark Summary (TXT)`
  2. `📊 Sample-Level CSV`
  3. `📈 Aggregate Metrics CSV`
- **What Should Appear:**  
  Three full-width download buttons.
- **What to Say:**  
  *"NADHAM QA generates three audit-ready evidence exports: a formatted plain-text Benchmark Summary containing complete metadata and transcripts, a granular Sample-Level CSV for spreadsheet analysis, and an Aggregate Metrics CSV designed for direct ingestion into CI/CD pipelines.*  
  *None of our reports or logs ever leak API keys or sensitive credentials."*
- **What Evaluator Should Understand:**  
  Outputs are structured for enterprise auditability and automated QA pipelines.

---

### Step 9: Honest Limitations, Roadmap & Conclusion (4:15 – 4:45)
- **What to Click / Show:**  
  Scroll back to the top branded header or show the `About NADHAM QA` expandable section.
- **What Should Appear:**  
  Header and footer branding.
- **What to Say:**  
  *"To conclude: we maintain strict engineering integrity about current testing status. While an earlier live request encountered a Cloudflare 504 gateway timeout, in a subsequent live test one live Malayalam recording was successfully transcribed with 8 out of 8 words correct and 0% WER. However, we state honestly that one successful sample does not establish general Malayalam accuracy across all dialects and speakers. Furthermore, our benchmark contains five normal Malayalam speech recordings and does not contain genuine noisy recording pairs, demonstrating complete transparency.*  
  *Our roadmap includes Inverse Text Normalization, multi-speaker diarization, and expansion to Tamil, Telugu, Kannada, and Hindi.*  
  *NADHAM QA is open-source, fully tested with 102 automated tests, and ready for deployment. Thank you."*
- **What Evaluator Should Understand:**  
  Candidate is mature, self-aware, scientifically honest, and has delivered a complete, high-impact project.

---

## 💡 Quick Speaking Tips for Presenter
1. **Pace:** Speak clearly at a moderate, conversational pace. Do not rush through the Indic linguistic terms.
2. **Pronunciation:** Pronounce Malayalam orthographic terms clearly: *Chillu* (ചി screen letters), *Matra* (vowel sign), *Virama* (chandrakkala `്`).
3. **Tone:** Confident, analytical, humble, and technically precise.
