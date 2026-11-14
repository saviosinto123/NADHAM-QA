import io
import os
import re
import csv
import time
import regex
import requests
import wave
import numpy as np
import streamlit as st
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import unicodedata

load_dotenv()

API_URL = "https://api.vachana.ai/stt/v3"
MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB upload limit

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NADHAM QA | Speech Recognition Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# Custom Styling - Modern Dark Navy & Blue Analytics Theme
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background-color: #0B1120;
        color: #F1F5F9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Branded Header Container */
    .brand-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }
    .brand-title {
        color: #F8FAFC;
        margin: 0;
        font-size: 30px;
        font-weight: 700;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-tag {
        font-size: 13px;
        font-weight: 600;
        background: rgba(37, 99, 235, 0.15);
        color: #60A5FA;
        border: 1px solid #2563EB;
        border-radius: 9999px;
        padding: 3px 12px;
        vertical-align: middle;
    }
    .brand-desc {
        color: #94A3B8;
        margin: 6px 0 0 0;
        font-size: 15px;
        font-weight: 400;
    }

    /* Status Bar Card */
    .status-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .status-card-label {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-card-val {
        color: #F8FAFC;
        font-size: 14px;
        font-weight: 600;
    }

    /* Section Cards */
    .panel-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .panel-header {
        color: #F8FAFC;
        font-size: 17px;
        font-weight: 600;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Operation Badges */
    .pill-correct {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid #059669;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        display: inline-block;
    }
    .pill-sub {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid #D97706;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        display: inline-block;
    }
    .pill-del {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid #DC2626;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        display: inline-block;
    }
    .pill-ins {
        background: rgba(139, 92, 246, 0.15);
        color: #A78BFA;
        border: 1px solid #7C3AED;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        display: inline-block;
    }

    /* Primary Evaluate Button */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 10px;
        border: 1px solid #3B82F6;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.35);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        border-color: #60A5FA;
        box-shadow: 0 6px 22px rgba(59, 130, 246, 0.55);
        transform: translateY(-1px);
    }

    /* Secondary Compare Button */
    div.stButton > button[kind="secondary"] {
        background: #1E293B;
        color: #38BDF8;
        font-size: 15px;
        font-weight: 600;
        padding: 11px 22px;
        border-radius: 10px;
        border: 1px solid #38BDF8;
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.15);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: #38BDF8;
        color: #0F172A;
        border-color: #7DD3FC;
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.35);
        transform: translateY(-1px);
    }

    /* Audio Quality & Comparison Metric Cards */
    .audio-card {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 8px;
    }
    .delta-badge-better {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid #059669;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 600;
    }
    .delta-badge-worse {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid #DC2626;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 600;
    }
    .delta-badge-neutral {
        background: rgba(148, 163, 184, 0.15);
        color: #94A3B8;
        border: 1px solid #475569;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Indic & Malayalam Normalization Pipeline
# -----------------------------------------------------------------------------
MALAYALAM_CHILLU_MAP = {
    "\u0D23\u0D4D\u200D": "\u0D7A",  # ൺ (N)
    "\u0D28\u0D4D\u200D": "\u0D7B",  # ൻ (NN)
    "\u0D30\u0D4D\u200D": "\u0D7C",  # ർ (RR)
    "\u0D32\u0D4D\u200D": "\u0D7D",  # ൽ (L)
    "\u0D33\u0D4D\u200D": "\u0D7E",  # ൾ (LL)
    "\u0D15\u0D4D\u200D": "\u0D7F",  # ൿ (K)
}

def words(text):
    # 1. Map legacy chillu with ZWJ to atomic chillu
    for leg, at in MALAYALAM_CHILLU_MAP.items():
        text = text.replace(leg, at)

    # 2. Replace zero-width spaces and non-breaking spaces with standard space
    text = re.sub(r"[\u200B\u00A0]", " ", text)

    # 3. Strip isolated ZWJ and ZWNJ
    text = re.sub(r"[\u200C\u200D]", "", text)

    # 4. Standard NFC normalization and lowercasing
    text = unicodedata.normalize("NFC", text.lower())

    tokens = text.split()
    cleaned = []

    for token in tokens:
        # Strip currency symbols (₹, $, €, £, etc.)
        token = "".join(ch for ch in token if unicodedata.category(ch) != "Sc")

        # Strip commas inside digit sequences (e.g. 1,00,000 -> 100000)
        token = re.sub(r"(?<=\d),(?=\d)", "", token)

        # Strip leading and trailing punctuation (brackets, quotes, periods, commas, etc.)
        token = re.sub(r"^[^\w\u0D00-\u0D7F]+|[^\w\u0D00-\u0D7F]+$", "", token)

        # If token is a decimal (e.g. 3.14), date (e.g. 15/08/1947 or 15-08-1947), or time (e.g. 12:30), preserve it
        if not re.match(r"^\d+([./:-]\d+)+$", token):
            # For regular words, strip internal punctuation
            token = "".join(
                ch for ch in token
                if not unicodedata.category(ch).startswith("P")
            )

        if token:
            cleaned.append(token)

    return cleaned


# -----------------------------------------------------------------------------
# Evaluation Engine (Wagner-Fischer Dynamic Programming)
# -----------------------------------------------------------------------------
def evaluate(reference, predicted):
    ref = words(reference)
    hyp = words(predicted)

    if not ref:
        return None

    dp = [[0] * (len(hyp) + 1) for _ in range(len(ref) + 1)]

    for i in range(len(ref) + 1):
        dp[i][0] = i

    for j in range(len(hyp) + 1):
        dp[0][j] = j

    for i in range(1, len(ref) + 1):
        for j in range(1, len(hyp) + 1):
            cost = 0 if ref[i-1] == hyp[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )

    # Trace back to identify individual errors
    i, j = len(ref), len(hyp)
    operations = []

    while i > 0 or j > 0:
        if i > 0 and j > 0:
            cost = 0 if ref[i-1] == hyp[j-1] else 1

            if dp[i][j] == dp[i-1][j-1] + cost:
                if cost == 0:
                    operations.append(("Correct", ref[i-1], hyp[j-1]))
                else:
                    operations.append(("Substitution", ref[i-1], hyp[j-1]))
                i -= 1
                j -= 1
                continue

        if i > 0 and dp[i][j] == dp[i-1][j] + 1:
            operations.append(("Deletion", ref[i-1], "—"))
            i -= 1
            continue

        operations.append(("Insertion", "—", hyp[j-1]))
        j -= 1

    operations.reverse()

    errors = dp[-1][-1]

    return {
        "wer": errors / len(ref) * 100,
        "errors": errors,
        "reference_words": len(ref),
        "recognized_words": len(hyp),
        "operations": operations
    }


# -----------------------------------------------------------------------------
# Character-Level Evaluation Engine (Unicode Grapheme Clusters & CER)
# -----------------------------------------------------------------------------
def characters(text):
    """
    Extract normalized Unicode grapheme clusters for Character Error Rate (CER).

    Linguistic & Normalization Policy:
    1. Reuses the canonical Indic normalization pipeline (Malayalam chillu mapping,
       zero-width character handling [ZWSP, NBSP, ZWJ, ZWNJ], NFC normalization,
       currency stripping, Indian numeric comma stripping, and punctuation removal).
    2. Whitespace Policy:
       Whitespace is excluded from the character stream. In agglutinative Indic languages
       such as Malayalam, compounds may be transcribed with or without spaces
       (e.g., 'വീട്ടിൽ പോയി' vs 'വീട്ടിൽപ്പോയി'). Excluding whitespace prevents
       artificial space insertion/deletion penalties from distorting acoustic speech accuracy.
    3. Grapheme Cluster Segmentation:
       Uses Unicode extended grapheme cluster matching (regex r'\\X') per UAX #29.
       Combining signs (vowel matras, viramas, anusvaras) remain attached to their base
       consonant as a single perceptual grapheme unit (e.g., 'യാ' = 1, 'ളം' = 1).
    """
    cleaned_tokens = words(text)
    graphemes = []
    for token in cleaned_tokens:
        graphemes.extend(regex.findall(r"\X", token))
    return graphemes


def evaluate_cer(reference, predicted):
    """
    Calculate Character Error Rate (CER) and character-level edit operations
    using Wagner-Fischer Dynamic Programming over Unicode grapheme clusters.

    Formula:
        CER = (Substitutions + Deletions + Insertions) / Reference Grapheme Count * 100

    Returns:
        dict containing:
            'cer': float percentage (or None if reference has 0 graphemes)
            'errors': int total character edit distance
            'reference_chars': int total reference graphemes
            'recognized_chars': int total predicted graphemes
            'substitutions': int count of character substitutions
            'deletions': int count of character deletions
            'insertions': int count of character insertions
            'correct': int count of matching graphemes
            'operations': list of (operation, ref_char, hyp_char)
    """
    ref_chars = characters(reference)
    hyp_chars = characters(predicted)

    if not ref_chars:
        return None

    dp = [[0] * (len(hyp_chars) + 1) for _ in range(len(ref_chars) + 1)]

    for i in range(len(ref_chars) + 1):
        dp[i][0] = i

    for j in range(len(hyp_chars) + 1):
        dp[0][j] = j

    for i in range(1, len(ref_chars) + 1):
        for j in range(1, len(hyp_chars) + 1):
            cost = 0 if ref_chars[i-1] == hyp_chars[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution / match
            )

    # Trace back to identify individual character errors
    i, j = len(ref_chars), len(hyp_chars)
    operations = []

    while i > 0 or j > 0:
        if i > 0 and j > 0:
            cost = 0 if ref_chars[i-1] == hyp_chars[j-1] else 1
            if dp[i][j] == dp[i-1][j-1] + cost:
                if cost == 0:
                    operations.append(("Correct", ref_chars[i-1], hyp_chars[j-1]))
                else:
                    operations.append(("Substitution", ref_chars[i-1], hyp_chars[j-1]))
                i -= 1
                j -= 1
                continue

        if i > 0 and dp[i][j] == dp[i-1][j] + 1:
            operations.append(("Deletion", ref_chars[i-1], "—"))
            i -= 1
            continue

        operations.append(("Insertion", "—", hyp_chars[j-1]))
        j -= 1

    operations.reverse()

    errors = dp[-1][-1]
    sub_count = sum(1 for op in operations if op[0] == "Substitution")
    del_count = sum(1 for op in operations if op[0] == "Deletion")
    ins_count = sum(1 for op in operations if op[0] == "Insertion")
    correct_count = sum(1 for op in operations if op[0] == "Correct")

    return {
        "cer": (errors / len(ref_chars)) * 100,
        "errors": errors,
        "reference_chars": len(ref_chars),
        "recognized_chars": len(hyp_chars),
        "substitutions": sub_count,
        "deletions": del_count,
        "insertions": ins_count,
        "correct": correct_count,
        "operations": operations
    }


# -----------------------------------------------------------------------------
# Critical Information Detection & Entity Comparison Engine
# -----------------------------------------------------------------------------
ML_NEGATION_PATTERNS = [
    r"(?:^|\s)(?:അല്ല|ഇല്ല|വേണ്ട|പാടില്ല|അരുത്)(?:$|[\s.,!?;:])",
    r"\S+(?:യല്ല|തല്ല|ില്ല|യില്ല|രുത്)(?:$|[\s.,!?;:])"
]
ML_NEG_REGEX = re.compile("|".join(ML_NEGATION_PATTERNS))

EN_NEGATIONS = {
    "not", "no", "never", "none", "neither", "nor", "cannot",
    "can't", "won't", "isn't", "aren't", "wasn't", "weren't", "don't", "doesn't", "didn't"
}

KNOWN_INDIC_NAMES = {
    "സാവിയോ", "സിന്ധു", "സാജു", "സാവിയോ സിന്ധു", "സാവിയോ സാജു"
}


def extract_critical_entities(text):
    """
    Extract domain-critical information entities using rule-based parsing:
    - Currency and amounts (₹, Rs, INR, $, €, £, രൂപ)
    - Dates (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)
    - Times (HH:MM AM/PM, 24-hr)
    - Phone numbers (10-digit Indian sequences, +91)
    - Numbers (Integers, Decimals, Indian formatted 1,00,000)
    - Negations (English keywords & Malayalam verbal suffixes)
    - Names (Dataset proper nouns & candidate entities)
    """
    if not text or not text.strip():
        return []

    entities = []
    consumed_spans = []

    def is_overlapping(span):
        return any(max(s[0], span[0]) < min(s[1], span[1]) for s in consumed_spans)

    # 1. Phone Numbers (Indian 10-digit mobile or with +91 / 0)
    phone_pattern = re.compile(
        r"(?:(?:\+91[\-\s]?)|(?:0))?[6-9]\d{4}[\-\s]?\d{5}\b|(?:\+91[\-\s]?)?[6-9]\d{9}\b"
    )
    for m in phone_pattern.finditer(text):
        digits = re.sub(r"\D", "", m.group())
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        elif len(digits) == 11 and digits.startswith("0"):
            digits = digits[1:]
        if len(digits) == 10 and digits[0] in "6789":
            entities.append({
                "category": "Phone Number",
                "raw": m.group().strip(),
                "normalized": digits,
                "span": m.span()
            })
            consumed_spans.append(m.span())

    # 2. Currency & Amounts (₹500, Rs. 1,00,000, INR 5000, $50, 500 രൂപ)
    curr_pattern = re.compile(
        r"(?:(₹|Rs\.?|INR|\$|€|£)\s*(\d+(?:,\d+)*(?:\.\d+)?))|(\b\d+(?:,\d+)*(?:\.\d+)?\s*(രൂപ|dollars?|rupees?))",
        re.IGNORECASE
    )
    for m in curr_pattern.finditer(text):
        if not is_overlapping(m.span()):
            raw_match = m.group().strip()
            num_match = re.search(r"\d+(?:,\d+)*(?:\.\d+)?", raw_match)
            if num_match:
                clean_num = num_match.group().replace(",", "")
                try:
                    num_val = float(clean_num) if "." in clean_num else int(clean_num)
                except ValueError:
                    num_val = clean_num
                curr_sym = "₹"
                if "$" in raw_match: curr_sym = "$"
                elif "€" in raw_match: curr_sym = "€"
                elif "£" in raw_match: curr_sym = "£"
                elif "inr" in raw_match.lower(): curr_sym = "INR"
                elif "rs" in raw_match.lower(): curr_sym = "Rs"
                elif "രൂപ" in raw_match: curr_sym = "രൂപ"

                entities.append({
                    "category": "Currency",
                    "raw": raw_match,
                    "normalized": f"{curr_sym} {num_val}",
                    "val": num_val,
                    "span": m.span()
                })
                consumed_spans.append(m.span())

    # 3. Dates (15/11/2026, 15-08-1947, 2026-11-15)
    date_pattern = re.compile(
        r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b"
    )
    for m in date_pattern.finditer(text):
        if not is_overlapping(m.span()):
            raw = m.group().strip()
            entities.append({
                "category": "Date",
                "raw": raw,
                "normalized": re.sub(r"[-.]", "/", raw),
                "span": m.span()
            })
            consumed_spans.append(m.span())

    # 4. Times (10:30 AM, 18:00)
    time_pattern = re.compile(
        r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*(?:AM|PM|am|pm))?\b"
    )
    for m in time_pattern.finditer(text):
        if not is_overlapping(m.span()):
            raw = m.group().strip()
            norm = re.sub(r"\s+", " ", raw.upper())
            entities.append({
                "category": "Time",
                "raw": raw,
                "normalized": norm,
                "span": m.span()
            })
            consumed_spans.append(m.span())

    # 5. Generic Numbers (Integers & Decimals)
    num_pattern = re.compile(r"\b\d+(?:,\d+)*(?:\.\d+)?\b")
    for m in num_pattern.finditer(text):
        if not is_overlapping(m.span()):
            raw = m.group().strip()
            clean_num = raw.replace(",", "")
            try:
                num_val = float(clean_num) if "." in clean_num else int(clean_num)
            except ValueError:
                num_val = clean_num
            entities.append({
                "category": "Number",
                "raw": raw,
                "normalized": str(num_val),
                "val": num_val,
                "span": m.span()
            })
            consumed_spans.append(m.span())

    # 6. Negations
    for word_match in re.finditer(r"\b[A-Za-z']+\b", text):
        w_lower = word_match.group().lower()
        if w_lower in EN_NEGATIONS and not is_overlapping(word_match.span()):
            entities.append({
                "category": "Negation",
                "raw": word_match.group(),
                "normalized": w_lower,
                "span": word_match.span()
            })
            consumed_spans.append(word_match.span())

    for m in ML_NEG_REGEX.finditer(text):
        if not is_overlapping(m.span()):
            raw_text = m.group().strip()
            entities.append({
                "category": "Negation",
                "raw": raw_text,
                "normalized": raw_text,
                "span": m.span()
            })
            consumed_spans.append(m.span())

    # 7. Names (Known benchmark proper nouns)
    for name in KNOWN_INDIC_NAMES:
        for m in re.finditer(re.escape(name), text):
            if not is_overlapping(m.span()):
                entities.append({
                    "category": "Name",
                    "raw": m.group(),
                    "normalized": m.group(),
                    "span": m.span()
                })
                consumed_spans.append(m.span())

    entities.sort(key=lambda x: x["span"][0])
    return entities


def compare_critical_entities(reference_text, hypothesis_text):
    """
    Compare domain-critical entities between ground truth reference and recognized transcript.

    Returns:
        dict containing:
            'total_items': int count of critical entities in reference
            'matching_items': int exact matches
            'changed_items': int altered entities (same category, different value)
            'missing_items': int entities present in reference but absent in transcript
            'extra_items': int spurious entities inserted in transcript
            'accuracy': float percentage of reference critical items preserved
            'details': list of dicts with Category, Reference Value, Recognized Value, Status, Explanation
    """
    ref_entities = extract_critical_entities(reference_text)
    hyp_entities = extract_critical_entities(hypothesis_text)

    matched_ref_indices = set()
    matched_hyp_indices = set()
    comparison_rows = []

    # Pass 1: Exact matches (priority alignment across all items)
    for r_idx, r in enumerate(ref_entities):
        cat = r["category"]
        r_norm = r["normalized"]
        for h_idx, h in enumerate(hyp_entities):
            if h_idx not in matched_hyp_indices and h["category"] == cat:
                if h["normalized"] == r_norm:
                    matched_ref_indices.add(r_idx)
                    matched_hyp_indices.add(h_idx)
                    comparison_rows.append({
                        "Category": cat,
                        "Reference Value": r["raw"],
                        "Recognized Value": h["raw"],
                        "Status": "Match",
                        "Explanation": f"Exact match for {cat} '{r['raw']}'"
                    })
                    break

    # Pass 2: Changed matches (same category, different values)
    for r_idx, r in enumerate(ref_entities):
        if r_idx in matched_ref_indices:
            continue
        cat = r["category"]
        for h_idx, h in enumerate(hyp_entities):
            if h_idx not in matched_hyp_indices and h["category"] == cat:
                matched_ref_indices.add(r_idx)
                matched_hyp_indices.add(h_idx)
                comparison_rows.append({
                    "Category": cat,
                    "Reference Value": r["raw"],
                    "Recognized Value": h["raw"],
                    "Status": "Changed",
                    "Explanation": f"{cat} changed from '{r['raw']}' to '{h['raw']}'"
                })
                break

    # Pass 3: Missing reference entities
    for r_idx, r in enumerate(ref_entities):
        if r_idx not in matched_ref_indices:
            comparison_rows.append({
                "Category": r["category"],
                "Reference Value": r["raw"],
                "Recognized Value": "—",
                "Status": "Missing",
                "Explanation": f"{r['category']} '{r['raw']}' present in reference but missing in transcription"
            })

    # Pass 4: Extra hypothesis entities (spurious insertions)
    for h_idx, h in enumerate(hyp_entities):
        if h_idx not in matched_hyp_indices:
            comparison_rows.append({
                "Category": h["category"],
                "Reference Value": "—",
                "Recognized Value": h["raw"],
                "Status": "Extra",
                "Explanation": f"Spurious {h['category']} '{h['raw']}' inserted by speech engine"
            })

    total_ref_items = len(ref_entities)
    matches = sum(1 for row in comparison_rows if row["Status"] == "Match")
    changed = sum(1 for row in comparison_rows if row["Status"] == "Changed")
    missing = sum(1 for row in comparison_rows if row["Status"] == "Missing")
    extra = sum(1 for row in comparison_rows if row["Status"] == "Extra")
    accuracy = (matches / total_ref_items * 100) if total_ref_items > 0 else (100.0 if not hyp_entities else 0.0)

    return {
        "total_items": total_ref_items,
        "matching_items": matches,
        "changed_items": changed,
        "missing_items": missing,
        "extra_items": extra,
        "accuracy": accuracy,
        "details": comparison_rows
    }


# -----------------------------------------------------------------------------
# Audio Quality Analysis Engine
# -----------------------------------------------------------------------------
def analyze_audio_quality(audio_data, filename=None):
    """
    Locally inspect and compute acoustic measurements for uncompressed PCM WAV audio:
    - Duration (seconds)
    - Sample rate (Hz)
    - Channels (Mono / Stereo / Multi-channel count)
    - Peak amplitude (dBFS & linear)
    - RMS level (dBFS & linear)
    - Clipping percentage (% of samples exceeding saturation threshold >= 0.999)
    - Silence percentage (% of 20ms frames with RMS energy below -40 dBFS)

    For compressed formats (MP3, M4A, OGG, AAC) or malformed files, returns
    supported=False with an explanatory message, allowing valid audio to be passed
    to Gnani ASR without local acoustic decoding.
    """
    if audio_data is None:
        return {
            "supported": False,
            "error": "No audio data provided.",
            "duration_s": None,
            "sample_rate": None,
            "channels": None,
            "channels_desc": "None",
            "peak_dbfs": None,
            "rms_dbfs": None,
            "clipping_pct": None,
            "silence_pct": None
        }

    if hasattr(audio_data, "getvalue"):
        raw_bytes = audio_data.getvalue()
    elif hasattr(audio_data, "read"):
        pos = audio_data.tell() if hasattr(audio_data, "tell") else 0
        raw_bytes = audio_data.read()
        if hasattr(audio_data, "seek"):
            audio_data.seek(pos)
    elif isinstance(audio_data, (bytes, bytearray)):
        raw_bytes = bytes(audio_data)
    else:
        return {
            "supported": False,
            "error": f"Unsupported audio input type: {type(audio_data).__name__}",
            "duration_s": None,
            "sample_rate": None,
            "channels": None,
            "channels_desc": "None",
            "peak_dbfs": None,
            "rms_dbfs": None,
            "clipping_pct": None,
            "silence_pct": None
        }

    if len(raw_bytes) == 0:
        return {
            "supported": False,
            "error": "Audio file is empty (0 bytes).",
            "duration_s": 0.0,
            "sample_rate": None,
            "channels": None,
            "channels_desc": "None",
            "peak_dbfs": None,
            "rms_dbfs": None,
            "clipping_pct": None,
            "silence_pct": None
        }

    try:
        with wave.open(io.BytesIO(raw_bytes), "rb") as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()

            if framerate <= 0 or n_frames == 0:
                return {
                    "supported": True,
                    "format": "PCM WAV",
                    "channels": n_channels,
                    "channels_desc": "Mono" if n_channels == 1 else ("Stereo" if n_channels == 2 else f"{n_channels}-ch"),
                    "sample_rate": framerate,
                    "duration_s": 0.0,
                    "peak_dbfs": -100.0,
                    "rms_dbfs": -100.0,
                    "clipping_pct": 0.0,
                    "silence_pct": 100.0,
                    "note": "Zero-duration or header-only audio"
                }

            duration_s = float(n_frames / float(framerate))
            frames = wf.readframes(n_frames)

            if sampwidth == 2:
                samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
            elif sampwidth == 1:
                samples = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
            elif sampwidth == 4:
                samples = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
            else:
                return {
                    "supported": False,
                    "format": f"{sampwidth * 8}-bit PCM WAV",
                    "error": f"Bit depth {sampwidth * 8}-bit is not supported for local acoustic decoding.",
                    "channels": n_channels,
                    "channels_desc": "Mono" if n_channels == 1 else ("Stereo" if n_channels == 2 else f"{n_channels}-ch"),
                    "sample_rate": framerate,
                    "duration_s": round(duration_s, 2),
                    "peak_dbfs": None,
                    "rms_dbfs": None,
                    "clipping_pct": None,
                    "silence_pct": None
                }

            peak_val = float(np.max(np.abs(samples))) if samples.size > 0 else 0.0
            peak_dbfs = float(20.0 * np.log10(peak_val)) if peak_val > 1e-6 else -100.0

            rms_val = float(np.sqrt(np.mean(samples ** 2))) if samples.size > 0 else 0.0
            rms_dbfs = float(20.0 * np.log10(rms_val)) if rms_val > 1e-6 else -100.0

            clipping_count = int(np.sum(np.abs(samples) >= 0.999))
            clipping_pct = float((clipping_count / samples.size) * 100.0) if samples.size > 0 else 0.0

            mono_samples = np.mean(samples.reshape(-1, n_channels), axis=1) if n_channels > 1 else samples
            frame_len = max(1, int(framerate * 0.02))
            num_frames = len(mono_samples) // frame_len
            if num_frames > 0:
                framed = mono_samples[:num_frames * frame_len].reshape(num_frames, frame_len)
                frame_rms = np.sqrt(np.mean(framed ** 2, axis=1))
                silent_frames = int(np.sum(frame_rms < 0.01))
                silence_pct = float((silent_frames / num_frames) * 100.0)
            else:
                silence_pct = 100.0 if rms_val < 0.01 else 0.0

            channels_label = "Mono" if n_channels == 1 else ("Stereo" if n_channels == 2 else f"{n_channels}-ch")

            return {
                "supported": True,
                "format": "PCM WAV",
                "channels": n_channels,
                "channels_desc": channels_label,
                "sample_rate": framerate,
                "duration_s": round(duration_s, 2),
                "peak_dbfs": round(peak_dbfs, 2),
                "rms_dbfs": round(rms_dbfs, 2),
                "clipping_pct": round(clipping_pct, 2),
                "silence_pct": round(silence_pct, 2)
            }
    except Exception as exc:
        ext = ""
        if filename and "." in filename:
            ext = filename.rsplit(".", 1)[-1].upper()
        fmt_label = f"{ext} (Compressed)" if ext in ["MP3", "M4A", "OGG", "AAC", "FLAC"] else "Compressed / Non-WAV"
        return {
            "supported": False,
            "format": fmt_label,
            "error": "Local acoustic signal analysis requires uncompressed PCM WAV. File was accepted for Gnani ASR without local decoding.",
            "channels": None,
            "channels_desc": "Unknown",
            "sample_rate": None,
            "duration_s": None,
            "peak_dbfs": None,
            "rms_dbfs": None,
            "clipping_pct": None,
            "silence_pct": None
        }


# -----------------------------------------------------------------------------
# Clean vs. Noisy Comparison Engine
# -----------------------------------------------------------------------------
def compare_clean_noisy(
    reference_text,
    clean_transcript,
    noisy_transcript,
    clean_quality=None,
    noisy_quality=None
):
    """
    Compare speech recognition reliability between clean and noisy recordings
    against the ground truth reference transcript.

    Computes:
    - Clean WER, CER, Word errors, Critical Information
    - Noisy WER, CER, Word errors, Critical Information
    - Delta WER (Noisy WER - Clean WER)
    - Delta CER (Noisy CER - Clean CER)
    - Word error differences (Substitutions, Deletions, Insertions)
    - Objective determination of which recording performed better based on actual results.
    """
    clean_wer_eval = evaluate(reference_text, clean_transcript)
    noisy_wer_eval = evaluate(reference_text, noisy_transcript)
    clean_cer_eval = evaluate_cer(reference_text, clean_transcript)
    noisy_cer_eval = evaluate_cer(reference_text, noisy_transcript)
    clean_crit = compare_critical_entities(reference_text, clean_transcript)
    noisy_crit = compare_critical_entities(reference_text, noisy_transcript)

    clean_wer = clean_wer_eval["wer"] if clean_wer_eval else 0.0
    noisy_wer = noisy_wer_eval["wer"] if noisy_wer_eval else 0.0
    delta_wer = noisy_wer - clean_wer

    clean_cer = clean_cer_eval["cer"] if clean_cer_eval else 0.0
    noisy_cer = noisy_cer_eval["cer"] if noisy_cer_eval else 0.0
    delta_cer = noisy_cer - clean_cer

    clean_errors = clean_wer_eval["errors"] if clean_wer_eval else 0
    noisy_errors = noisy_wer_eval["errors"] if noisy_wer_eval else 0
    delta_errors = noisy_errors - clean_errors

    # Determine which recording performed better based strictly on calculated results
    if delta_wer > 0:
        better_recording = "clean"
        impact_summary = (
            f"Degradation under noise: Clean recording performed better by {delta_wer:.2f}% WER "
            f"({delta_cer:+.2f}% CER). Background noise introduced {delta_errors} additional word error(s)."
        )
    elif delta_wer < 0:
        better_recording = "noisy"
        impact_summary = (
            f"Inverse result: Noisy recording achieved {abs(delta_wer):.2f}% lower WER than clean recording "
            f"({delta_cer:+.2f}% CER). (Note: ASR acoustic models can occasionally benefit from ambient frequency "
            f"matching specific training data distributions)."
        )
    else:
        # WER tied, check CER
        if delta_cer > 0:
            better_recording = "clean"
            impact_summary = (
                f"Equal WER ({clean_wer:.2f}%), but clean recording achieved {delta_cer:.2f}% lower CER."
            )
        elif delta_cer < 0:
            better_recording = "noisy"
            impact_summary = (
                f"Equal WER ({clean_wer:.2f}%), but noisy recording achieved {abs(delta_cer):.2f}% lower CER."
            )
        else:
            better_recording = "tie"
            impact_summary = (
                f"Identical performance: Both recordings achieved exactly {clean_wer:.2f}% WER and {clean_cer:.2f}% CER."
            )

    # Word-level error differences
    clean_ops = clean_wer_eval["operations"] if clean_wer_eval else []
    noisy_ops = noisy_wer_eval["operations"] if noisy_wer_eval else []

    clean_subs = sum(1 for op in clean_ops if op[0] == "Substitution")
    noisy_subs = sum(1 for op in noisy_ops if op[0] == "Substitution")
    clean_dels = sum(1 for op in clean_ops if op[0] == "Deletion")
    noisy_dels = sum(1 for op in noisy_ops if op[0] == "Deletion")
    clean_ins = sum(1 for op in clean_ops if op[0] == "Insertion")
    noisy_ins = sum(1 for op in noisy_ops if op[0] == "Insertion")

    # Metrics comparison table rows
    table_rows = [
        {"Metric": "Word Error Rate (WER)", "Clean Recording": f"{clean_wer:.2f}%", "Noisy Recording": f"{noisy_wer:.2f}%", "Delta (Noisy - Clean)": f"{delta_wer:+.2f}%"},
        {"Metric": "Character Error Rate (CER)", "Clean Recording": f"{clean_cer:.2f}%", "Noisy Recording": f"{noisy_cer:.2f}%", "Delta (Noisy - Clean)": f"{delta_cer:+.2f}%"},
        {"Metric": "Total Word Errors", "Clean Recording": str(clean_errors), "Noisy Recording": str(noisy_errors), "Delta (Noisy - Clean)": f"{delta_errors:+d}"},
        {"Metric": "Word Substitutions", "Clean Recording": str(clean_subs), "Noisy Recording": str(noisy_subs), "Delta (Noisy - Clean)": f"{noisy_subs - clean_subs:+d}"},
        {"Metric": "Word Deletions", "Clean Recording": str(clean_dels), "Noisy Recording": str(noisy_dels), "Delta (Noisy - Clean)": f"{noisy_dels - clean_dels:+d}"},
        {"Metric": "Word Insertions", "Clean Recording": str(clean_ins), "Noisy Recording": str(noisy_ins), "Delta (Noisy - Clean)": f"{noisy_ins - clean_ins:+d}"},
        {"Metric": "Critical Entity Accuracy", "Clean Recording": f"{clean_crit['accuracy']:.2f}%", "Noisy Recording": f"{noisy_crit['accuracy']:.2f}%", "Delta (Noisy - Clean)": f"{noisy_crit['accuracy'] - clean_crit['accuracy']:+.2f}%"},
        {"Metric": "Critical Entities Preserved", "Clean Recording": f"{clean_crit['matching_items']}/{clean_crit['total_items']}", "Noisy Recording": f"{noisy_crit['matching_items']}/{noisy_crit['total_items']}", "Delta (Noisy - Clean)": f"{noisy_crit['matching_items'] - clean_crit['matching_items']:+d}"},
    ]

    # Add acoustic quality comparison rows if available
    cq_supported = clean_quality and clean_quality.get("supported")
    nq_supported = noisy_quality and noisy_quality.get("supported")

    if cq_supported:
        cq_dur = f"{clean_quality.get('duration_s', 0):.2f}s"
        cq_rms = f"{clean_quality.get('rms_dbfs', 0):.2f} dBFS"
        cq_peak = f"{clean_quality.get('peak_dbfs', 0):.2f} dBFS"
        cq_clip = f"{clean_quality.get('clipping_pct', 0):.2f}%"
        cq_sil = f"{clean_quality.get('silence_pct', 0):.2f}%"
    else:
        cq_dur = cq_rms = cq_peak = cq_clip = cq_sil = "N/A"

    if nq_supported:
        nq_dur = f"{noisy_quality.get('duration_s', 0):.2f}s"
        nq_rms = f"{noisy_quality.get('rms_dbfs', 0):.2f} dBFS"
        nq_peak = f"{noisy_quality.get('peak_dbfs', 0):.2f} dBFS"
        nq_clip = f"{noisy_quality.get('clipping_pct', 0):.2f}%"
        nq_sil = f"{noisy_quality.get('silence_pct', 0):.2f}%"
    else:
        nq_dur = nq_rms = nq_peak = nq_clip = nq_sil = "N/A"

    if cq_supported or nq_supported:
        table_rows.extend([
            {"Metric": "Audio RMS Energy", "Clean Recording": cq_rms, "Noisy Recording": nq_rms, "Delta (Noisy - Clean)": f"{(noisy_quality.get('rms_dbfs', 0) - clean_quality.get('rms_dbfs', 0)):+.2f} dB" if (cq_supported and nq_supported) else "N/A"},
            {"Metric": "Peak Amplitude", "Clean Recording": cq_peak, "Noisy Recording": nq_peak, "Delta (Noisy - Clean)": f"{(noisy_quality.get('peak_dbfs', 0) - clean_quality.get('peak_dbfs', 0)):+.2f} dB" if (cq_supported and nq_supported) else "N/A"},
            {"Metric": "Clipping Percentage", "Clean Recording": cq_clip, "Noisy Recording": nq_clip, "Delta (Noisy - Clean)": f"{(noisy_quality.get('clipping_pct', 0) - clean_quality.get('clipping_pct', 0)):+.2f}%" if (cq_supported and nq_supported) else "N/A"},
            {"Metric": "Silence Percentage", "Clean Recording": cq_sil, "Noisy Recording": nq_sil, "Delta (Noisy - Clean)": f"{(noisy_quality.get('silence_pct', 0) - clean_quality.get('silence_pct', 0)):+.2f}%" if (cq_supported and nq_supported) else "N/A"},
        ])

    return {
        "clean_wer": clean_wer,
        "noisy_wer": noisy_wer,
        "delta_wer": delta_wer,
        "clean_cer": clean_cer,
        "noisy_cer": noisy_cer,
        "delta_cer": delta_cer,
        "clean_errors": clean_errors,
        "noisy_errors": noisy_errors,
        "delta_errors": delta_errors,
        "clean_wer_eval": clean_wer_eval,
        "noisy_wer_eval": noisy_wer_eval,
        "clean_cer_eval": clean_cer_eval,
        "noisy_cer_eval": noisy_cer_eval,
        "clean_crit": clean_crit,
        "noisy_crit": noisy_crit,
        "better_recording": better_recording,
        "interpretation": impact_summary,
        "table_rows": table_rows
    }


def generate_comparison_txt_report(
    comp_results,
    reference,
    clean_audio_name,
    noisy_audio_name,
    language,
    clean_req_id="N/A",
    noisy_req_id="N/A"
):
    """Generate diagnostic plain-text comparison report between clean and noisy recordings."""
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table_lines = [
        f"{'Metric':<32} | {'Clean Recording':<18} | {'Noisy Recording':<18} | {'Delta (Noisy - Clean)'}",
        "-" * 95
    ]
    for row in comp_results["table_rows"]:
        table_lines.append(
            f"{row['Metric']:<32} | {row['Clean Recording']:<18} | {row['Noisy Recording']:<18} | {row['Delta (Noisy - Clean)']}"
        )
    table_text = "\n".join(table_lines)

    report = f"""================================================================================
NADHAM QA - CLEAN VS. NOISY SPEECH RECOGNITION COMPARISON REPORT
================================================================================
Timestamp:          {timestamp_str}
Clean Audio:        {clean_audio_name}
Noisy Audio:        {noisy_audio_name}
Language:           {language}
Model:              Gnani Prisma v2.5
Clean Request ID:   {clean_req_id}
Noisy Request ID:   {noisy_req_id}

BENCHMARK OUTCOME & RELIABILITY INTERPRETATION:
--------------------------------------------------------------------------------
Better Recording:   {comp_results['better_recording'].upper()}
Interpretation:     {comp_results['interpretation']}

ACCURACY & ACOUSTIC COMPARISON TABLE:
--------------------------------------------------------------------------------
{table_text}

TRANSCRIPTS:
--------------------------------------------------------------------------------
Shared Ground Truth Reference:
{reference}

Clean Recording Transcript:
{comp_results.get('clean_transcript', 'N/A')}

Noisy Recording Transcript:
{comp_results.get('noisy_transcript', 'N/A')}

================================================================================
Generated by NADHAM QA Platform | Kerala-first. India-ready.
"""
    return report


def generate_comparison_csv(comp_results):
    """Generate CSV byte data from comparison results table."""
    df = pd.DataFrame(comp_results["table_rows"])
    return df.to_csv(index=False).encode("utf-8")


# -----------------------------------------------------------------------------
# Gnani Prisma STT API Client & Credential Resolution
# -----------------------------------------------------------------------------
def get_api_key():
    """Retrieve Gnani API key from environment variables or Streamlit secrets."""
    # 1. Check OS environment variable (.env)
    key = os.getenv("GNANI_API_KEY")
    if key and key.strip():
        return key.strip()

    # 2. Safely check Streamlit Community Cloud secrets
    try:
        if hasattr(st, "secrets") and "GNANI_API_KEY" in st.secrets:
            sec_key = st.secrets["GNANI_API_KEY"]
            if sec_key and str(sec_key).strip():
                return str(sec_key).strip()
    except Exception:
        # Handles missing secrets file, access errors, or Streamlit runtime without secrets
        pass

    return None


def call_gnani(audio, language):
    api_key = get_api_key()

    if not api_key:
        raise ValueError("API key missing. Check your .env file.")

    audio_bytes = audio.getvalue()
    if len(audio_bytes) == 0:
        raise ValueError("The uploaded audio file is empty (0 bytes). Please upload a valid recording.")

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise ValueError("Audio file exceeds the maximum allowed size of 25 MB.")

    headers = {
        "X-API-Key-ID": api_key
    }

    files = {
        "audio_file": (
            audio.name,
            audio_bytes,
            audio.type or "application/octet-stream"
        )
    }

    data = {
        "language_code": language,
        "format": "verbatim"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        files=files,
        data=data,
        timeout=90
    )

    if response.status_code != 200:
        raw_text = response.text.strip()
        # Sanitize HTML / gateway errors (e.g. 502/504 from Cloudflare or upstream proxies)
        if "<html" in raw_text.lower() or "<!doctype" in raw_text.lower():
            if response.status_code in (502, 503, 504):
                raise Exception(
                    f"Gnani API gateway error (HTTP {response.status_code}). "
                    "The upstream speech service is temporarily unavailable or timed out. Please retry shortly."
                )
            else:
                raise Exception(f"Gnani API service returned an unexpected HTML error (HTTP {response.status_code}).")

        # Strip any stray HTML tags from error message
        clean_text = re.sub(r"<[^>]+>", "", raw_text[:250]).strip()
        raise Exception(
            f"Gnani API error {response.status_code}: {clean_text or 'Service error'}"
        )

    try:
        result = response.json()
    except Exception:
        raise Exception(f"Gnani API returned an invalid non-JSON response (HTTP {response.status_code}).")

    if not result.get("success"):
        raise Exception(str(result.get("error", result)))

    return result


# -----------------------------------------------------------------------------
# Benchmark Dataset Discovery & Batch Evaluation Engine
# -----------------------------------------------------------------------------
def extract_sample_id(filename: str) -> str:
    """Extract clean sample ID by stripping audio and text extensions repeatedly.

    Handles double extensions such as '.mp3.mp3' and '.mp3.txt'.
    """
    if not filename:
        return ""
    name = os.path.basename(filename)
    known_exts = {".mp3", ".wav", ".txt", ".ogg", ".flac", ".m4a"}
    while True:
        base, ext = os.path.splitext(name)
        if ext.lower() in known_exts and base:
            name = base
        else:
            break
    return name


def discover_benchmark_dataset(dataset_dir="dataset") -> dict:
    """Discover and validate benchmark audio recordings and reference transcripts.

    Discovers samples in dataset/normal/ and dataset/transcripts/, pairing them
    by canonical sample ID. Validates audio existence, file size, and transcript content.
    Transparently reports whether clean/noisy paired recordings are available.
    """
    if not os.path.isabs(dataset_dir):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidate = os.path.join(base_dir, dataset_dir)
        if os.path.exists(candidate):
            dataset_dir = candidate

    normal_dir = os.path.join(dataset_dir, "normal")
    transcripts_dir = os.path.join(dataset_dir, "transcripts")
    noisy_dir = os.path.join(dataset_dir, "noisy")

    # Check for paired noisy directory
    has_paired_noise = False
    if os.path.isdir(noisy_dir):
        noisy_files = [
            f for f in os.listdir(noisy_dir)
            if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a"))
        ]
        has_paired_noise = len(noisy_files) > 0

    audio_files = {}
    if os.path.isdir(normal_dir):
        for f in sorted(os.listdir(normal_dir)):
            if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a")):
                sid = extract_sample_id(f)
                audio_files[sid] = os.path.join(normal_dir, f)

    transcript_files = {}
    if os.path.isdir(transcripts_dir):
        for f in sorted(os.listdir(transcripts_dir)):
            if f.lower().endswith(".txt"):
                sid = extract_sample_id(f)
                transcript_files[sid] = os.path.join(transcripts_dir, f)

    all_sids = sorted(list(set(audio_files.keys()) | set(transcript_files.keys())))
    samples = []
    valid_count = 0
    invalid_count = 0

    for sid in all_sids:
        a_path = audio_files.get(sid)
        t_path = transcript_files.get(sid)

        sample = {
            "sample_id": sid,
            "audio_path": a_path,
            "audio_filename": os.path.basename(a_path) if a_path else None,
            "transcript_path": t_path,
            "transcript_filename": os.path.basename(t_path) if t_path else None,
            "reference_transcript": "",
            "audio_size_bytes": 0,
            "condition": "normal",
            "status": "valid",
            "error_detail": None
        }

        if not a_path or not os.path.exists(a_path):
            sample["status"] = "missing_audio"
            sample["error_detail"] = "Audio recording file missing from dataset/normal"
            invalid_count += 1
        elif os.path.getsize(a_path) == 0:
            sample["status"] = "invalid_audio"
            sample["error_detail"] = "Audio file is 0 bytes (empty)"
            invalid_count += 1
        elif os.path.getsize(a_path) > MAX_AUDIO_BYTES:
            sample["status"] = "invalid_audio"
            sample["error_detail"] = f"Audio file exceeds maximum size limit ({MAX_AUDIO_BYTES // (1024*1024)}MB)"
            invalid_count += 1
        elif not t_path or not os.path.exists(t_path):
            sample["status"] = "missing_transcript"
            sample["error_detail"] = "Reference transcript file missing from dataset/transcripts"
            invalid_count += 1
        else:
            try:
                sample["audio_size_bytes"] = os.path.getsize(a_path)
                with open(t_path, "r", encoding="utf-8") as tf:
                    text = tf.read().strip()
                if not text:
                    sample["status"] = "empty_transcript"
                    sample["error_detail"] = "Reference transcript file is empty"
                    invalid_count += 1
                else:
                    sample["reference_transcript"] = text
                    sample["status"] = "valid"
                    valid_count += 1
            except Exception as e:
                sample["status"] = "read_error"
                sample["error_detail"] = f"Failed to read reference transcript: {e}"
                invalid_count += 1

        samples.append(sample)

    return {
        "dataset_dir": dataset_dir,
        "samples": samples,
        "total_discovered": len(samples),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "has_paired_noise": has_paired_noise,
        "normal_condition_count": len([s for s in samples if s["status"] == "valid"]),
        "noisy_condition_count": 0,
        "clean_noisy_paired_count": 0
    }


def evaluate_benchmark_batch(
    samples_to_evaluate: list,
    progress_callback=None,
    api_caller=None,
    language="Malayalam"
) -> dict:
    """Execute batch evaluation across benchmark samples.

    Uses standard aggregate formulas (sum of errors / sum of reference units).
    Excludes failed or invalid samples from WER/CER denominator and error sums.
    """
    sample_results = []
    total_samples = len(samples_to_evaluate)

    for idx, sample in enumerate(samples_to_evaluate):
        sid = sample.get("sample_id", f"sample_{idx+1}")
        ref_text = sample.get("reference_transcript", "")
        audio_path = sample.get("audio_path")
        audio_fn = sample.get("audio_filename") or (os.path.basename(audio_path) if audio_path else "unknown")

        if progress_callback:
            progress_callback(idx, total_samples, sid)

        if sample.get("status") != "valid":
            sample_results.append({
                "sample_id": sid,
                "audio_filename": audio_fn,
                "reference": ref_text,
                "hypothesis": "",
                "status": "Skipped",
                "latency_sec": 0.0,
                "request_id": "N/A",
                "ref_words": 0,
                "hyp_words": 0,
                "word_errors": 0,
                "substitutions": 0,
                "deletions": 0,
                "insertions": 0,
                "wer": None,
                "ref_graphemes": 0,
                "hyp_graphemes": 0,
                "char_errors": 0,
                "char_substitutions": 0,
                "char_deletions": 0,
                "char_insertions": 0,
                "cer": None,
                "critical_expected": 0,
                "critical_matched": 0,
                "critical_changed": 0,
                "critical_missing": 0,
                "critical_extra": 0,
                "critical_match_rate": None,
                "error_message": sample.get("error_detail") or "Sample not valid for evaluation"
            })
            continue

        try:
            if not audio_path or not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            with open(audio_path, "rb") as af:
                audio_bytes = af.read()

            start_t = time.perf_counter()
            caller = api_caller if api_caller is not None else call_gnani

            resp = caller(audio_bytes, filename=audio_fn, language=language)
            latency = round(time.perf_counter() - start_t, 3)

            hyp_text = resp.get("transcript", "")
            req_id = resp.get("request_id") or resp.get("transaction_id") or "N/A"

            # WER Evaluation
            wer_res = evaluate(ref_text, hyp_text)
            if not wer_res:
                raise ValueError("WER evaluation returned None for empty reference")

            wer_subs = sum(1 for op in wer_res["operations"] if op[0] == "Substitution")
            wer_dels = sum(1 for op in wer_res["operations"] if op[0] == "Deletion")
            wer_ins = sum(1 for op in wer_res["operations"] if op[0] == "Insertion")
            wer_errors = wer_subs + wer_dels + wer_ins

            # CER Evaluation
            cer_res = evaluate_cer(ref_text, hyp_text)
            if not cer_res:
                raise ValueError("CER evaluation returned None for empty reference")

            # Critical Entities Evaluation
            crit_res = compare_critical_entities(ref_text, hyp_text)

            sample_results.append({
                "sample_id": sid,
                "audio_filename": audio_fn,
                "reference": ref_text,
                "hypothesis": hyp_text,
                "status": "Success",
                "latency_sec": latency,
                "request_id": req_id,
                "ref_words": wer_res["reference_words"],
                "hyp_words": wer_res["recognized_words"],
                "word_errors": wer_errors,
                "substitutions": wer_subs,
                "deletions": wer_dels,
                "insertions": wer_ins,
                "wer": round(wer_res["wer"], 2),
                "ref_graphemes": cer_res["reference_chars"],
                "hyp_graphemes": cer_res["recognized_chars"],
                "char_errors": cer_res["errors"],
                "char_substitutions": cer_res["substitutions"],
                "char_deletions": cer_res["deletions"],
                "char_insertions": cer_res["insertions"],
                "cer": round(cer_res["cer"], 2),
                "critical_expected": crit_res["total_items"],
                "critical_matched": crit_res["matching_items"],
                "critical_changed": crit_res["changed_items"],
                "critical_missing": crit_res["missing_items"],
                "critical_extra": crit_res["extra_items"],
                "critical_match_rate": round(crit_res["accuracy"], 1),
                "error_message": None
            })
        except Exception as e:
            sample_results.append({
                "sample_id": sid,
                "audio_filename": audio_fn,
                "reference": ref_text,
                "hypothesis": "",
                "status": "Failed",
                "latency_sec": 0.0,
                "request_id": "N/A",
                "ref_words": 0,
                "hyp_words": 0,
                "word_errors": 0,
                "substitutions": 0,
                "deletions": 0,
                "insertions": 0,
                "wer": None,
                "ref_graphemes": 0,
                "hyp_graphemes": 0,
                "char_errors": 0,
                "char_substitutions": 0,
                "char_deletions": 0,
                "char_insertions": 0,
                "cer": None,
                "critical_expected": 0,
                "critical_matched": 0,
                "critical_changed": 0,
                "critical_missing": 0,
                "critical_extra": 0,
                "critical_match_rate": None,
                "error_message": str(e)
            })

    if progress_callback:
        progress_callback(total_samples, total_samples, "Completed")

    # Aggregate Calculations
    success_list = [r for r in sample_results if r["status"] == "Success"]
    failed_list = [r for r in sample_results if r["status"] == "Failed"]
    skipped_list = [r for r in sample_results if r["status"] == "Skipped"]

    successful_count = len(success_list)
    failed_count = len(failed_list)
    skipped_count = len(skipped_list)

    if successful_count > 0:
        total_ref_words = sum(r["ref_words"] for r in success_list)
        total_hyp_words = sum(r["hyp_words"] for r in success_list)
        total_substitutions = sum(r["substitutions"] for r in success_list)
        total_deletions = sum(r["deletions"] for r in success_list)
        total_insertions = sum(r["insertions"] for r in success_list)
        total_word_errors = total_substitutions + total_deletions + total_insertions
        aggregate_wer = round((total_word_errors / total_ref_words) * 100, 2) if total_ref_words > 0 else 0.0

        total_ref_graphemes = sum(r["ref_graphemes"] for r in success_list)
        total_hyp_graphemes = sum(r["hyp_graphemes"] for r in success_list)
        total_char_substitutions = sum(r["char_substitutions"] for r in success_list)
        total_char_deletions = sum(r["char_deletions"] for r in success_list)
        total_char_insertions = sum(r["char_insertions"] for r in success_list)
        total_char_errors = total_char_substitutions + total_char_deletions + total_char_insertions
        aggregate_cer = round((total_char_errors / total_ref_graphemes) * 100, 2) if total_ref_graphemes > 0 else 0.0

        total_crit_expected = sum(r["critical_expected"] for r in success_list)
        total_crit_matched = sum(r["critical_matched"] for r in success_list)
        total_crit_changed = sum(r["critical_changed"] for r in success_list)
        total_crit_missing = sum(r["critical_missing"] for r in success_list)
        total_crit_extra = sum(r["critical_extra"] for r in success_list)
        aggregate_crit_match_rate = round((total_crit_matched / total_crit_expected) * 100, 2) if total_crit_expected > 0 else 100.0

        total_latency = sum(r["latency_sec"] for r in success_list)
        avg_latency = round(total_latency / successful_count, 3)
    else:
        total_ref_words = 0
        total_hyp_words = 0
        total_substitutions = 0
        total_deletions = 0
        total_insertions = 0
        total_word_errors = 0
        aggregate_wer = None

        total_ref_graphemes = 0
        total_hyp_graphemes = 0
        total_char_substitutions = 0
        total_char_deletions = 0
        total_char_insertions = 0
        total_char_errors = 0
        aggregate_cer = None

        total_crit_expected = 0
        total_crit_matched = 0
        total_crit_changed = 0
        total_crit_missing = 0
        total_crit_extra = 0
        aggregate_crit_match_rate = None
        avg_latency = 0.0

    success_rate = round((successful_count / total_samples) * 100, 1) if total_samples > 0 else 0.0

    return {
        "summary": {
            "total_samples": total_samples,
            "successful_samples": successful_count,
            "failed_samples": failed_count,
            "skipped_samples": skipped_count,
            "benchmark_success_rate": success_rate,
            "language": language,
            "timestamp": datetime.now().isoformat()
        },
        "aggregate": {
            "aggregate_wer": aggregate_wer,
            "total_ref_words": total_ref_words,
            "total_hyp_words": total_hyp_words,
            "total_word_errors": total_word_errors,
            "substitutions": total_substitutions,
            "deletions": total_deletions,
            "insertions": total_insertions,
            "aggregate_cer": aggregate_cer,
            "total_ref_graphemes": total_ref_graphemes,
            "total_hyp_graphemes": total_hyp_graphemes,
            "total_char_errors": total_char_errors,
            "char_substitutions": total_char_substitutions,
            "char_deletions": total_char_deletions,
            "char_insertions": total_char_insertions,
            "aggregate_critical_match_rate": aggregate_crit_match_rate,
            "total_critical_expected": total_crit_expected,
            "total_critical_matched": total_crit_matched,
            "total_critical_changed": total_crit_changed,
            "total_critical_missing": total_crit_missing,
            "total_critical_extra": total_crit_extra,
            "avg_latency_sec": avg_latency
        },
        "sample_results": sample_results
    }


def generate_benchmark_summary_txt(batch_results: dict, dataset_info: dict) -> str:
    """Generate comprehensive benchmark summary report in plain text format."""
    summary = batch_results.get("summary", {})
    agg = batch_results.get("aggregate", {})
    samples = batch_results.get("sample_results", [])

    lines = []
    lines.append("=" * 80)
    lines.append("NADHAM QA 2.0 — MALAYALAM SPEECH RECOGNITION BENCHMARK REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated at: {summary.get('timestamp', 'N/A')}")
    lines.append(f"Language: {summary.get('language', 'Malayalam')}")
    lines.append("Acoustic Condition: Normal / Clean (Real In-the-Wild Audio)")
    lines.append("Paired Noise Status: UNAVAILABLE (No paired clean/noisy recordings in dataset)")
    lines.append("")
    lines.append("1. DATASET INVENTORY")
    lines.append("-" * 80)
    lines.append(f"Total Discovered Samples : {dataset_info.get('total_discovered', len(samples))}")
    lines.append(f"Verified Valid Samples   : {dataset_info.get('valid_count', len(samples))}")
    lines.append(f"Total Evaluated Samples  : {summary.get('total_samples', 0)}")
    lines.append(f"Successful Evaluations   : {summary.get('successful_samples', 0)}")
    lines.append(f"Failed Evaluations       : {summary.get('failed_samples', 0)}")
    lines.append(f"Skipped Evaluations      : {summary.get('skipped_samples', 0)}")
    lines.append(f"Benchmark Success Rate   : {summary.get('benchmark_success_rate', 0.0)}%")
    lines.append("")
    lines.append("2. AGGREGATE RECOGNITION & ENTITY METRICS")
    lines.append("-" * 80)
    wer_str = f"{agg.get('aggregate_wer', 'N/A')}%" if agg.get('aggregate_wer') is not None else "N/A"
    cer_str = f"{agg.get('aggregate_cer', 'N/A')}%" if agg.get('aggregate_cer') is not None else "N/A"
    crit_str = f"{agg.get('aggregate_critical_match_rate', 'N/A')}%" if agg.get('aggregate_critical_match_rate') is not None else "N/A"
    lines.append(f"Aggregate Word Error Rate (WER)        : {wer_str}")
    lines.append(f"  - Total Reference Words              : {agg.get('total_ref_words', 0)}")
    lines.append(f"  - Total Hypothesis Words             : {agg.get('total_hyp_words', 0)}")
    lines.append(f"  - Total Word Errors                  : {agg.get('total_word_errors', 0)}")
    lines.append(f"  - Word Substitutions                 : {agg.get('substitutions', 0)}")
    lines.append(f"  - Word Deletions                     : {agg.get('deletions', 0)}")
    lines.append(f"  - Word Insertions                    : {agg.get('insertions', 0)}")
    lines.append("")
    lines.append(f"Aggregate Character Error Rate (CER)   : {cer_str}")
    lines.append(f"  - Total Reference Graphemes          : {agg.get('total_ref_graphemes', 0)}")
    lines.append(f"  - Total Hypothesis Graphemes         : {agg.get('total_hyp_graphemes', 0)}")
    lines.append(f"  - Total Character Errors             : {agg.get('total_char_errors', 0)}")
    lines.append(f"  - Character Substitutions            : {agg.get('char_substitutions', 0)}")
    lines.append(f"  - Character Deletions                : {agg.get('char_deletions', 0)}")
    lines.append(f"  - Character Insertions               : {agg.get('char_insertions', 0)}")
    lines.append("")
    lines.append(f"Aggregate Critical Entity Match Rate   : {crit_str}")
    lines.append(f"  - Total Expected Entities            : {agg.get('total_critical_expected', 0)}")
    lines.append(f"  - Total Matched Entities             : {agg.get('total_critical_matched', 0)}")
    lines.append(f"  - Total Changed Entities             : {agg.get('total_critical_changed', 0)}")
    lines.append(f"  - Total Missing Entities             : {agg.get('total_critical_missing', 0)}")
    lines.append(f"  - Total Extra Entities               : {agg.get('total_critical_extra', 0)}")
    lines.append(f"Average API Latency                    : {agg.get('avg_latency_sec', 0.0)}s")
    lines.append("")
    lines.append("3. SAMPLE-LEVEL EVALUATION BREAKDOWN")
    lines.append("-" * 80)
    lines.append(f"{'Sample ID':<16} | {'Status':<9} | {'WER (%)':<8} | {'CER (%)':<8} | {'Crit Match':<11} | {'Latency':<8} | {'Audio File':<22}")
    lines.append("-" * 80)
    for s in samples:
        sid = s.get("sample_id", "")
        st_val = s.get("status", "")
        w_val = f"{s.get('wer')}%" if s.get('wer') is not None else "N/A"
        c_val = f"{s.get('cer')}%" if s.get('cer') is not None else "N/A"
        cm_val = f"{s.get('critical_match_rate')}%" if s.get('critical_match_rate') is not None else "N/A"
        lat_val = f"{s.get('latency_sec', 0.0):.2f}s"
        afn = s.get("audio_filename", "")
        lines.append(f"{sid:<16} | {st_val:<9} | {w_val:<8} | {c_val:<8} | {cm_val:<11} | {lat_val:<8} | {afn:<22}")
    lines.append("")
    lines.append("4. DETAILED SAMPLE TRANSCRIPTS")
    lines.append("-" * 80)
    for s in samples:
        lines.append(f"[{s.get('sample_id')}] - {s.get('audio_filename')}")
        lines.append(f"  Status        : {s.get('status')}")
        lines.append(f"  Request ID    : {s.get('request_id', 'N/A')}")
        lines.append(f"  Reference     : {s.get('reference', '')}")
        lines.append(f"  Hypothesis    : {s.get('hypothesis', '')}")
        if s.get("error_message"):
            lines.append(f"  Error Detail  : {s.get('error_message')}")
        else:
            lines.append(f"  Word Errors   : {s.get('word_errors')} (S: {s.get('substitutions')}, D: {s.get('deletions')}, I: {s.get('insertions')})")
            lines.append(f"  Char Errors   : {s.get('char_errors')} (S: {s.get('char_substitutions')}, D: {s.get('char_deletions')}, I: {s.get('char_insertions')})")
        lines.append("")
    lines.append("=" * 80)
    lines.append("METHODOLOGICAL NOTE & LIMITATIONS")
    lines.append("=" * 80)
    lines.append("1. Aggregate WER and CER are calculated as exact global error quotients (sum of errors")
    lines.append("   divided by sum of reference units) rather than arithmetic averages of percentages.")
    lines.append("2. CER uses Unicode UAX #29 extended grapheme clusters; whitespace is excluded.")
    lines.append("3. Genuine clean/noisy paired recordings are not present in the current dataset;")
    lines.append("   NADHAM QA refrains from simulating artificial noise or synthesizing fake results.")
    lines.append("=" * 80)
    return "\n".join(lines)


def generate_benchmark_sample_csv(batch_results: dict) -> str:
    """Generate sample-level benchmark results in CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        "sample_id",
        "audio_filename",
        "status",
        "latency_sec",
        "request_id",
        "wer_pct",
        "ref_words",
        "hyp_words",
        "word_errors",
        "word_substitutions",
        "word_deletions",
        "word_insertions",
        "cer_pct",
        "ref_graphemes",
        "hyp_graphemes",
        "char_errors",
        "char_substitutions",
        "char_deletions",
        "char_insertions",
        "critical_expected",
        "critical_matched",
        "critical_changed",
        "critical_missing",
        "critical_extra",
        "critical_match_rate_pct",
        "reference",
        "hypothesis",
        "error_message"
    ]
    writer.writerow(headers)

    for s in batch_results.get("sample_results", []):
        writer.writerow([
            s.get("sample_id", ""),
            s.get("audio_filename", ""),
            s.get("status", ""),
            s.get("latency_sec", 0.0),
            s.get("request_id", ""),
            s.get("wer") if s.get("wer") is not None else "",
            s.get("ref_words", 0),
            s.get("hyp_words", 0),
            s.get("word_errors", 0),
            s.get("substitutions", 0),
            s.get("deletions", 0),
            s.get("insertions", 0),
            s.get("cer") if s.get("cer") is not None else "",
            s.get("ref_graphemes", 0),
            s.get("hyp_graphemes", 0),
            s.get("char_errors", 0),
            s.get("char_substitutions", 0),
            s.get("char_deletions", 0),
            s.get("char_insertions", 0),
            s.get("critical_expected", 0),
            s.get("critical_matched", 0),
            s.get("critical_changed", 0),
            s.get("critical_missing", 0),
            s.get("critical_extra", 0),
            s.get("critical_match_rate") if s.get("critical_match_rate") is not None else "",
            s.get("reference", ""),
            s.get("hypothesis", ""),
            s.get("error_message") or ""
        ])

    return output.getvalue()


def generate_benchmark_aggregate_csv(batch_results: dict) -> str:
    """Generate aggregate benchmark summary metrics in CSV format."""
    summary = batch_results.get("summary", {})
    agg = batch_results.get("aggregate", {})

    output = io.StringIO()
    writer = csv.writer(output)

    headers = ["metric", "value", "unit", "description"]
    writer.writerow(headers)

    rows = [
        ["total_samples", summary.get("total_samples", 0), "count", "Total samples submitted for benchmark"],
        ["successful_samples", summary.get("successful_samples", 0), "count", "Samples transcribed and evaluated successfully"],
        ["failed_samples", summary.get("failed_samples", 0), "count", "Samples that encountered API or processing failures"],
        ["skipped_samples", summary.get("skipped_samples", 0), "count", "Samples skipped due to invalid audio or transcript"],
        ["benchmark_success_rate", summary.get("benchmark_success_rate", 0.0), "%", "Percentage of successful sample evaluations"],
        ["aggregate_wer", agg.get("aggregate_wer") if agg.get("aggregate_wer") is not None else "", "%", "Global Word Error Rate (total word errors / total reference words)"],
        ["total_ref_words", agg.get("total_ref_words", 0), "words", "Total reference words in successful samples"],
        ["total_hyp_words", agg.get("total_hyp_words", 0), "words", "Total hypothesis words in successful samples"],
        ["total_word_errors", agg.get("total_word_errors", 0), "errors", "Sum of word substitutions, deletions, and insertions"],
        ["word_substitutions", agg.get("substitutions", 0), "errors", "Word substitutions"],
        ["word_deletions", agg.get("deletions", 0), "errors", "Word deletions"],
        ["word_insertions", agg.get("insertions", 0), "errors", "Word insertions"],
        ["aggregate_cer", agg.get("aggregate_cer") if agg.get("aggregate_cer") is not None else "", "%", "Global Character Error Rate (total char errors / total reference graphemes)"],
        ["total_ref_graphemes", agg.get("total_ref_graphemes", 0), "graphemes", "Total reference grapheme clusters in successful samples"],
        ["total_hyp_graphemes", agg.get("total_hyp_graphemes", 0), "graphemes", "Total hypothesis grapheme clusters in successful samples"],
        ["total_char_errors", agg.get("total_char_errors", 0), "errors", "Sum of char substitutions, deletions, and insertions"],
        ["char_substitutions", agg.get("char_substitutions", 0), "errors", "Character substitutions"],
        ["char_deletions", agg.get("char_deletions", 0), "errors", "Character deletions"],
        ["char_insertions", agg.get("char_insertions", 0), "errors", "Character insertions"],
        ["aggregate_critical_match_rate", agg.get("aggregate_critical_match_rate") if agg.get("aggregate_critical_match_rate") is not None else "", "%", "Global Critical Entity Match Rate"],
        ["total_critical_expected", agg.get("total_critical_expected", 0), "entities", "Total expected critical entities across successful samples"],
        ["total_critical_matched", agg.get("total_critical_matched", 0), "entities", "Total matched critical entities across successful samples"],
        ["total_critical_changed", agg.get("total_critical_changed", 0), "entities", "Total changed critical entities"],
        ["total_critical_missing", agg.get("total_critical_missing", 0), "entities", "Total missing critical entities"],
        ["total_critical_extra", agg.get("total_critical_extra", 0), "entities", "Total extra critical entities"],
        ["avg_latency_sec", agg.get("avg_latency_sec", 0.0), "seconds", "Average API latency per successful sample"]
    ]

    for r in rows:
        writer.writerow(r)

    return output.getvalue()


# -----------------------------------------------------------------------------
# State Management Initialization
# -----------------------------------------------------------------------------
if "eval_history" not in st.session_state:
    st.session_state["eval_history"] = []

if "api_status" not in st.session_state:
    st.session_state["api_status"] = "Ready (Unverified Live)"

if "compare_results" not in st.session_state:
    st.session_state["compare_results"] = None

if "audio_quality" not in st.session_state:
    st.session_state["audio_quality"] = None

if "benchmark_results" not in st.session_state:
    st.session_state["benchmark_results"] = None


# -----------------------------------------------------------------------------
# APPLICATION INTERFACE
# -----------------------------------------------------------------------------

# Title for testing compatibility
st.title("🎙️ NADHAM QA")
st.subheader("Kerala-first. India-ready.")

# Branded Header Component
st.markdown("""
<div class="brand-header">
    <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
        <div>
            <h2 style="color: #F8FAFC; margin: 0; font-size: 26px; font-weight: 700; letter-spacing: -0.5px;">
                🎙️ NADHAM QA Analytics Platform
            </h2>
            <p class="brand-desc">
                High-Precision Indic Speech Recognition Evaluation & Benchmarking for Gnani Prisma STT
            </p>
        </div>
        <div>
            <span class="brand-tag">
                Prisma v2.5 Ready
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

language_codes = {
    "Malayalam": "ml-IN",
    "English": "en-IN",
    "Hindi": "hi-IN"
}

# -----------------------------------------------------------------------------
# Configuration & Upload Section
# -----------------------------------------------------------------------------
tab_eval, tab_compare, tab_benchmark = st.tabs([
    "🎙️ Single Evaluation",
    "🔬 Clean vs. Noisy Comparison",
    "📊 Malayalam Benchmark & Reliability Evidence"
])

with tab_eval:
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.markdown("#### 🎧 Audio Input & Language")
        language = st.selectbox(
            "Select recording language",
            ["Malayalam", "English", "Hindi"],
            index=0,
            help="Target language for speech recognition transcription."
        )

        audio = st.file_uploader(
            "Upload audio recording",
            type=["wav", "mp3", "ogg", "flac", "aac", "m4a"],
            help="Max size: 25 MB. Recommended duration: 10–30 seconds for initial testing."
        )

        if audio is not None:
            st.audio(audio)
            st.caption(f"📁 **File:** `{audio.name}` ({len(audio.getvalue()) / 1024:.1f} KB)")
        else:
            st.caption("Upload a speech recording in WAV, MP3, OGG, FLAC, AAC, or M4A format.")

    with col_right:
        st.markdown("#### 📝 Ground Truth Reference")
        reference = st.text_area(
            "Reference transcript",
            placeholder="Enter exactly what was spoken in the recording (Malayalam, English, or Hindi)...",
            height=145,
            help="Ground-truth text against which the speech engine's transcript is benchmarked."
        )
        st.caption("ℹ️ Punctuation, currency symbols, and zero-width characters will be canonically normalized.")

    # -----------------------------------------------------------------------------
    # System Status Indicators
    # -----------------------------------------------------------------------------
    st.markdown("#### ⚙️ System Status")
    stat1, stat2, stat3 = st.columns(3)

    with stat1:
        st.markdown("""
        <div class="status-card">
            <span class="status-card-label">ASR Engine</span>
            <span class="status-card-val">Gnani Prisma v2.5</span>
        </div>
        """, unsafe_allow_html=True)

    with stat2:
        st.markdown(f"""
        <div class="status-card">
            <span class="status-card-label">Active Language Code</span>
            <span class="status-card-val">{language} ({language_codes[language]})</span>
        </div>
        """, unsafe_allow_html=True)

    with stat3:
        current_status = st.session_state.get("api_status", "Ready (Unverified Live)")
        if "Verified" in current_status:
            badge_style = "color: #34D399;"
            dot = "●"
        elif "504" in current_status or "Latency" in current_status:
            badge_style = "color: #F87171;"
            dot = "▲"
        else:
            badge_style = "color: #38BDF8;"
            dot = "●"

        st.markdown(f"""
        <div class="status-card">
            <span class="status-card-label">API Gateway Status</span>
            <span class="status-card-val" style="{badge_style}">{dot} {current_status}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------------
    # Action Button: Run Evaluation
    # (Must be the primary button on the page for AppTest compatibility)
    # -----------------------------------------------------------------------------
    run_clicked = st.button("🚀 Run NADHAM QA Test", type="primary", use_container_width=True)

    if run_clicked:
        # Clear previous run results to avoid stale displays on new run or error
        for key in ["transcript", "reference", "request_id", "language", "audio_name"]:
            st.session_state.pop(key, None)

        if audio is None:
            st.error("Please upload an audio file.")

        elif len(audio.getvalue()) == 0:
            st.error("The uploaded audio file is empty (0 bytes). Please upload a valid audio recording.")

        elif len(audio.getvalue()) > MAX_AUDIO_BYTES:
            st.error(f"Audio file exceeds the maximum allowed size of {MAX_AUDIO_BYTES // (1024 * 1024)} MB.")

        elif not reference.strip():
            st.error("Please enter the reference transcript.")

        elif not words(reference):
            st.error("Reference transcript contains only punctuation or no valid words. Please enter meaningful text.")

        else:
            try:
                with st.spinner("Gnani Prisma is analysing your speech..."):
                    result = call_gnani(
                        audio,
                        language_codes[language]
                    )

                transcript = result.get("transcript", "")

                st.session_state["transcript"] = transcript
                st.session_state["reference"] = reference
                st.session_state["request_id"] = result.get(
                    "request_id", "Not available"
                )
                st.session_state["language"] = language
                st.session_state["audio_name"] = audio.name
                st.session_state["api_status"] = "Online (Verified 200)"

                # Pre-compute metrics to record history
                computed_metrics = evaluate(reference, transcript)
                cer_metrics = evaluate_cer(reference, transcript)
                if computed_metrics:
                    st.session_state["eval_history"].append({
                        "wer": computed_metrics["wer"],
                        "cer": cer_metrics["cer"] if cer_metrics else None,
                        "errors": computed_metrics["errors"],
                        "char_errors": cer_metrics["errors"] if cer_metrics else None,
                        "ref_words": computed_metrics["reference_words"],
                        "ref_chars": cer_metrics["reference_chars"] if cer_metrics else None,
                        "correct": sum(1 for op in computed_metrics["operations"] if op[0] == "Correct"),
                        "substitutions": sum(1 for op in computed_metrics["operations"] if op[0] == "Substitution"),
                        "deletions": sum(1 for op in computed_metrics["operations"] if op[0] == "Deletion"),
                        "insertions": sum(1 for op in computed_metrics["operations"] if op[0] == "Insertion"),
                        "language": language,
                        "timestamp": datetime.now()
                    })

            except Exception as error:
                err_str = str(error)
                if "504" in err_str or "gateway" in err_str.lower():
                    st.session_state["api_status"] = "Gateway Latency (504 Timeout)"
                else:
                    st.session_state["api_status"] = "API Error"
                st.error(f"Test failed: {error}")


    # -----------------------------------------------------------------------------
    # Session Aggregate Metric Cards
    # (Supported strictly by actual session evaluation data)
    # -----------------------------------------------------------------------------
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 📊 Session Performance Overview")

    total_evals = len(st.session_state["eval_history"])
    if total_evals > 0:
        latest_item = st.session_state["eval_history"][-1]
        latest_wer_val = f"{latest_item['wer']:.2f}%"
        latest_cer_val = f"{latest_item['cer']:.2f}%" if latest_item.get("cer") is not None else "—"
        avg_wer_val = f"{sum(e['wer'] for e in st.session_state['eval_history']) / total_evals:.2f}%"
        total_evals_val = str(total_evals)
    else:
        latest_wer_val = "—"
        latest_cer_val = "—"
        avg_wer_val = "—"
        total_evals_val = "0"

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Latest WER", latest_wer_val, help="Word Error Rate of the most recent evaluation in this session.")
    m_col2.metric("Latest CER", latest_cer_val, help="Character Error Rate (Unicode grapheme clusters) of the most recent evaluation.")
    m_col3.metric("Average WER", avg_wer_val, help="Cumulative average WER across all runs in current session.")
    m_col4.metric("Total Evaluations", total_evals_val, help="Number of successful evaluations completed in this session.")

    st.divider()

    # -----------------------------------------------------------------------------
    # Evaluation Results Section
    # -----------------------------------------------------------------------------
    if "transcript" in st.session_state:

        st.header("📊 Evaluation Results")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Reference Transcript**")
            st.info(st.session_state["reference"])

        with col2:
            st.markdown("**Gnani Prisma Transcript**")
            st.success(st.session_state["transcript"])

        metrics = evaluate(
            st.session_state["reference"],
            st.session_state["transcript"]
        )
        cer_metrics = evaluate_cer(
            st.session_state["reference"],
            st.session_state["transcript"]
        )

        if metrics:

            st.markdown("### Accuracy Metrics")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Word Error Rate (WER)",
                f"{metrics['wer']:.2f}%",
                help="Word-level error rate: (Substitutions + Deletions + Insertions) / Reference Words * 100"
            )

            c2.metric(
                "Character Error Rate (CER)",
                f"{cer_metrics['cer']:.2f}%" if cer_metrics else "N/A",
                help="Character-level error rate: (Substitutions + Deletions + Insertions) / Reference Graphemes * 100"
            )

            c3.metric(
                "Word Errors",
                f"{metrics['errors']} / {metrics['reference_words']}",
                help="Total word errors vs reference word count"
            )

            c4.metric(
                "Character Errors",
                f"{cer_metrics['errors']} / {cer_metrics['reference_chars']}" if cer_metrics else "N/A",
                help="Total character edit errors vs reference grapheme cluster count"
            )

            st.caption(
                "ℹ️ **Linguistic Note:** WER evaluates complete word tokens. CER evaluates Unicode UAX #29 grapheme clusters "
                "(base consonants with attached matras, viramas, and chillus; whitespace excluded), providing fine-grained accuracy "
                "for agglutinative Indic languages. Metrics are calculated strictly against the supplied reference transcript."
            )

            # Operations Breakdown Indicators
            correct_count = sum(1 for op in metrics["operations"] if op[0] == "Correct")
            sub_count = sum(1 for op in metrics["operations"] if op[0] == "Substitution")
            del_count = sum(1 for op in metrics["operations"] if op[0] == "Deletion")
            ins_count = sum(1 for op in metrics["operations"] if op[0] == "Insertion")

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            pill_col1, pill_col2, pill_col3, pill_col4 = st.columns(4)
            with pill_col1:
                st.markdown(f"<div class='pill-correct'>🟢 Correct: <b>{correct_count}</b></div>", unsafe_allow_html=True)
            with pill_col2:
                st.markdown(f"<div class='pill-sub'>🟠 Substitutions: <b>{sub_count}</b></div>", unsafe_allow_html=True)
            with pill_col3:
                st.markdown(f"<div class='pill-del'>🔴 Deletions: <b>{del_count}</b></div>", unsafe_allow_html=True)
            with pill_col4:
                st.markdown(f"<div class='pill-ins'>🟣 Insertions: <b>{ins_count}</b></div>", unsafe_allow_html=True)
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            st.markdown("### Word-Level Error Analysis")

            rows = []
            for status, reference_word, predicted_word in metrics["operations"]:
                rows.append({
                    "Status": status,
                    "Reference Word": reference_word,
                    "Recognized Word": predicted_word
                })

            st.dataframe(rows, use_container_width=True)

            st.caption(
                "Correct = matched | Substitution = incorrect word | "
                "Deletion = missing word | Insertion = extra word"
            )

            # ---------------------------------------------------------------------
            # Critical Information Analysis (Rule-Based)
            # ---------------------------------------------------------------------
            crit_results = compare_critical_entities(
                st.session_state["reference"],
                st.session_state["transcript"]
            )

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("### 🎯 Critical Information Analysis")
            st.caption(
                "Rule-based detection of mission-critical domain entities: Currency, Dates, Times, "
                "Phone Numbers, Numbers, Negations, and Named Entities. Requires human verification for edge-case contexts."
            )

            crit_c1, crit_c2, crit_c3, crit_c4, crit_c5 = st.columns(5)
            crit_c1.metric("Critical Entities", crit_results["total_items"])
            crit_c2.metric("Exact Matches", crit_results["matching_items"])
            crit_c3.metric("Changed Values", crit_results["changed_items"])
            crit_c4.metric("Missing Entities", crit_results["missing_items"])
            crit_c5.metric("Extra (Spurious)", crit_results["extra_items"])

            if crit_results["details"]:
                st.dataframe(crit_results["details"], use_container_width=True)
            else:
                st.info("No critical entities (numbers, dates, currency, phone numbers, negation) detected in reference or hypothesis.")

            # Word-level text table for the TXT report
            table_lines = [
                f"{'#':<4} | {'Status':<14} | {'Reference Word':<25} | {'Recognized Word':<25}",
                "-" * 75
            ]
            for idx, (status, ref_w, hyp_w) in enumerate(metrics["operations"], start=1):
                table_lines.append(
                    f"{idx:<4} | {status:<14} | {ref_w:<25} | {hyp_w:<25}"
                )
            ops_table_text = "\n".join(table_lines)

            crit_table_lines = [
                f"{'Category':<15} | {'Status':<10} | {'Reference Value':<22} | {'Recognized Value':<22} | {'Explanation'}",
                "-" * 95
            ]
            for row in crit_results["details"]:
                crit_table_lines.append(
                    f"{row['Category']:<15} | {row['Status']:<10} | {row['Reference Value']:<22} | {row['Recognized Value']:<22} | {row['Explanation']}"
                )
            crit_table_text = "\n".join(crit_table_lines) if crit_results["details"] else "No critical entities detected."

            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            audio_name = st.session_state.get("audio_name", "audio_recording")

            cer_block = ""
            if cer_metrics:
                cer_block = f"""
    Character Error Rate (CER):   {cer_metrics['cer']:.2f}%
    Total Character Errors:       {cer_metrics['errors']}
    Reference Grapheme Count:     {cer_metrics['reference_chars']}
    Recognized Grapheme Count:    {cer_metrics['recognized_chars']}
    Character Substitutions:      {cer_metrics['substitutions']}
    Character Deletions:          {cer_metrics['deletions']}
    Character Insertions:         {cer_metrics['insertions']}
    (CER Formula: [Char Substitutions + Deletions + Insertions] / Reference Grapheme Count * 100)
    (CER Policy: Unicode UAX #29 grapheme clusters; whitespace excluded to isolate acoustic transcription accuracy)
    """

            aq = st.session_state.get("audio_quality")
            audio_quality_block = ""
            if aq and aq.get("supported"):
                audio_quality_block = f"""
ACOUSTIC SIGNAL QUALITY:
--------------------------------------------------------------------------------
Duration:                     {aq['duration_s']}s
Sample Rate:                  {aq['sample_rate']} Hz
Channels:                     {aq['channels_desc']} ({aq['channels']} ch)
RMS Energy:                   {aq['rms_dbfs']} dBFS
Peak Amplitude:               {aq['peak_dbfs']} dBFS
Clipping Percentage:          {aq['clipping_pct']}%
Silence Percentage:           {aq['silence_pct']}%
"""
            st.session_state['audio_quality_report_block'] = audio_quality_block

            crit_block = f"""
    CRITICAL INFORMATION ANALYSIS (RULE-BASED):
    --------------------------------------------------------------------------------
    Reference Critical Items:     {crit_results['total_items']}
    Matching Items:               {crit_results['matching_items']}
    Changed Items:                {crit_results['changed_items']}
    Missing Items:                {crit_results['missing_items']}
    Extra (Spurious) Items:       {crit_results['extra_items']}
    Critical Entity Accuracy:     {crit_results['accuracy']:.2f}%

    {crit_table_text}
    (Note: Rule-based heuristic extraction for domain verification; verify edge-case names manually)
    """

            report = f"""================================================================================
    NADHAM QA - SPEECH RECOGNITION EVALUATION REPORT
    ================================================================================
    Timestamp:          {timestamp_str}
    Audio File:         {audio_name}
    Language:           {st.session_state['language']}
    Gnani Request ID:   {st.session_state['request_id']}
    Model:              Gnani Prisma v2.5

    ACCURACY METRICS:
    --------------------------------------------------------------------------------
    Word Error Rate:        {metrics['wer']:.2f}%
    Total Word Errors:      {metrics['errors']}
    Reference Word Count:   {metrics['reference_words']}
    Recognized Word Count:  {metrics['recognized_words']}
    {cer_block}
    {crit_block}
    TRANSCRIPTS:
    --------------------------------------------------------------------------------
    Reference Transcript:
    {st.session_state['reference']}

    Gnani Transcript:
    {st.session_state['transcript']}

    WORD-LEVEL ERROR BREAKDOWN:
    --------------------------------------------------------------------------------
    {ops_table_text}
    ================================================================================
    Generated by NADHAM QA Platform | Kerala-first. India-ready.
    """

            # Generate CSV export
            df_export = pd.DataFrame(rows)
            csv_data = df_export.to_csv(index=False).encode("utf-8")

            # Generate Critical Entities CSV export
            df_crit_export = pd.DataFrame(crit_results["details"]) if crit_results["details"] else pd.DataFrame(columns=["Category", "Reference Value", "Recognized Value", "Status", "Explanation"])
            csv_crit_data = df_crit_export.to_csv(index=False).encode("utf-8")

            st.markdown("### 📥 Diagnostic Reports & Export")
            col_d1, col_d2, col_d3 = st.columns(3)

            with col_d1:
                st.download_button(
                    "📥 Download Test Report (.txt)",
                    report,
                    file_name=f"NADHAM_QA_Report_{audio_name}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with col_d2:
                st.download_button(
                    "📊 Download Error Analysis (.csv)",
                    csv_data,
                    file_name=f"NADHAM_QA_Analysis_{audio_name}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col_d3:
                st.download_button(
                    "🎯 Download Critical Entities (.csv)",
                    csv_crit_data,
                    file_name=f"NADHAM_QA_Critical_{audio_name}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # -----------------------------------------------------------------------------
    # About NADHAM QA Section (Expandable)
    # -----------------------------------------------------------------------------

with tab_compare:
    st.markdown("### 🔬 Clean vs. Noisy Speech Recognition Benchmark")
    st.caption(
        "Evaluate speech recognition degradation, character-level sensitivity, critical entity retention, "
        "and acoustic signal properties under background noise conditions."
    )

    st.warning(
        "⚠️ **Credit & API Notice:** Clean vs. Noisy comparison evaluates two recordings against a shared "
        "reference transcript. This initiates two independent requests to Gnani Prisma STT and consumes "
        "2 API transactions. Analysis begins strictly when you click the comparison button below."
    )

    comp_language = st.selectbox(
        "Select recording language",
        ["Malayalam", "English", "Hindi"],
        index=0,
        key="comp_lang_select",
        help="Target language for clean and noisy transcription."
    )

    col_clean, col_noisy = st.columns(2, gap="medium")

    with col_clean:
        st.markdown("#### 🟢 Clean Audio Recording")
        clean_audio = st.file_uploader(
            "Upload clean recording",
            type=["wav", "mp3", "ogg", "flac", "aac", "m4a"],
            key="clean_audio_input",
            help="High-quality recording with minimal background noise."
        )
        clean_q = None
        if clean_audio is not None:
            st.audio(clean_audio)
            st.caption(f"📁 `{clean_audio.name}` ({len(clean_audio.getvalue()) / 1024:.1f} KB)")
            clean_q = analyze_audio_quality(clean_audio.getvalue(), filename=clean_audio.name)
            if clean_q["supported"]:
                st.markdown(f"""
                <div class="audio-card">
                    <div style="font-size: 12px; font-weight: 600; color: #34D399; margin-bottom: 6px;">
                        🔊 Clean Acoustic Signal ({clean_q['channels_desc']}, {clean_q['sample_rate']} Hz)
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px; color: #94A3B8;">
                        <div>⏱️ Duration: <b style="color: #F8FAFC;">{clean_q['duration_s']}s</b></div>
                        <div>📊 RMS Energy: <b style="color: #F8FAFC;">{clean_q['rms_dbfs']} dBFS</b></div>
                        <div>⚡ Peak Level: <b style="color: #F8FAFC;">{clean_q['peak_dbfs']} dBFS</b></div>
                        <div>🔇 Silence: <b style="color: #F8FAFC;">{clean_q['silence_pct']}%</b></div>
                        <div>⚠️ Clipping: <b style="color: {'#F87171' if clean_q['clipping_pct'] > 0 else '#34D399'};">{clean_q['clipping_pct']}%</b></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption(f"ℹ️ {clean_q['error']}")

    with col_noisy:
        st.markdown("#### 🔴 Noisy Audio Recording")
        noisy_audio = st.file_uploader(
            "Upload noisy recording",
            type=["wav", "mp3", "ogg", "flac", "aac", "m4a"],
            key="noisy_audio_input",
            help="Same speech recorded with background noise, babble, or reverberation."
        )
        noisy_q = None
        if noisy_audio is not None:
            st.audio(noisy_audio)
            st.caption(f"📁 `{noisy_audio.name}` ({len(noisy_audio.getvalue()) / 1024:.1f} KB)")
            noisy_q = analyze_audio_quality(noisy_audio.getvalue(), filename=noisy_audio.name)
            if noisy_q["supported"]:
                st.markdown(f"""
                <div class="audio-card">
                    <div style="font-size: 12px; font-weight: 600; color: #F87171; margin-bottom: 6px;">
                        🔊 Noisy Acoustic Signal ({noisy_q['channels_desc']}, {noisy_q['sample_rate']} Hz)
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px; color: #94A3B8;">
                        <div>⏱️ Duration: <b style="color: #F8FAFC;">{noisy_q['duration_s']}s</b></div>
                        <div>📊 RMS Energy: <b style="color: #F8FAFC;">{noisy_q['rms_dbfs']} dBFS</b></div>
                        <div>⚡ Peak Level: <b style="color: #F8FAFC;">{noisy_q['peak_dbfs']} dBFS</b></div>
                        <div>🔇 Silence: <b style="color: #F8FAFC;">{noisy_q['silence_pct']}%</b></div>
                        <div>⚠️ Clipping: <b style="color: {'#F87171' if noisy_q['clipping_pct'] > 0 else '#34D399'};">{noisy_q['clipping_pct']}%</b></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.caption(f"ℹ️ {noisy_q['error']}")

    st.markdown("#### 📝 Shared Ground Truth Reference")
    comp_reference = st.text_area(
        "Ground truth reference transcript",
        placeholder="Enter the exact spoken reference common to both recordings...",
        height=100,
        key="comp_reference_input",
        help="Ground-truth reference against which both clean and noisy transcripts are evaluated."
    )

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    run_compare_clicked = st.button("🔬 Run Clean vs Noisy Comparison", type="secondary", use_container_width=True, key="run_compare_button")

    if run_compare_clicked:
        # Clear previous comparison results to prevent stale displays on error or new run
        st.session_state["compare_results"] = None

        if clean_audio is None:
            st.error("Please upload the clean audio recording.")
        elif noisy_audio is None:
            st.error("Please upload the noisy audio recording.")
        elif len(clean_audio.getvalue()) == 0:
            st.error("The clean audio file is empty (0 bytes). Please upload a valid recording.")
        elif len(noisy_audio.getvalue()) == 0:
            st.error("The noisy audio file is empty (0 bytes). Please upload a valid recording.")
        elif len(clean_audio.getvalue()) > MAX_AUDIO_BYTES:
            st.error(f"Clean audio file exceeds {MAX_AUDIO_BYTES // (1024*1024)} MB limit.")
        elif len(noisy_audio.getvalue()) > MAX_AUDIO_BYTES:
            st.error(f"Noisy audio file exceeds {MAX_AUDIO_BYTES // (1024*1024)} MB limit.")
        elif not comp_reference.strip():
            st.error("Please enter the shared reference transcript.")
        elif not words(comp_reference):
            st.error("Reference transcript contains only punctuation or no valid words. Please enter meaningful text.")
        else:
            try:
                with st.spinner("Transcribing clean recording with Gnani Prisma..."):
                    clean_res = call_gnani(clean_audio, language_codes[comp_language])
                with st.spinner("Transcribing noisy recording with Gnani Prisma..."):
                    noisy_res = call_gnani(noisy_audio, language_codes[comp_language])

                clean_trans = clean_res.get("transcript", "")
                noisy_trans = noisy_res.get("transcript", "")
                c_q = analyze_audio_quality(clean_audio.getvalue(), filename=clean_audio.name)
                n_q = analyze_audio_quality(noisy_audio.getvalue(), filename=noisy_audio.name)

                comp_data = compare_clean_noisy(
                    comp_reference,
                    clean_trans,
                    noisy_trans,
                    c_q,
                    n_q
                )
                comp_data["clean_transcript"] = clean_trans
                comp_data["noisy_transcript"] = noisy_trans

                st.session_state["compare_results"] = {
                    "clean_audio_name": clean_audio.name,
                    "noisy_audio_name": noisy_audio.name,
                    "clean_transcript": clean_trans,
                    "noisy_transcript": noisy_trans,
                    "clean_request_id": clean_res.get("request_id", "Not available"),
                    "noisy_request_id": noisy_res.get("request_id", "Not available"),
                    "reference": comp_reference,
                    "language": comp_language,
                    "clean_quality": c_q,
                    "noisy_quality": n_q,
                    "comparison": comp_data
                }
            except Exception as e:
                st.error(f"Comparison benchmark failed: {e}")

    # Display comparison results if available
    comp_state = st.session_state.get("compare_results")
    if comp_state:
        cmp = comp_state["comparison"]
        st.divider()
        st.markdown("### 📊 Benchmark Comparison Results")

        # Interpretation banner
        if cmp["better_recording"] == "clean":
            st.success(f"🟢 **{cmp['interpretation']}**")
        elif cmp["better_recording"] == "noisy":
            st.info(f"🔵 **{cmp['interpretation']}**")
        else:
            st.info(f"⚪ **{cmp['interpretation']}**")

        # Top 4 Metric Comparison Cards
        top1, top2, top3, top4 = st.columns(4)
        top1.metric(
            "Word Error Rate (WER)",
            f"{cmp['clean_wer']:.2f}% vs {cmp['noisy_wer']:.2f}%",
            delta=f"{cmp['delta_wer']:+.2f}%",
            delta_color="inverse"
        )
        top2.metric(
            "Character Error Rate (CER)",
            f"{cmp['clean_cer']:.2f}% vs {cmp['noisy_cer']:.2f}%",
            delta=f"{cmp['delta_cer']:+.2f}%",
            delta_color="inverse"
        )
        top3.metric(
            "Total Word Errors",
            f"{cmp['clean_errors']} vs {cmp['noisy_errors']}",
            delta=f"{cmp['delta_errors']:+d}",
            delta_color="inverse"
        )
        top4.metric(
            "Critical Entity Accuracy",
            f"{cmp['clean_crit']['accuracy']:.1f}% vs {cmp['noisy_crit']['accuracy']:.1f}%",
            delta=f"{cmp['noisy_crit']['accuracy'] - cmp['clean_crit']['accuracy']:+.1f}%",
            delta_color="normal"
        )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        # Side-by-side transcripts
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(f"**Clean Recording Transcript** (`{comp_state['clean_audio_name']}`)")
            st.success(comp_state["clean_transcript"] or "(Empty transcript returned)")
            st.caption(f"Request ID: `{comp_state['clean_request_id']}`")
        with t_col2:
            st.markdown(f"**Noisy Recording Transcript** (`{comp_state['noisy_audio_name']}`)")
            st.info(comp_state["noisy_transcript"] or "(Empty transcript returned)")
            st.caption(f"Request ID: `{comp_state['noisy_request_id']}`")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📋 Detailed Comparison Table")
        st.dataframe(cmp["table_rows"], use_container_width=True)

        # Downloads
        comp_txt_report = generate_comparison_txt_report(
            cmp,
            comp_state["reference"],
            comp_state["clean_audio_name"],
            comp_state["noisy_audio_name"],
            comp_state["language"],
            comp_state["clean_request_id"],
            comp_state["noisy_request_id"]
        )
        comp_csv_data = generate_comparison_csv(cmp)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        st.markdown("#### 📥 Download Comparison Reports")
        dc1, dc2 = st.columns(2)
        with dc1:
            st.download_button(
                "📥 Download Comparison Report (.txt)",
                comp_txt_report,
                file_name=f"NADHAM_QA_Comparison_{comp_state['clean_audio_name']}_vs_{comp_state['noisy_audio_name']}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with dc2:
            st.download_button(
                "📊 Download Comparison Metrics (.csv)",
                comp_csv_data,
                file_name=f"NADHAM_QA_Comparison_{comp_state['clean_audio_name']}_vs_{comp_state['noisy_audio_name']}.csv",
                mime="text/csv",
                use_container_width=True
            )


with tab_benchmark:
    st.markdown("### 📊 Malayalam Speech Recognition Benchmark & Reliability Evidence")
    st.caption(
        "Standardized batch evaluation across genuine Malayalam speech recordings using Gnani Prisma STT."
    )

    dataset_info = discover_benchmark_dataset()

    # Section A: Dataset Inventory Cards
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.metric("Discovered Samples", dataset_info["total_discovered"])
    with b_col2:
        st.metric("Verified Valid", dataset_info["valid_count"])
    with b_col3:
        st.metric("Acoustic Condition", f"Normal / Clean ({dataset_info['normal_condition_count']})")
    with b_col4:
        st.metric("Paired Noise Status", "Unavailable (0 pairs)")

    # Section B: Clean/Noisy Transparency Callout
    st.info(
        "ℹ️ **Paired Clean vs. Noisy Benchmark Status:** The current benchmark dataset contains 5 genuine "
        "Malayalam speech recordings under normal/clean acoustic conditions. Genuine paired clean-versus-noisy "
        "recordings are not present in this dataset. NADHAM QA rigorously evaluates all available samples "
        "without fabricating synthetic noise or simulating unrecorded conditions."
    )

    # Section C: Benchmark Controls
    st.markdown("#### ⚙️ Benchmark Execution Controls")
    valid_sample_ids = [s["sample_id"] for s in dataset_info["samples"] if s["status"] == "valid"]
    selected_sample_ids = st.multiselect(
        "Select Benchmark Samples to Evaluate",
        options=valid_sample_ids,
        default=valid_sample_ids,
        help="Select which Malayalam audio samples to include in the benchmark batch evaluation run."
    )
    num_selected = len(selected_sample_ids)

    st.warning(
        f"⚠️ **Credit & API Notice:** Executing this benchmark will initiate **{num_selected}** live API request(s) "
        f"to Gnani Prisma STT and consume **{num_selected}** API transactions. Analysis begins strictly when you click the button below."
    )

    run_benchmark_btn = st.button(
        "🚀 Execute Malayalam Benchmark",
        type="primary",
        use_container_width=True,
        disabled=(num_selected == 0)
    )

    # Section D: Execution Logic
    if run_benchmark_btn:
        st.session_state["benchmark_results"] = None
        samples_to_run = [s for s in dataset_info["samples"] if s["sample_id"] in selected_sample_ids]

        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def batch_progress(current, total, sid):
            frac = current / total if total > 0 else 1.0
            progress_bar.progress(frac)
            if current < total:
                status_text.markdown(f"**Evaluating sample {current + 1} of {total}:** `{sid}`...")
            else:
                status_text.markdown("**Batch evaluation completed!** Processing aggregate metrics...")

        try:
            with st.spinner("Executing Malayalam benchmark evaluation across selected samples..."):
                batch_res = evaluate_benchmark_batch(
                    samples_to_run,
                    progress_callback=batch_progress,
                    api_caller=call_gnani,
                    language="Malayalam"
                )
                st.session_state["benchmark_results"] = batch_res
                status_text.empty()
                progress_bar.empty()
                st.success(
                    f"✅ Benchmark run completed: {batch_res['summary']['successful_samples']}/{batch_res['summary']['total_samples']} "
                    f"samples evaluated successfully."
                )
        except Exception as e:
            st.error(f"Benchmark batch evaluation encountered an unexpected error: {e}")

    # Section E: Results Dashboard
    if st.session_state.get("benchmark_results"):
        bench = st.session_state["benchmark_results"]
        agg = bench.get("aggregate", {})
        summ = bench.get("summary", {})
        s_results = bench.get("sample_results", [])

        st.markdown("### 📈 Aggregate Benchmark Metrics")

        agg_col1, agg_col2, agg_col3, agg_col4 = st.columns(4)
        with agg_col1:
            wer_display = f"{agg.get('aggregate_wer')}%" if agg.get('aggregate_wer') is not None else "N/A"
            st.metric("Aggregate WER", wer_display, help="Total word errors divided by total reference words across successful samples")
        with agg_col2:
            cer_display = f"{agg.get('aggregate_cer')}%" if agg.get('aggregate_cer') is not None else "N/A"
            st.metric("Aggregate CER", cer_display, help="Total character errors divided by total reference graphemes across successful samples")
        with agg_col3:
            st.metric("Benchmark Success Rate", f"{summ.get('benchmark_success_rate', 0.0)}%", help="Percentage of samples transcribed successfully")
        with agg_col4:
            crit_disp = f"{agg.get('aggregate_critical_match_rate')}%" if agg.get('aggregate_critical_match_rate') is not None else "N/A"
            st.metric("Critical Entity Match", crit_disp, help="Overall critical entity retention rate across successful samples")

        st.markdown("#### 🔬 Aggregate Error Breakdown")
        err_col1, err_col2 = st.columns(2)
        with err_col1:
            st.markdown(
                f"""
                <div style="background-color: var(--card-bg, #ffffff); padding: 16px; border-radius: 8px; border: 1px solid #e0e0e0;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Word-Level Statistics</div>
                    <div>Reference Words: <b>{agg.get('total_ref_words', 0)}</b></div>
                    <div>Hypothesis Words: <b>{agg.get('total_hyp_words', 0)}</b></div>
                    <div>Total Word Errors: <b>{agg.get('total_word_errors', 0)}</b></div>
                    <div style="margin-top: 4px; font-size: 0.9em; color: #555;">
                        Substitutions: {agg.get('substitutions', 0)} | Deletions: {agg.get('deletions', 0)} | Insertions: {agg.get('insertions', 0)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with err_col2:
            st.markdown(
                f"""
                <div style="background-color: var(--card-bg, #ffffff); padding: 16px; border-radius: 8px; border: 1px solid #e0e0e0;">
                    <div style="font-weight: 600; margin-bottom: 8px;">Character-Level Statistics (Grapheme Clusters)</div>
                    <div>Reference Graphemes: <b>{agg.get('total_ref_graphemes', 0)}</b></div>
                    <div>Hypothesis Graphemes: <b>{agg.get('total_hyp_graphemes', 0)}</b></div>
                    <div>Total Character Errors: <b>{agg.get('total_char_errors', 0)}</b></div>
                    <div style="margin-top: 4px; font-size: 0.9em; color: #555;">
                        Substitutions: {agg.get('char_substitutions', 0)} | Deletions: {agg.get('char_deletions', 0)} | Insertions: {agg.get('char_insertions', 0)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📋 Sample-Level Evaluation Table")

        df_rows = []
        for s in s_results:
            df_rows.append({
                "Sample ID": s.get("sample_id"),
                "Status": s.get("status"),
                "WER (%)": f"{s.get('wer')}%" if s.get('wer') is not None else "N/A",
                "CER (%)": f"{s.get('cer')}%" if s.get('cer') is not None else "N/A",
                "Crit Match (%)": f"{s.get('critical_match_rate')}%" if s.get('critical_match_rate') is not None else "N/A",
                "Ref Words": s.get("ref_words"),
                "Word Errors": s.get("word_errors"),
                "Ref Chars": s.get("ref_graphemes"),
                "Char Errors": s.get("char_errors"),
                "Latency (s)": f"{s.get('latency_sec', 0.0):.2f}",
                "Audio File": s.get("audio_filename")
            })
        if df_rows:
            st.dataframe(pd.DataFrame(df_rows), use_container_width=True)

        with st.expander("🔍 Inspect Individual Sample Details & Transcripts", expanded=False):
            for s in s_results:
                st.markdown(f"#### Sample `{s.get('sample_id')}` ({s.get('audio_filename')})")
                st.markdown(f"**Status:** {s.get('status')} | **Request ID:** `{s.get('request_id', 'N/A')}` | **Latency:** {s.get('latency_sec', 0.0):.2f}s")
                st.markdown("**Reference Transcript:**")
                st.info(s.get("reference", "—"))
                st.markdown("**Gnani Hypothesis Transcript:**")
                if s.get("status") == "Success":
                    st.success(s.get("hypothesis", "—"))
                else:
                    st.error(f"Evaluation Failed: {s.get('error_message')}")
                st.markdown(
                    f"WER: **{s.get('wer') if s.get('wer') is not None else 'N/A'}%** (S:{s.get('substitutions')}, D:{s.get('deletions')}, I:{s.get('insertions')}) | "
                    f"CER: **{s.get('cer') if s.get('cer') is not None else 'N/A'}%** (S:{s.get('char_substitutions')}, D:{s.get('char_deletions')}, I:{s.get('char_insertions')}) | "
                    f"Critical Match: **{s.get('critical_match_rate') if s.get('critical_match_rate') is not None else 'N/A'}%**"
                )
                st.divider()

        st.markdown("### 📥 Export Benchmark Evidence Reports")
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        with dl_col1:
            txt_report_data = generate_benchmark_summary_txt(bench, dataset_info)
            st.download_button(
                "📥 Benchmark Summary (TXT)",
                txt_report_data.encode("utf-8"),
                file_name=f"NADHAM_QA_Benchmark_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with dl_col2:
            sample_csv_data = generate_benchmark_sample_csv(bench)
            st.download_button(
                "📊 Sample-Level CSV",
                sample_csv_data.encode("utf-8"),
                file_name=f"NADHAM_QA_Benchmark_Samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col3:
            agg_csv_data = generate_benchmark_aggregate_csv(bench)
            st.download_button(
                "📈 Aggregate Metrics CSV",
                agg_csv_data.encode("utf-8"),
                file_name=f"NADHAM_QA_Benchmark_Aggregate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )


with st.expander("ℹ️ About NADHAM QA — Kerala-First Speech Intelligence", expanded=False):
    st.markdown("""
    ### 🎙️ The Kerala-First Speech Intelligence Mission
    **NADHAM QA** is an enterprise evaluation platform designed to benchmark Indic speech recognition models with true linguistic precision, specifically tailored for **Gnani Prisma STT (v2.5)**.

    #### 🌟 Why Malayalam Needs Specialized Evaluation:
    1. **Malayalam Chillu Ambiguity:** Modern Unicode represents chillu letters atomically (`ൺ`, `ൻ`, `ർ`, `ൽ`, `ൾ`, `ൿ`), whereas legacy keyboards generate decomposed consonant + virama (`്`) + Zero-Width Joiner (`ZWJ`). Standard NFC normalization fails to equate them; NADHAM QA canonicalizes them to prevent artificial error inflation.
    2. **Zero-Width Controls:** Zero-Width Spaces (`\\u200B`) and Joiners (`\\u200D`/`\\u200C`) that glue words together are handled cleanly.
    3. **Entity Preservation:** Standard punctuation filters destroy decimals (`3.14` → `314`) and dates (`15/08/1947` → `15081947`). NADHAM QA preserves numeric entities and normalizes currency symbols (`₹`, `$`).

    #### ⚙️ Evaluation Methodology:
    NADHAM QA implements the exact **Wagner-Fischer Dynamic Programming algorithm** to compute word-level and character-level edit distance:
    $$\\text{WER} = \\frac{\\text{Substitutions} + \\text{Deletions} + \\text{Insertions}}{\\text{Reference Word Count}} \\times 100\\%$$
    $$\\text{CER} = \\frac{\\text{Char Substitutions} + \\text{Char Deletions} + \\text{Char Insertions}}{\\text{Reference Grapheme Count}} \\times 100\\%$$

    *Note on CER Policy:* Character Error Rate is evaluated over Unicode UAX #29 extended grapheme clusters (base characters with attached matras, viramas, and chillus; whitespace excluded) strictly against the supplied reference transcript.

    #### 🛡️ Enterprise Safety Guardrails:
    - Client-side rejection of 0-byte (empty) audio files to safeguard API quotas.
    - 25 MB file size limit to prevent memory exhaustion (DoS).
    - Upstream HTML error sanitization (detecting Cloudflare 502/504 gateway timeouts without dumping raw markup).
    - Session state invalidation on each new test to eliminate stale UI metrics.
    """)

st.divider()

st.caption(
    "NADHAM QA | Powered by Gnani Prisma"
)
