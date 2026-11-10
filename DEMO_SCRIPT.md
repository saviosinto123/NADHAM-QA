# 🎤 NADHAM QA: 3-Minute Presentation & Demo Script

**Presenter:** Intern Candidate  
**Target Audience:** Gnani AI Technical Leadership & Evaluation Panel  
**Time Limit:** 3 Minutes  
**Focus:** Kerala-First Voice Intelligence Testing Platform  

---

## ⏱️ Minute 1: The Problem & Kerala-First Vision

**[Visual: Title screen — 🎙️ NADHAM QA: Kerala-first. India-ready.]**

> *"Good afternoon everyone. Today, voice intelligence in India is transforming banking, healthcare, and governance. But evaluating automatic speech recognition in regional languages has a major blind spot: standard evaluation tools fail on Indian language orthography.*
>
> *Take Malayalam, for example. In Malayalam, chillu characters can be written using modern atomic Unicode or legacy decomposed sequences with zero-width joiners. They look identical to the human eye, but standard Python tools treat them as completely different words, falsely inflating Word Error Rates.*
>
> *Furthermore, standard punctuation filters wipe out decimals like 3.14, turn dates like 15/08/1947 into corrupted single numbers, and fail on currency symbols like the Indian Rupee.*
>
> *To solve this, I built **NADHAM QA**—a specialized evaluation and benchmarking platform designed to test Indian voice intelligence models with true linguistic precision, deeply integrated with the Gnani Prisma STT engine."*

---

## ⏱️ Minute 2: Technical Architecture & Live Demo

**[Visual: Screen share of Streamlit dashboard at localhost:8501]**

> *"Let’s look at the application in action.*
>
> *Here on the dashboard, we select our target recording language—Malayalam, English, or Hindi—and upload our audio recording. Notice that the platform immediately provides an embedded audio player, allowing evaluators to audition the audio directly alongside the transcript.*
>
> *Under the hood, NADHAM QA features an Indic-aware Unicode normalization pipeline. It canonicalizes all six Malayalam chillu characters, eliminates zero-width spacing issues, preserves date formats and decimal points, and normalizes currency values without losing numbers.*
>
> *When we execute an evaluation, the system runs a Wagner-Fischer dynamic programming algorithm to perform exact word-level Levenshtein alignment. It displays the Word Error Rate, total errors, and reference word counts, paired with an interactive error diagnostics table that breaks down every single Substitution, Deletion, and Insertion.*
>
> *On the engineering side, the system is backed by **32 automated Pytest unit and integration tests** with a 100% pass rate, covering every linguistic edge case, API response type, and data invariant."*

---

## ⏱️ Minute 3: Resilience, Reporting & Next Steps

**[Visual: Show error table, TXT report download, CSV export, and defensive handling]**

> *"Beyond accuracy, NADHAM QA is engineered with enterprise-grade defensive guardrails:*
> - *It automatically rejects zero-byte audio files to avoid wasting paid API quotas.*
> - *It enforces a strict 25 MB file size limit to prevent memory exhaustion.*
> - *It instantly invalidates session state on new runs to eliminate stale metrics.*
> - *And during live testing when the upstream API returned an HTTP 504 gateway timeout, our built-in HTML error sanitizer cleanly protected the user interface without dumping raw Cloudflare markup.*
>
> *Finally, for auditability and CI/CD pipelines, evaluators can export comprehensive plain-text reports complete with execution timestamps, or download the full word-level error matrix as a structured CSV file.*
>
> *NADHAM QA ensures that when Gnani Prisma transcribes Indian voices, every metric is mathematically sound, linguistically faithful, and production-ready.*
>
> *Thank you, and I look forward to your questions."*

---

## 💡 Quick Answers for Potential Judge Questions

- **Q: How did you verify the Levenshtein alignment?**  
  *A: "We proved the mathematical invariant $\text{Substitutions} + \text{Deletions} + \text{Insertions} == \text{Total Errors}$ across all edge cases including 100% deletion, hallucination (>100% WER), and exact matches."*

- **Q: Why does the report state the live API is unverified?**  
  *A: "Because engineering honesty comes first. During our test run, the live endpoint returned an HTTP 504 gateway timeout from Cloudflare. While our request dispatch and error sanitization worked flawlessly, we do not claim successful live transcription until real text is returned."*

- **Q: How does this scale to other Indian languages?**  
  *A: "The normalization engine is designed to be extensible. While our focus was Malayalam chillu characters, the currency, date, decimal, and zero-width handlers apply equally to Hindi, Tamil, Telugu, and Kannada."*
