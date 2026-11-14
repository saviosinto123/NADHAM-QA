# 📱 NADHAM QA 2.0: Social Media Announcement Drafts

This document contains copy-paste-ready drafts for sharing **NADHAM QA 2.0** on LinkedIn and X (formerly Twitter).

---

## 👔 1. LinkedIn Announcement Post (Recommended Full Version)

```text
🚀 Excited to unveil NADHAM QA 2.0 — a Kerala-first Indian Voice Intelligence Testing & Reliability Platform built for the Gnani AI Great Indian AI Internship Challenge 2026! 🎙️🇮🇳

Evaluating Automatic Speech Recognition (ASR) in Indian languages has a major regional blind spot: standard Western evaluation toolkits rely on ASCII whitespace splitting and Latin character models.

When applied to Indic scripts—and Malayalam in particular—they fail on fundamental orthographic realities:
1️⃣ Malayalam Chillu Ambiguity: Modern atomic Unicode chillus (ൺ, ൻ, ർ, ൽ, ൾ, ൿ) vs legacy decomposed consonant + virama + ZWJ sequences look identical to human eyes, but naive tools treat them as 100% substitution errors.
2️⃣ Agglutination: Suffixes and postpositions attach directly to root words in Malayalam. A single boundary inflection penalizes the entire word in standard Word Error Rate (WER).
3️⃣ Critical Data Vulnerability: Stripping punctuation naively corrupts decimals (3.14 → 314), dates, and currency values (₹500 → 500).

To solve this, I built NADHAM QA 2.0, deeply integrated with Gnani Prisma STT (v2.5):

✨ Key Capabilities:
🔹 Indic & Malayalam Normalization: Canonical chillu mapping, zero-width joiner/space resolution, and number preservation.
🔹 Dual-Granularity Evaluation: Dynamic Programming Wagner-Fischer WER alongside Character Error Rate (CER) computed over Unicode UAX #29 extended grapheme clusters (\X via regex, whitespace excluded).
🔹 Critical Information Detection: A deterministic two-pass alignment engine auditing 7 high-risk categories (numbers, dates, times, currency, phone numbers, Malayalam negations like 'അല്ല'/'ഇല്ല', and regional named entities).
🔹 Local Acoustic Quality Analysis: Pure-Python WAV signal metrics (duration, sample rate, peak amplitude, RMS dBFS, digital clipping %, and 20ms frame silence %).
🔹 Clean vs. Noisy Degradation Comparison: Empirical quantification of speech degradation (ΔWER and ΔCER) under ambient noise.
🔹 Reproducible Malayalam Benchmark: Systematic batch evaluation across our genuine Malayalam speech dataset, computing exact global error quotients (Σerrors / Σunits) with audit-ready TXT and CSV evidence exports.

🔬 Engineering Integrity & Transparency:
In the spirit of honest engineering:
- Live testing with Gnani Prisma STT (https://api.vachana.ai/stt/v3): an earlier request encountered an upstream Cloudflare HTTP 504 Gateway Time-out. In a subsequent live evaluation, one live Malayalam speech recording was successfully transcribed with 8/8 words correct and 0% WER.
- However, one successful sample does not establish general Malayalam transcription accuracy across diverse speakers or regional dialects.
- The benchmark platform currently contains 5 normal Malayalam speech recordings (dataset/normal/) with 45 reference words and 181 grapheme clusters, validating reproducible evaluation mechanics.
- The platform does not contain genuine noisy recording pairs, and transparently discloses this rather than fabricating synthetic noise.
- Client request formatting and error sanitization are fully verified across 102 passing automated tests.

🔗 Try the Live App: https://nadham-voice.streamlit.app/
💻 GitHub Repository: https://github.com/saviosinto123/NADHAM-QA

I would love to hear feedback and technical insights from the speech AI and Indic NLP community!

#SpeechRecognition #VoiceAI #GnaniAI #IndicNLP #Malayalam #AIInternship #OpenSource #Streamlit #Python #MachineLearning #AIEvaluation
```

---

## 🐦 2. X / Twitter Announcement (Short Thread Version)

### Post 1 (Main Announcement):
```text
🎙️ Excited to announce NADHAM QA 2.0 — an Indian Voice Intelligence Testing Platform built for the @Gnani_ai Great Indian AI Internship Challenge 2026! 🇮🇳

Standard ASR tools fail on Malayalam orthography. NADHAM QA delivers scientific linguistic evaluation. 🧵👇

🔗 https://nadham-voice.streamlit.app/
```

### Post 2 (Core Features):
```text
2/4 Why Malayalam needs specialized QA:
• Canonical chillu mapping (resolving legacy virama+ZWJ vs atomic Unicode)
• Dual WER & CER over Unicode UAX #29 grapheme clusters
• Critical Info Detection (currency, dates, numbers, Malayalam negations 'അല്ല'/'ഇല്ല')
• Local WAV acoustic metrics (RMS, peak, clipping, silence)
```

### Post 3 (Benchmark & Engineering Transparency):
```text
3/4 Reproducible Malayalam Benchmark:
• Batch evaluation across genuine Malayalam speech recordings
• Exact global error quotients (Σerrors / Σunits, no percentage averaging)
• Transparent limitation reporting: zero synthetic noise fabrication
• 102 / 102 automated tests passing ✅
```

### Post 4 (Links):
```text
4/4 Open-source & live on Streamlit Cloud:
💻 GitHub: https://github.com/saviosinto123/NADHAM-QA
📊 Live App: https://nadham-voice.streamlit.app/

Feedback from the speech AI and Indic NLP community is warmly welcomed! 🚀

#VoiceAI #IndicNLP #Malayalam #SpeechAI #Python
```
