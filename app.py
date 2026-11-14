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
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom Styling - Modern Dark Navy & Electric Purple/Cyan SaaS Dashboard Theme
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Google Fonts & Base Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Malayalam:wght@400;500;600;700&display=swap');

    /* Color Palette:
       Background: Deep navy (#080D20)
       Sidebar: Dark navy (#10162D)
       Cards: Slightly lighter navy (#151D38)
       Primary accent: Electric purple (#7545FF)
       Secondary accent: Cyan blue (#21B8FF)
       Success: Green (#28D98A)
       Main text: White (#F8FAFC)
       Secondary text: Soft grey (#94A3B8)
    */

    /* Global App Container */
    .stApp {
        background-color: #080D20 !important;
        color: #F8FAFC !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans Malayalam", sans-serif !important;
    }

    /* Streamlit Main View Padding */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
    }

    /* Fixed-Style Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #10162D !important;
        border-right: 1px solid rgba(117, 69, 255, 0.15) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    }

    section[data-testid="stSidebar"] div.block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* Sidebar Branding Box */
    .sidebar-brand-box {
        padding: 4px 0 16px 0;
    }
    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-icon-wrapper {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, rgba(117, 69, 255, 0.25) 0%, rgba(33, 184, 255, 0.15) 100%);
        border: 1px solid rgba(117, 69, 255, 0.4);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(117, 69, 255, 0.2);
    }
    .brand-title-wrap {
        display: flex;
        flex-direction: column;
    }
    .brand-title-text {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .brand-subtitle-text {
        color: #94A3B8;
        font-size: 11.5px;
        font-weight: 500;
        margin-top: 6px;
        letter-spacing: 0.2px;
    }
    .sidebar-sep {
        height: 1px;
        background: linear-gradient(90deg, rgba(117, 69, 255, 0.3) 0%, rgba(33, 184, 255, 0.1) 50%, transparent 100%);
        margin: 14px 0 18px 0;
    }
    .sidebar-nav-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    /* Sidebar Navigation Radio Items */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        gap: 6px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        background-color: transparent !important;
        border-radius: 8px !important;
        padding: 9px 12px !important;
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
        cursor: pointer !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background-color: rgba(117, 69, 255, 0.12) !important;
        color: #FFFFFF !important;
        border-color: rgba(117, 69, 255, 0.25) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(117, 69, 255, 0.25) 0%, rgba(33, 184, 255, 0.1) 100%) !important;
        color: #FFFFFF !important;
        border-left: 3px solid #7545FF !important;
        border-color: rgba(117, 69, 255, 0.35) !important;
        font-weight: 600 !important;
    }

    /* Sidebar Bottom Status Card */
    .sidebar-bottom-card {
        background: #151D38;
        border: 1px solid rgba(117, 69, 255, 0.2);
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 20px;
    }
    .engine-badge {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .engine-label {
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.5px;
    }
    .engine-name {
        font-size: 12px;
        font-weight: 600;
        color: #21B8FF;
    }
    .security-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        padding-top: 6px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
    }
    .sec-dot {
        width: 8px;
        height: 8px;
        background-color: #28D98A;
        border-radius: 50%;
        box-shadow: 0 0 8px #28D98A;
        display: inline-block;
    }
    .sec-text {
        font-size: 11px;
        font-weight: 500;
        color: #28D98A;
    }

    /* Kerala-Inspired Dashboard Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0D142E 0%, #151D38 55%, #181938 100%);
        border: 1px solid rgba(117, 69, 255, 0.3);
        border-radius: 16px;
        padding: 30px 34px 26px 34px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 20px;
    }
    .hero-banner::before {
        content: "";
        position: absolute;
        top: -40px;
        right: -40px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(117, 69, 255, 0.28) 0%, rgba(33, 184, 255, 0.12) 40%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-content {
        max-width: 600px;
        z-index: 1;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(117, 69, 255, 0.15);
        border: 1px solid rgba(117, 69, 255, 0.35);
        color: #C084FC;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 11.5px;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: 0.3px;
    }
    .hero-title {
        color: #FFFFFF;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.6px;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }
    .hero-grad-text {
        background: linear-gradient(135deg, #21B8FF 0%, #7545FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        color: #94A3B8;
        font-size: 15px;
        font-weight: 400;
        line-height: 1.5;
        margin: 0 0 18px 0;
    }
    .hero-meta-row {
        display: flex;
        align-items: center;
        gap: 14px;
        flex-wrap: wrap;
        padding-top: 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
    }
    .meta-label {
        color: #64748B;
        font-weight: 500;
    }
    .meta-val {
        color: #E2E8F0;
        font-weight: 600;
    }
    .meta-divider {
        width: 4px;
        height: 4px;
        background-color: #475569;
        border-radius: 50%;
    }
    .hero-graphic {
        z-index: 1;
        opacity: 0.95;
    }

    /* Metric KPI Cards */
    .kpi-card {
        background-color: #151D38;
        border: 1px solid rgba(117, 69, 255, 0.2);
        border-radius: 14px;
        padding: 20px 22px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 148px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 12px;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(33, 184, 255, 0.45);
    }
    .kpi-top-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #94A3B8;
    }
    .kpi-icon {
        font-size: 18px;
        padding: 6px 9px;
        background: rgba(117, 69, 255, 0.12);
        border-radius: 8px;
        border: 1px solid rgba(117, 69, 255, 0.2);
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .kpi-subtitle {
        font-size: 12px;
        color: #94A3B8;
        margin-bottom: 10px;
    }
    .kpi-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        align-self: flex-start;
    }

    /* Quick Access Module Cards */
    .module-card {
        background: linear-gradient(145deg, #151D38 0%, #11172E 100%);
        border: 1px solid rgba(117, 69, 255, 0.2);
        border-radius: 14px;
        padding: 22px;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.2s ease;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
        margin-bottom: 10px;
    }
    .module-card:hover {
        border-color: rgba(117, 69, 255, 0.45);
        box-shadow: 0 8px 24px rgba(117, 69, 255, 0.15);
        transform: translateY(-2px);
    }
    .module-num {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .module-title {
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .module-desc {
        font-size: 13px;
        color: #94A3B8;
        line-height: 1.5;
        flex-grow: 1;
        margin-bottom: 12px;
    }

    /* Dashboard Cards / General Container Cards */
    .dashboard-card {
        background-color: #151D38;
        border: 1px solid rgba(117, 69, 255, 0.2);
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        margin-bottom: 20px;
    }

    /* Primary and Secondary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7545FF 0%, #21B8FF 100%) !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 10px 22px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(117, 69, 255, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #38BDF8 100%) !important;
        box-shadow: 0 6px 22px rgba(117, 69, 255, 0.55) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #151D38 !important;
        color: #F8FAFC !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        border: 1px solid rgba(117, 69, 255, 0.25) !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #21B8FF !important;
        color: #21B8FF !important;
        background-color: #1A2447 !important;
        transform: translateY(-1px) !important;
    }

    /* Form Controls & Inputs */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {
        background-color: #151D38 !important;
        border-color: rgba(117, 69, 255, 0.25) !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
    }
    div[data-testid="stFileUploader"] {
        background-color: #151D38 !important;
        border: 1px dashed rgba(117, 69, 255, 0.35) !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }

    /* Word Error Highlight Badges */
    .tok-correct {
        background: rgba(40, 217, 138, 0.15);
        color: #28D98A;
        border: 1px solid rgba(40, 217, 138, 0.3);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 500;
        display: inline-block;
        margin: 2px;
    }
    .tok-sub {
        background: rgba(239, 68, 68, 0.18);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 500;
        display: inline-block;
        margin: 2px;
    }
    .tok-del {
        background: rgba(249, 115, 22, 0.18);
        color: #FB923C;
        border: 1px solid rgba(249, 115, 22, 0.4);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 500;
        text-decoration: line-through;
        display: inline-block;
        margin: 2px;
    }
    .tok-ins {
        background: rgba(33, 184, 255, 0.18);
        color: #60A5FA;
        border: 1px solid rgba(33, 184, 255, 0.4);
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 500;
        display: inline-block;
        margin: 2px;
    }

    /* Status Bar Card */
    .status-card {
        background: #151D38;
        border: 1px solid rgba(117, 69, 255, 0.2);
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin-bottom: 12px;
    }
    .status-card-label {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-card-val {
        color: #F8FAFC;
        font-size: 14px;
        font-weight: 600;
    }

    /* App Footer */
    .app-footer {
        margin-top: 48px;
        padding-top: 24px;
        border-top: 1px solid rgba(117, 69, 255, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }
    .footer-copy {
        color: #94A3B8;
        font-size: 13px;
    }
    .footer-links {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .footer-link {
        color: #21B8FF !important;
        text-decoration: none !important;
        font-size: 13px;
        font-weight: 500;
    }
    .footer-link:hover {
        color: #7545FF !important;
        text-decoration: underline !important;
    }
    .footer-sep {
        color: #475569;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


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
    if not text or not isinstance(text, str) or not text.strip():
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
            'match_rate': float percentage of reference critical items preserved (synonym for accuracy)
            'details': list of dicts with Category, Reference Value, Recognized Value, Status, Explanation
    """
    if not reference_text or not isinstance(reference_text, str):
        ref_entities = []
    else:
        ref_entities = extract_critical_entities(reference_text)

    if not hypothesis_text or not isinstance(hypothesis_text, str):
        hyp_entities = []
    else:
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
        "match_rate": accuracy,
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
    reference_text=None,
    clean_transcript="",
    noisy_transcript="",
    clean_quality=None,
    noisy_quality=None,
    clean_audio_name="clean_recording",
    noisy_audio_name="noisy_recording",
    reference=None,
    **kwargs
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
    ref_text = reference_text or reference or ""
    clean_wer_eval = evaluate(ref_text, clean_transcript)
    noisy_wer_eval = evaluate(ref_text, noisy_transcript)
    clean_cer_eval = evaluate_cer(ref_text, clean_transcript)
    noisy_cer_eval = evaluate_cer(ref_text, noisy_transcript)
    clean_crit = compare_critical_entities(ref_text, clean_transcript)
    noisy_crit = compare_critical_entities(ref_text, noisy_transcript)

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
        "table_rows": table_rows,
        "clean_transcript": clean_transcript,
        "noisy_transcript": noisy_transcript,
        "reference": ref_text,
        "clean_audio_name": clean_audio_name,
        "noisy_audio_name": noisy_audio_name,
        "clean_quality": clean_quality,
        "noisy_quality": noisy_quality,
        "clean": {
            "wer": clean_wer,
            "cer": clean_cer,
            "errors": clean_errors,
            "transcript": clean_transcript,
            "ref_words": clean_wer_eval["reference_words"] if clean_wer_eval else 0,
            "quality": clean_quality
        },
        "noisy": {
            "wer": noisy_wer,
            "cer": noisy_cer,
            "errors": noisy_errors,
            "transcript": noisy_transcript,
            "ref_words": noisy_wer_eval["reference_words"] if noisy_wer_eval else 0,
            "quality": noisy_quality
        },
        "degradation": {
            "delta_wer": delta_wer,
            "delta_cer": delta_cer,
            "delta_errors": delta_errors,
            "outcome": better_recording.capitalize()
        }
    }


def generate_comparison_txt_report(
    comp_results,
    reference=None,
    clean_audio_name=None,
    noisy_audio_name=None,
    language=None,
    clean_req_id="N/A",
    noisy_req_id="N/A"
):
    """Generate diagnostic plain-text comparison report between clean and noisy recordings."""
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    table_lines = [
        f"{'Metric':<32} | {'Clean Recording':<18} | {'Noisy Recording':<18} | {'Delta (Noisy - Clean)'}",
        "-" * 95
    ]
    for row in comp_results.get("table_rows", []):
        table_lines.append(
            f"{row.get('Metric', ''):<32} | {row.get('Clean Recording', ''):<18} | {row.get('Noisy Recording', ''):<18} | {row.get('Delta (Noisy - Clean)', '')}"
        )
    table_text = "\n".join(table_lines)

    ref_str = reference or comp_results.get("reference", "N/A")
    c_name = clean_audio_name or comp_results.get("clean_audio_name", "Clean Recording")
    n_name = noisy_audio_name or comp_results.get("noisy_audio_name", "Noisy Recording")
    lang_str = language or comp_results.get("language", "Malayalam")
    c_req = clean_req_id if clean_req_id != "N/A" else comp_results.get("clean_request_id", "N/A")
    n_req = noisy_req_id if noisy_req_id != "N/A" else comp_results.get("noisy_request_id", "N/A")
    clean_tr = comp_results.get("clean", {}).get("transcript") if isinstance(comp_results.get("clean"), dict) else comp_results.get("clean_transcript", "N/A")
    noisy_tr = comp_results.get("noisy", {}).get("transcript") if isinstance(comp_results.get("noisy"), dict) else comp_results.get("noisy_transcript", "N/A")
    outcome_str = comp_results.get("better_recording", "N/A").upper()

    report = f"""================================================================================
NADHAM QA - CLEAN VS. NOISY SPEECH RECOGNITION COMPARISON REPORT
================================================================================
Timestamp:          {timestamp_str}
Clean Audio:        {c_name}
Noisy Audio:        {n_name}
Language:           {lang_str}
Model:              Gnani Prisma v2.5
Clean Request ID:   {c_req}
Noisy Request ID:   {n_req}

BENCHMARK OUTCOME & RELIABILITY INTERPRETATION:
--------------------------------------------------------------------------------
Better Recording:   {outcome_str}
Interpretation:     {comp_results.get('interpretation', 'N/A')}

ACCURACY & ACOUSTIC COMPARISON TABLE:
--------------------------------------------------------------------------------
{table_text}

TRANSCRIPTS:
--------------------------------------------------------------------------------
Shared Ground Truth Reference:
{ref_str}

Clean Recording Transcript:
{clean_tr}

Noisy Recording Transcript:
{noisy_tr}

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
    lines.append("NADHAM QA — MALAYALAM SPEECH RECOGNITION BENCHMARK REPORT")
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

# -----------------------------------------------------------------------------
# State Management Initialization
# -----------------------------------------------------------------------------
if "eval_history" not in st.session_state:
    st.session_state["eval_history"] = []

if "api_status" not in st.session_state:
    st.session_state["api_status"] = "Ready (Dual-Source Secure)"

if "compare_results" not in st.session_state:
    st.session_state["compare_results"] = None

if "audio_quality" not in st.session_state:
    st.session_state["audio_quality"] = None

if "benchmark_results" not in st.session_state:
    st.session_state["benchmark_results"] = None

if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "📊 Dashboard"

language_codes = {
    "Malayalam": "ml-IN",
    "English": "en-IN",
    "Hindi": "hi-IN"
}

# -----------------------------------------------------------------------------
# Fixed-Style Sidebar Navigation & Branding
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand-box">
        <div class="brand-row">
            <div class="brand-icon-wrapper">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="2" x2="12" y2="22" stroke="url(#sbWaveGrad)"></line>
                    <line x1="8" y1="6" x2="8" y2="18" stroke="url(#sbWaveGrad)"></line>
                    <line x1="16" y1="6" x2="16" y2="18" stroke="url(#sbWaveGrad)"></line>
                    <line x1="4" y1="10" x2="4" y2="14" stroke="url(#sbWaveGrad)"></line>
                    <line x1="20" y1="10" x2="20" y2="14" stroke="url(#sbWaveGrad)"></line>
                    <defs>
                        <linearGradient id="sbWaveGrad" x1="4" y1="2" x2="20" y2="22" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#21B8FF"/>
                            <stop offset="1" stop-color="#7545FF"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            <div class="brand-title-wrap">
                <span class="brand-title-text">NADHAM <span style="color: #21B8FF;">QA</span></span>
            </div>
        </div>
        <div class="brand-subtitle-text">Speech Intelligence for Malayalam</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sidebar-sep'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-nav-label'>NAVIGATION</div>", unsafe_allow_html=True)

    nav_options = [
        "📊 Dashboard",
        "🎙️ Single Evaluation",
        "🔬 Clean vs Noisy",
        "🧪 Benchmark Lab",
        "📜 Evaluation History",
        "📑 Reports & Export",
        "ℹ️ About"
    ]

    if st.session_state.get("nav_selection") not in nav_options:
        st.session_state["nav_selection"] = "📊 Dashboard"

    current_nav_idx = nav_options.index(st.session_state["nav_selection"])

    selected_nav = st.radio(
        "Navigation Menu",
        nav_options,
        index=current_nav_idx,
        key="nav_selection_radio",
        label_visibility="collapsed"
    )

    if selected_nav != st.session_state["nav_selection"]:
        st.session_state["nav_selection"] = selected_nav
        st.rerun()

    st.markdown("<div style='min-height: 100px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sep'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-bottom-card">
        <div class="engine-badge">
            <span class="engine-label">Engine</span>
            <span class="engine-name">Gnani Prisma v2.5</span>
        </div>
        <div class="security-indicator">
            <span class="sec-dot"></span>
            <span class="sec-text">Secure API Integration</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Top Header & Product Title
# -----------------------------------------------------------------------------
st.title("🎙️ NADHAM QA")


# -----------------------------------------------------------------------------
# VIEW 1: 📊 DASHBOARD (Overview)
# -----------------------------------------------------------------------------
if st.session_state["nav_selection"] == "📊 Dashboard":
    # Kerala-Inspired Dark Navy & Purple Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-content">
            <div class="hero-badge">
                <span class="sec-dot"></span>
                <span>Kerala-First Voice Intelligence</span>
            </div>
            <h2 class="hero-title">Welcome to <span class="hero-grad-text">NADHAM QA</span></h2>
            <p class="hero-subtitle">
                Evaluate. Analyze. Improve Malayalam Speech Recognition.
            </p>
            <div class="hero-meta-row">
                <div class="meta-item">
                    <span class="meta-label">Engine:</span>
                    <span class="meta-val">Gnani Prisma v2.5</span>
                </div>
                <div class="meta-divider"></div>
                <div class="meta-item">
                    <span class="meta-label">Focus:</span>
                    <span class="meta-val">Malayalam Orthography</span>
                </div>
                <div class="meta-divider"></div>
                <div class="meta-item">
                    <span class="meta-label">Metrics:</span>
                    <span class="meta-val">Wagner-Fischer WER · UAX #29 CER</span>
                </div>
            </div>
        </div>
        <div class="hero-graphic">
            <svg class="hero-svg" width="340" height="100" viewBox="0 0 340 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="waveGradHero" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#7545FF"/>
                        <stop offset="50%" stop-color="#21B8FF"/>
                        <stop offset="100%" stop-color="#28D98A"/>
                    </linearGradient>
                    <linearGradient id="backwaterGrad" x1="0%" y1="100%" x2="100%" y2="0%">
                        <stop offset="0%" stop-color="#080D20" stop-opacity="0.8"/>
                        <stop offset="100%" stop-color="#21B8FF" stop-opacity="0.15"/>
                    </linearGradient>
                </defs>
                <path d="M0 65 Q 60 55, 120 65 T 240 65 T 340 65 L 340 100 L 0 100 Z" fill="url(#backwaterGrad)"/>
                <path d="M0 75 Q 50 65, 100 75 T 200 75 T 300 75 T 340 75 L 340 100 L 0 100 Z" fill="rgba(117,69,255,0.15)"/>
                <line x1="20" y1="62" x2="20" y2="40" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="40" y1="64" x2="40" y2="28" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="60" y1="62" x2="60" y2="15" stroke="url(#waveGradHero)" stroke-width="3" stroke-linecap="round"/>
                <line x1="80" y1="65" x2="80" y2="35" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="100" y1="65" x2="100" y2="45" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="120" y1="64" x2="120" y2="22" stroke="url(#waveGradHero)" stroke-width="3" stroke-linecap="round"/>
                <line x1="140" y1="63" x2="140" y2="10" stroke="url(#waveGradHero)" stroke-width="3.5" stroke-linecap="round"/>
                <line x1="160" y1="65" x2="160" y2="20" stroke="url(#waveGradHero)" stroke-width="3" stroke-linecap="round"/>
                <line x1="180" y1="64" x2="180" y2="38" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="200" y1="65" x2="200" y2="12" stroke="url(#waveGradHero)" stroke-width="3.5" stroke-linecap="round"/>
                <line x1="220" y1="65" x2="220" y2="30" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="240" y1="64" x2="240" y2="20" stroke="url(#waveGradHero)" stroke-width="3" stroke-linecap="round"/>
                <line x1="260" y1="64" x2="260" y2="45" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="280" y1="65" x2="280" y2="16" stroke="url(#waveGradHero)" stroke-width="3" stroke-linecap="round"/>
                <line x1="300" y1="64" x2="300" y2="35" stroke="url(#waveGradHero)" stroke-width="2.5" stroke-linecap="round"/>
                <line x1="320" y1="66" x2="320" y2="25" stroke="url(#waveGradHero)" stroke-width="3" stroke-linecap="round"/>
            </svg>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # KPI Metric Cards
    # -------------------------------------------------------------------------
    st.markdown("#### 📊 Key Performance Indicators")

    all_wers = []
    all_cers = []
    total_crit_matched = 0
    total_crit_expected = 0
    samples_evaluated_count = len(st.session_state["eval_history"])

    for item in st.session_state["eval_history"]:
        if item.get("wer") is not None:
            all_wers.append(item["wer"])
        if item.get("cer") is not None:
            all_cers.append(item["cer"])

    if st.session_state.get("benchmark_results") and "sample_results" in st.session_state["benchmark_results"]:
        bench = st.session_state["benchmark_results"]
        for s in bench.get("sample_results", []):
            if s.get("status") == "SUCCESS":
                samples_evaluated_count += 1
                if s.get("wer") is not None:
                    all_wers.append(s["wer"])
                if s.get("cer") is not None:
                    all_cers.append(s["cer"])
                if s.get("critical_entities"):
                    total_crit_expected += s["critical_entities"].get("expected", 0)
                    total_crit_matched += s["critical_entities"].get("matched", 0)

    # 1. Average WER
    if all_wers:
        avg_wer_num = sum(all_wers) / len(all_wers)
        avg_wer_val = f"{avg_wer_num:.2f}%"
        if avg_wer_num < 15.0:
            wer_status = ("#28D98A", "rgba(40, 217, 138, 0.15)", "High Precision")
        elif avg_wer_num < 30.0:
            wer_status = ("#FFB020", "rgba(255, 176, 32, 0.15)", "Moderate Error")
        else:
            wer_status = ("#EF4444", "rgba(239, 68, 68, 0.15)", "High Error Rate")
    else:
        avg_wer_val = "N/A"
        wer_status = ("#94A3B8", "rgba(148, 163, 184, 0.12)", "No Evaluations Yet")

    # 2. Average CER
    if all_cers:
        avg_cer_num = sum(all_cers) / len(all_cers)
        avg_cer_val = f"{avg_cer_num:.2f}%"
        if avg_cer_num < 10.0:
            cer_status = ("#28D98A", "rgba(40, 217, 138, 0.15)", "High Grapheme Precision")
        else:
            cer_status = ("#FFB020", "rgba(255, 176, 32, 0.15)", "Moderate Grapheme Error")
    else:
        avg_cer_val = "N/A"
        cer_status = ("#94A3B8", "rgba(148, 163, 184, 0.12)", "No Evaluations Yet")

    # 3. Critical Entity Match Rate
    if total_crit_expected > 0:
        crit_rate = (total_crit_matched / total_crit_expected) * 100
        crit_match_rate_val = f"{crit_rate:.1f}%"
        crit_status = ("#28D98A", "rgba(40, 217, 138, 0.15)", f"{total_crit_matched}/{total_crit_expected} Retained")
    else:
        crit_match_rate_val = "N/A"
        crit_status = ("#94A3B8", "rgba(148, 163, 184, 0.12)", "No Entities Tested")

    # 4. Samples Evaluated
    samples_val = str(samples_evaluated_count)
    samples_status = ("#21B8FF", "rgba(33, 184, 255, 0.15)", "Active Session") if samples_evaluated_count > 0 else ("#94A3B8", "rgba(148, 163, 184, 0.12)", "Awaiting Input")

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top-row">
                <span class="kpi-label">Average WER</span>
                <span class="kpi-icon">🎯</span>
            </div>
            <div class="kpi-value">{avg_wer_val}</div>
            <div class="kpi-subtitle">Word Error Rate (Wagner-Fischer)</div>
            <div class="kpi-status-badge" style="background: {wer_status[1]}; color: {wer_status[0]}; border: 1px solid {wer_status[0]};">
                ● {wer_status[2]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top-row">
                <span class="kpi-label">Average CER</span>
                <span class="kpi-icon">🔤</span>
            </div>
            <div class="kpi-value">{avg_cer_val}</div>
            <div class="kpi-subtitle">UAX #29 Grapheme Clusters</div>
            <div class="kpi-status-badge" style="background: {cer_status[1]}; color: {cer_status[0]}; border: 1px solid {cer_status[0]};">
                ● {cer_status[2]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top-row">
                <span class="kpi-label">Critical Match Rate</span>
                <span class="kpi-icon">🛡️</span>
            </div>
            <div class="kpi-value">{crit_match_rate_val}</div>
            <div class="kpi-subtitle">7 High-Risk Entity Types</div>
            <div class="kpi-status-badge" style="background: {crit_status[1]}; color: {crit_status[0]}; border: 1px solid {crit_status[0]};">
                ● {crit_status[2]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-top-row">
                <span class="kpi-label">Samples Evaluated</span>
                <span class="kpi-icon">📈</span>
            </div>
            <div class="kpi-value">{samples_val}</div>
            <div class="kpi-subtitle">Total Single & Batch Runs</div>
            <div class="kpi-status-badge" style="background: {samples_status[1]}; color: {samples_status[0]}; border: 1px solid {samples_status[0]};">
                ● {samples_status[2]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Performance Analytics
    # -------------------------------------------------------------------------
    st.markdown("#### 📈 Performance Analytics")

    if all_wers:
        col_c1, col_c2 = st.columns(2)
        chart_df = pd.DataFrame({
            "Evaluation Run": [f"Run {i+1}" for i in range(len(all_wers))],
            "WER (%)": all_wers,
            "CER (%)": all_cers if len(all_cers) == len(all_wers) else [0.0]*len(all_wers)
        }).set_index("Evaluation Run")

        with col_c1:
            st.markdown("##### 🎯 Word Error Rate (WER) Trend")
            st.line_chart(chart_df[["WER (%)"]], color="#7545FF")

        with col_c2:
            st.markdown("##### 🔤 Character Error Rate (CER) Trend")
            st.line_chart(chart_df[["CER (%)"]], color="#21B8FF")
    else:
        st.markdown("""
        <div class="dashboard-card" style="text-align: center; padding: 36px 20px;">
            <div style="font-size: 36px; margin-bottom: 10px;">📊</div>
            <div style="font-size: 17px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">No Evaluation Analytics Available Yet</div>
            <p style="color: #94A3B8; font-size: 13.5px; max-width: 500px; margin: 0 auto;">
                Analytics charts and progression metrics populate automatically as you evaluate speech samples in Single Evaluation, Clean vs Noisy, or Benchmark Lab.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Evaluation Modules Quick Access
    # -------------------------------------------------------------------------
    st.markdown("#### ⚡ Evaluation Modules")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
        <div class="module-card">
            <div class="module-num" style="color: #7545FF;">MODULE 01</div>
            <div class="module-title">🎙️ Single Evaluation</div>
            <div class="module-desc">
                Upload audio, provide ground-truth reference text, and evaluate ASR accuracy with Wagner-Fischer WER, grapheme CER, and critical entity detection.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Single Evaluation →", key="btn_dash_single", use_container_width=True):
            st.session_state["nav_selection"] = "🎙️ Single Evaluation"
            st.rerun()

    with col_m2:
        st.markdown("""
        <div class="module-card">
            <div class="module-num" style="color: #21B8FF;">MODULE 02</div>
            <div class="module-title">🔬 Clean vs Noisy</div>
            <div class="module-desc">
                Compare paired audio recordings to quantify recognition degradation (ΔWER and ΔCER), acoustic signal degradation, and critical retention.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Clean vs Noisy →", key="btn_dash_compare", use_container_width=True):
            st.session_state["nav_selection"] = "🔬 Clean vs Noisy"
            st.rerun()

    col_m3, col_m4 = st.columns(2)
    with col_m3:
        st.markdown("""
        <div class="module-card">
            <div class="module-num" style="color: #28D98A;">MODULE 03</div>
            <div class="module-title">🧪 Benchmark Lab</div>
            <div class="module-desc">
                Systematic batch evaluation across standardized Malayalam speech recordings, computing exact global error quotients with zero noise fabrication.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Benchmark Lab →", key="btn_dash_bench", use_container_width=True):
            st.session_state["nav_selection"] = "🧪 Benchmark Lab"
            st.rerun()

    with col_m4:
        st.markdown("""
        <div class="module-card">
            <div class="module-num" style="color: #A855F7;">MODULE 04</div>
            <div class="module-title">📜 Evaluation History</div>
            <div class="module-desc">
                Review historical evaluation logs, examine past transcript alignments, and export structured CSV/TXT verification evidence for auditing.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Evaluation History →", key="btn_dash_hist", use_container_width=True):
            st.session_state["nav_selection"] = "📜 Evaluation History"
            st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Recent Evaluation Results Table
    # -------------------------------------------------------------------------
    st.markdown("#### 📋 Recent Evaluation Results")

    if st.session_state["eval_history"]:
        hist_rows = []
        for i, h in enumerate(reversed(st.session_state["eval_history"])):
            ts = h.get("timestamp", datetime.now())
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if isinstance(ts, datetime) else str(ts)
            hist_rows.append({
                "Date & Time": ts_str,
                "Module": h.get("module", "Single Evaluation"),
                "Language": h.get("language", "Malayalam"),
                "Ref Words": h.get("ref_words", 0),
                "WER (%)": f"{h.get('wer', 0.0):.2f}%",
                "CER (%)": f"{h.get('cer', 0.0):.2f}%" if h.get("cer") is not None else "—",
                "Status": "COMPLETED"
            })
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True)
    else:
        st.markdown("""
        <div class="dashboard-card" style="text-align: center; padding: 32px 20px;">
            <div style="font-size: 32px; margin-bottom: 8px;">📋</div>
            <div style="font-size: 16px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">No Evaluation History in Current Session</div>
            <p style="color: #94A3B8; font-size: 13px; margin: 0 auto; max-width: 480px;">
                Completed single evaluations and benchmark runs will automatically appear here with full diagnostic metrics.
            </p>
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 2: 🎙️ SINGLE EVALUATION
# -----------------------------------------------------------------------------
elif st.session_state["nav_selection"] == "🎙️ Single Evaluation":
    st.markdown("### 🎙️ Single Audio Evaluation")
    st.caption("Benchmark ASR transcription accuracy, character-level grapheme edits, and domain-critical entities with Gnani Prisma STT.")

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

    # System Status Indicators
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
        current_status = st.session_state.get("api_status", "Ready (Dual-Source Secure)")
        if "Verified" in current_status or "Online" in current_status:
            badge_style = "color: #28D98A;"
            dot = "●"
        elif "504" in current_status or "Latency" in current_status:
            badge_style = "color: #EF4444;"
            dot = "▲"
        else:
            badge_style = "color: #21B8FF;"
            dot = "●"

        st.markdown(f"""
        <div class="status-card">
            <span class="status-card-label">API Gateway Status</span>
            <span class="status-card-val" style="{badge_style}">{dot} {current_status}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    run_clicked = st.button("🚀 Run NADHAM QA Test", type="primary", use_container_width=True)

    if run_clicked:
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
                    result = call_gnani(audio, language_codes[language])

                transcript = result.get("transcript", "")
                st.session_state["transcript"] = transcript
                st.session_state["reference"] = reference
                st.session_state["request_id"] = result.get("request_id", "Not available")
                st.session_state["language"] = language
                st.session_state["audio_name"] = audio.name
                st.session_state["api_status"] = "Online (Verified 200)"

                computed_metrics = evaluate(reference, transcript)
                cer_metrics = evaluate_cer(reference, transcript)
                if computed_metrics:
                    st.session_state["eval_history"].append({
                        "module": "Single Evaluation",
                        "audio_name": audio.name,
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

                if audio.name.lower().endswith(".wav"):
                    st.session_state["audio_quality"] = analyze_audio_quality(audio.getvalue())
                else:
                    st.session_state["audio_quality"] = {"supported": False, "message": "Acoustic signal metrics currently support standard PCM WAV formats."}

            except Exception as error:
                err_str = str(error)
                if "504" in err_str or "gateway" in err_str.lower():
                    st.session_state["api_status"] = "Gateway Latency (504 Timeout)"
                else:
                    st.session_state["api_status"] = "API Error"
                st.error(f"Test failed: {error}")

    # Display Single Evaluation Results
    if st.session_state.get("transcript") is not None and st.session_state.get("reference") is not None:
        ref_text = st.session_state["reference"]
        hyp_text = st.session_state["transcript"]
        metrics = evaluate(ref_text, hyp_text)
        cer_metrics = evaluate_cer(ref_text, hyp_text)
        crit_results = None
        try:
            crit_results = compare_critical_entities(ref_text, hyp_text)
        except Exception as e:
            logger.error(f"Critical entity evaluation error: {e}")
            crit_results = None

        st.markdown("---")
        st.markdown("### 📊 Evaluation Diagnostics & Metrics")

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Word Error Rate (WER)", f"{metrics['wer']:.2f}%", help="Lower is better. 0% represents a perfect word-level match.")
        with m_col2:
            if cer_metrics and "cer" in cer_metrics:
                st.metric("Character Error Rate (CER)", f"{cer_metrics['cer']:.2f}%", help="Character-level edit distance evaluated over Unicode UAX #29 extended grapheme clusters.")
            else:
                st.metric("Character Error Rate (CER)", "N/A")
        with m_col3:
            if crit_results and isinstance(crit_results, dict) and ("match_rate" in crit_results or "accuracy" in crit_results):
                crit_rate = crit_results.get("match_rate", crit_results.get("accuracy"))
                if crit_results.get("total_items", 0) > 0 and crit_rate is not None:
                    st.metric(
                        "Critical Entity Match",
                        f"{crit_rate:.1f}%",
                        help="Retention of high-stakes entities: numbers, dates, times, currencies, phone numbers, negations, and names."
                    )
                else:
                    st.metric(
                        "Critical Entity Match",
                        "N/A",
                        help="No domain-critical entities (numbers, dates, times, currencies, phone numbers, negations, or names) detected in reference text."
                    )
            else:
                st.metric(
                    "Critical Entity Match",
                    "N/A",
                    help="Critical information evaluation is unavailable or could not be completed."
                )
        with m_col4:
            st.metric("Total Word Errors", f"{metrics['errors']}", help="Sum of word substitutions, deletions, and insertions.")

        aq = st.session_state.get("audio_quality")
        if aq and aq.get("supported"):
            st.markdown("#### 🎧 Local Acoustic Signal Metrics")
            aq_c1, aq_c2, aq_c3, aq_c4 = st.columns(4)
            with aq_c1:
                st.metric("Duration / Rate", f"{aq['duration_s']:.2f}s", f"{aq['sample_rate']} Hz")
            with aq_c2:
                st.metric("Peak Amplitude", f"{aq['peak_dbfs']:.1f} dBFS")
            with aq_c3:
                st.metric("RMS Level", f"{aq['rms_dbfs']:.1f} dBFS")
            with aq_c4:
                st.metric("Clipping / Silence", f"{aq['clipping_pct']:.1f}% clip", f"{aq['silence_pct']:.1f}% silent")

        # ---------------------------------------------------------------------
        # Transcript Comparison UI
        # ---------------------------------------------------------------------
        st.markdown("#### 📝 Comparative Transcripts")

        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(f"""
            <div class="dashboard-card" style="min-height: 140px;">
                <div style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 8px;">Ground Truth Reference</div>
                <div style="color: #FFFFFF; font-size: 16px; line-height: 1.8; font-family: 'Noto Sans Malayalam', sans-serif;">
                    {ref_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with t_col2:
            req_id_str = st.session_state.get("request_id", "N/A")
            st.markdown(f"""
            <div class="dashboard-card" style="min-height: 140px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 700; color: #21B8FF; text-transform: uppercase;">Gnani Prisma Recognized</span>
                    <span style="font-size: 10px; color: #64748B;">Req ID: {str(req_id_str)[:12]}</span>
                </div>
                <div style="color: #FFFFFF; font-size: 16px; line-height: 1.8; font-family: 'Noto Sans Malayalam', sans-serif;">
                    {hyp_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Word-Level Error Highlight Visualization
        st.markdown("#### 🔍 Word-Level Alignment & Highlight")
        highlight_tokens = []
        for op in metrics["operations"]:
            tag = op[0]
            ref_w = op[1]
            hyp_w = op[2]
            if tag == "Correct":
                highlight_tokens.append(f'<span class="tok-correct">{ref_w}</span>')
            elif tag == "Substitution":
                highlight_tokens.append(f'<span class="tok-sub">{ref_w} ➔ {hyp_w}</span>')
            elif tag == "Deletion":
                highlight_tokens.append(f'<span class="tok-del">{ref_w}</span>')
            elif tag == "Insertion":
                highlight_tokens.append(f'<span class="tok-ins">+{hyp_w}</span>')

        st.markdown(f"""
        <div class="dashboard-card" style="line-height: 2.2;">
            {' '.join(highlight_tokens)}
        </div>
        """, unsafe_allow_html=True)

        # Critical Entities Comparison Table
        st.markdown("#### 🛡️ Critical Information Detection & Entity Alignment")
        if crit_results and isinstance(crit_results, dict) and crit_results.get("details"):
            df_crit = pd.DataFrame(crit_results["details"])
            st.dataframe(df_crit, use_container_width=True)
        else:
            st.info("No domain-critical entities (numbers, dates, times, currencies, phone numbers, negations, or names) detected in the reference text.")

        # Download Reports
        st.markdown("#### 📥 Diagnostic Reports & Export")
        audio_name = st.session_state.get("audio_name", "recording")
        if crit_results and isinstance(crit_results, dict) and crit_results.get("total_items", 0) > 0 and ("match_rate" in crit_results or "accuracy" in crit_results):
            crit_rep_rate = crit_results.get("match_rate", crit_results.get("accuracy"))
            crit_match_str = f"{crit_rep_rate:.1f}%"
        elif crit_results and isinstance(crit_results, dict) and crit_results.get("total_items", 0) == 0:
            crit_match_str = "N/A (No entities in reference)"
        else:
            crit_match_str = "N/A (Unavailable)"

        report_txt = (
            "NADHAM QA - SPEECH RECOGNITION TEST REPORT\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Audio: {audio_name}\n"
            f"Language: {st.session_state.get('language', 'Malayalam')}\n"
            f"WER: {metrics['wer']:.2f}%\n"
            f"CER: {cer_metrics['cer'] if cer_metrics else 'N/A'}%\n"
            f"Critical Match Rate: {crit_match_str}\n\n"
            "Reference Transcript:\n"
            f"{ref_text}\n\n"
            "Recognized Transcript:\n"
            f"{hyp_text}\n"
        )
        dl_c1, dl_c2 = st.columns(2)
        with dl_c1:
            st.download_button(
                "📥 Download Test Report (.txt)",
                report_txt,
                file_name=f"NADHAM_QA_Report_{audio_name}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with dl_c2:
            rows = [{"Operation": op[0], "Reference Word": op[1], "Recognized Word": op[2]} for op in metrics["operations"]]
            df_ops = pd.DataFrame(rows)
            st.download_button(
                "📊 Download Error Analysis (.csv)",
                df_ops.to_csv(index=False).encode("utf-8"),
                file_name=f"NADHAM_QA_Analysis_{audio_name}.csv",
                mime="text/csv",
                use_container_width=True
            )


# -----------------------------------------------------------------------------
# VIEW 3: 🔬 CLEAN VS NOISY COMPARISON
# -----------------------------------------------------------------------------
elif st.session_state["nav_selection"] == "🔬 Clean vs Noisy":
    st.markdown("### 🔬 Clean vs. Noisy Speech Recognition Benchmark")
    st.caption("Quantify speech recognition degradation, character-level sensitivity, critical entity retention, and acoustic signal properties under ambient noise.")

    st.warning("⚠️ **Credit & API Notice:** Clean vs. Noisy comparison evaluates two recordings against a shared reference transcript. This initiates two independent requests to Gnani Prisma STT and consumes 2 API transactions. Analysis begins strictly when you click the comparison button below.")

    comp_language = st.selectbox(
        "Select recording language",
        ["Malayalam", "English", "Hindi"],
        index=0,
        key="comp_lang_select"
    )

    col_clean, col_noisy = st.columns(2, gap="medium")

    with col_clean:
        st.markdown("#### 🟢 Clean Audio Recording")
        clean_audio = st.file_uploader(
            "Upload clean recording",
            type=["wav", "mp3", "ogg", "flac", "aac", "m4a"],
            key="clean_audio_input"
        )
        if clean_audio is not None:
            st.audio(clean_audio)
            st.caption(f"📁 `{clean_audio.name}` ({len(clean_audio.getvalue()) / 1024:.1f} KB)")

    with col_noisy:
        st.markdown("#### 🔴 Noisy Audio Recording")
        noisy_audio = st.file_uploader(
            "Upload noisy recording",
            type=["wav", "mp3", "ogg", "flac", "aac", "m4a"],
            key="noisy_audio_input"
        )
        if noisy_audio is not None:
            st.audio(noisy_audio)
            st.caption(f"📁 `{noisy_audio.name}` ({len(noisy_audio.getvalue()) / 1024:.1f} KB)")

    comp_reference = st.text_area(
        "Ground truth reference transcript",
        placeholder="Enter exactly what was spoken in both recordings...",
        height=120,
        key="comp_ref_text"
    )

    run_compare_clicked = st.button("🔬 Run Clean vs Noisy Comparison", type="primary", use_container_width=True)

    if run_compare_clicked:
        if clean_audio is None or noisy_audio is None:
            st.error("Please upload both Clean and Noisy audio recordings.")
        elif len(clean_audio.getvalue()) == 0 or len(noisy_audio.getvalue()) == 0:
            st.error("One of the uploaded audio files is empty (0 bytes).")
        elif len(clean_audio.getvalue()) > MAX_AUDIO_BYTES or len(noisy_audio.getvalue()) > MAX_AUDIO_BYTES:
            st.error(f"One of the audio files exceeds the {MAX_AUDIO_BYTES // (1024 * 1024)} MB limit.")
        elif not comp_reference.strip() or not words(comp_reference):
            st.error("Please enter a valid reference transcript with meaningful words.")
        else:
            try:
                with st.spinner("Transcribing Clean and Noisy recordings with Gnani Prisma STT..."):
                    clean_res = call_gnani(clean_audio, language_codes[comp_language])
                    noisy_res = call_gnani(noisy_audio, language_codes[comp_language])

                clean_text = clean_res.get("transcript", "")
                noisy_text = noisy_res.get("transcript", "")

                clean_q = analyze_audio_quality(clean_audio.getvalue()) if clean_audio.name.lower().endswith(".wav") else {"supported": False, "message": "MP3/other format"}
                noisy_q = analyze_audio_quality(noisy_audio.getvalue()) if noisy_audio.name.lower().endswith(".wav") else {"supported": False, "message": "MP3/other format"}

                comparison = compare_clean_noisy(
                    reference=comp_reference,
                    clean_transcript=clean_text,
                    noisy_transcript=noisy_text,
                    clean_quality=clean_q,
                    noisy_quality=noisy_q,
                    clean_audio_name=clean_audio.name,
                    noisy_audio_name=noisy_audio.name
                )

                st.session_state["compare_results"] = comparison
                st.session_state["eval_history"].append({
                    "module": "Clean vs Noisy",
                    "wer": comparison["clean"]["wer"],
                    "cer": comparison["clean"]["cer"],
                    "noisy_wer": comparison["noisy"]["wer"],
                    "noisy_cer": comparison["noisy"]["cer"],
                    "ref_words": comparison["clean"]["ref_words"],
                    "language": comp_language,
                    "timestamp": datetime.now()
                })
            except Exception as e:
                st.error(f"Comparison test failed: {e}")

    # Display Comparison Results
    comp = st.session_state.get("compare_results")
    if comp:
        st.markdown("---")
        st.markdown("### 📊 Clean vs. Noisy Degradation Analysis")

        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        with c_m1:
            st.metric("Clean WER", f"{comp['clean']['wer']:.2f}%")
        with c_m2:
            st.metric("Noisy WER", f"{comp['noisy']['wer']:.2f}%")
        with c_m3:
            d_wer = comp["degradation"]["delta_wer"]
            st.metric("ΔWER (Degradation)", f"{d_wer:+.2f}%", delta_color="inverse")
        with c_m4:
            st.metric("Comparison Outcome", comp["degradation"]["outcome"])

        # Acoustic Quality Comparison Table
        cq = comp.get("clean_quality", {})
        nq = comp.get("noisy_quality", {})
        if cq.get("supported") and nq.get("supported"):
            st.markdown("#### 🎧 Acoustic Signal Comparison")
            aq_table = pd.DataFrame([
                {"Metric": "Duration", "Clean Audio": f"{cq['duration_s']:.2f}s", "Noisy Audio": f"{nq['duration_s']:.2f}s"},
                {"Metric": "Peak Amplitude", "Clean Audio": f"{cq['peak_dbfs']:.1f} dBFS", "Noisy Audio": f"{nq['peak_dbfs']:.1f} dBFS"},
                {"Metric": "RMS Level", "Clean Audio": f"{cq['rms_dbfs']:.1f} dBFS", "Noisy Audio": f"{nq['rms_dbfs']:.1f} dBFS"},
                {"Metric": "Clipping %", "Clean Audio": f"{cq['clipping_pct']:.1f}%", "Noisy Audio": f"{nq['clipping_pct']:.1f}%"},
                {"Metric": "Silence %", "Clean Audio": f"{cq['silence_pct']:.1f}%", "Noisy Audio": f"{nq['silence_pct']:.1f}%"}
            ])
            st.dataframe(aq_table, use_container_width=True)

        # Transcripts Display
        st.markdown("#### 📝 Recognized Transcripts")
        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown(f"""
            <div class="dashboard-card">
                <span style="color: #28D98A; font-size: 11px; font-weight: 700; text-transform: uppercase;">Clean Recognized</span>
                <p style="color: #FFFFFF; font-size: 15px; margin-top: 8px; line-height: 1.8;">{comp['clean']['transcript']}</p>
            </div>
            """, unsafe_allow_html=True)
        with tc2:
            st.markdown(f"""
            <div class="dashboard-card">
                <span style="color: #EF4444; font-size: 11px; font-weight: 700; text-transform: uppercase;">Noisy Recognized</span>
                <p style="color: #FFFFFF; font-size: 15px; margin-top: 8px; line-height: 1.8;">{comp['noisy']['transcript']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Export Buttons
        dl_c1, dl_c2 = st.columns(2)
        with dl_c1:
            txt_rep = generate_comparison_txt_report(comp)
            st.download_button("📥 Download Comparison Report (.txt)", txt_rep, file_name="NADHAM_QA_Comparison_Report.txt", mime="text/plain", use_container_width=True)
        with dl_c2:
            csv_rep = generate_comparison_csv(comp)
            st.download_button("📊 Download Comparison CSV (.csv)", csv_rep if isinstance(csv_rep, bytes) else csv_rep.encode("utf-8"), file_name="NADHAM_QA_Comparison.csv", mime="text/csv", use_container_width=True)


# -----------------------------------------------------------------------------
# VIEW 4: 🧪 BENCHMARK LAB
# -----------------------------------------------------------------------------
elif st.session_state["nav_selection"] == "🧪 Benchmark Lab":
    st.markdown("### 🧪 Malayalam Benchmark Lab & Reliability Evidence")
    st.caption("Systematic batch evaluation across standardized Malayalam speech recordings with exact aggregate error quotients.")

    dataset_info = discover_benchmark_dataset()

    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.metric("Discovered Samples", f"{dataset_info['total_discovered']}")
    with b_col2:
        st.metric("Verified Valid", f"{dataset_info['valid_count']}")
    with b_col3:
        st.metric("Acoustic Condition", "Pure Normal Speech")
    with b_col4:
        st.metric("Paired Noise Status", "No Paired Noisy Samples")

    # Transparency Notice (Required)
    st.info("📢 **Paired Clean vs. Noisy Benchmark Status:** The benchmark dataset currently contains five normal Malayalam speech recordings (`dataset/normal/`) and does not contain paired noisy recordings. In the spirit of honest evaluation, NADHAM QA transparently reports this rather than fabricating synthetic noise.")

    sample_options = [s["sample_id"] for s in dataset_info["samples"] if s.get("valid_pair")]
    selected_samples = st.multiselect(
        "Select Benchmark Samples to Evaluate",
        sample_options,
        default=sample_options
    )

    st.warning("⚠️ **API Consumption Warning:** Batch evaluation sends one live request to Gnani Prisma STT per selected sample. Run only when necessary.")

    run_bench_clicked = st.button("🚀 Execute Malayalam Benchmark", type="primary", use_container_width=True)

    if run_bench_clicked:
        if not selected_samples:
            st.error("Please select at least one benchmark sample to evaluate.")
        else:
            prog_bar = st.progress(0.0)
            status_txt = st.empty()

            def progress_cb(current, total, sample_id):
                prog_bar.progress(current / total)
                status_txt.text(f"Evaluating {sample_id} ({current}/{total})...")

            batch_results = evaluate_benchmark_batch(
                dataset_info,
                selected_sample_ids=selected_samples,
                language_code="ml-IN",
                progress_callback=progress_cb
            )

            prog_bar.progress(1.0)
            status_txt.text("Benchmark batch evaluation complete!")
            st.session_state["benchmark_results"] = batch_results

    bench = st.session_state.get("benchmark_results")
    if bench:
        agg = bench.get("aggregate", {})
        summary = bench.get("summary", {})

        st.markdown("---")
        st.markdown("### 📊 Benchmark Aggregate Results")

        res_c1, res_c2, res_c3, res_c4 = st.columns(4)
        with res_c1:
            st.metric("Aggregate WER", f"{agg.get('aggregate_wer', 0.0):.2f}%" if agg.get("aggregate_wer") is not None else "N/A")
        with res_c2:
            st.metric("Aggregate CER", f"{agg.get('aggregate_cer', 0.0):.2f}%" if agg.get("aggregate_cer") is not None else "N/A")
        with res_c3:
            st.metric("Benchmark Success Rate", f"{summary.get('benchmark_success_rate', 0.0):.1f}%")
        with res_c4:
            st.metric("Critical Entity Match", f"{agg.get('aggregate_critical_match_rate', 0.0):.1f}%" if agg.get("aggregate_critical_match_rate") is not None else "N/A")

        # Sample-Level Results Table
        st.markdown("#### 📋 Sample-Level Breakdown")
        table_rows = []
        for s in bench.get("sample_results", []):
            table_rows.append({
                "Sample ID": s["sample_id"],
                "Audio File": s["audio_filename"],
                "Ref Words": s["ref_words"],
                "Hyp Words": s["hyp_words"],
                "WER (%)": f"{s['wer']:.2f}%" if s.get("wer") is not None else "N/A",
                "CER (%)": f"{s['cer']:.2f}%" if s.get("cer") is not None else "N/A",
                "Critical Match": f"{s['critical_match_rate']:.1f}%" if s.get("critical_match_rate") is not None else "N/A",
                "Latency (s)": f"{s.get('latency_sec', 0.0):.2f}",
                "Status": s.get("status", "SUCCESS")
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        # Export Evidence
        st.markdown("#### 📥 Export Benchmark Evidence Reports")
        dl_c1, dl_c2, dl_c3 = st.columns(3)
        with dl_c1:
            txt_rep = generate_benchmark_summary_txt(bench, dataset_info)
            st.download_button("📥 Benchmark Summary (TXT)", txt_rep.encode("utf-8"), file_name=f"NADHAM_QA_Benchmark_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain", use_container_width=True)
        with dl_c2:
            sample_csv = generate_benchmark_sample_csv(bench)
            st.download_button("📊 Sample-Level CSV", sample_csv.encode("utf-8"), file_name=f"NADHAM_QA_Benchmark_Samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
        with dl_c3:
            agg_csv = generate_benchmark_aggregate_csv(bench)
            st.download_button("📈 Aggregate Metrics CSV", agg_csv.encode("utf-8"), file_name=f"NADHAM_QA_Benchmark_Aggregate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)


# -----------------------------------------------------------------------------
# VIEW 5: 📜 EVALUATION HISTORY & AUDIT
# -----------------------------------------------------------------------------
elif st.session_state["nav_selection"] == "📜 Evaluation History":
    st.markdown("### 📜 Evaluation History & Audit Trail")
    st.caption("Complete chronological record of all single and benchmark evaluation sessions executed.")

    if st.session_state["eval_history"]:
        h_col1, h_col2, h_col3 = st.columns(3)
        with h_col1:
            st.metric("Total Executions", len(st.session_state["eval_history"]))
        with h_col2:
            wers = [h["wer"] for h in st.session_state["eval_history"] if h.get("wer") is not None]
            st.metric("Session Average WER", f"{sum(wers)/len(wers):.2f}%" if wers else "N/A")
        with h_col3:
            cers = [h["cer"] for h in st.session_state["eval_history"] if h.get("cer") is not None]
            st.metric("Session Average CER", f"{sum(cers)/len(cers):.2f}%" if cers else "N/A")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        history_data = []
        for h in reversed(st.session_state["eval_history"]):
            ts = h.get("timestamp", datetime.now())
            ts_str = ts.strftime("%Y-%m-%d %H:%M:%S") if isinstance(ts, datetime) else str(ts)
            history_data.append({
                "Timestamp": ts_str,
                "Module": h.get("module", "Single Evaluation"),
                "Language": h.get("language", "Malayalam"),
                "Ref Words": h.get("ref_words", "N/A"),
                "WER (%)": f"{h.get('wer', 0.0):.2f}%",
                "CER (%)": f"{h.get('cer', 0.0):.2f}%" if h.get("cer") is not None else "—",
                "Status": "COMPLETED"
            })
        st.dataframe(pd.DataFrame(history_data), use_container_width=True)

        if st.button("🗑️ Clear Session History", key="btn_clear_history"):
            st.session_state["eval_history"] = []
            st.rerun()
    else:
        st.markdown("""
        <div class="dashboard-card" style="text-align: center; padding: 48px 20px;">
            <div style="font-size: 40px; margin-bottom: 12px;">📜</div>
            <div style="font-size: 18px; font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">No Evaluation History Recorded Yet</div>
            <p style="color: #94A3B8; font-size: 14px; max-width: 500px; margin: 0 auto;">
                Perform an evaluation in Single Evaluation, Clean vs Noisy, or Benchmark Lab to generate audit logs.
            </p>
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 6: 📑 REPORTS & EXPORT CENTER
# -----------------------------------------------------------------------------
elif st.session_state["nav_selection"] == "📑 Reports & Export":
    st.markdown("### 📑 Reports & Diagnostic Export Center")
    st.caption("Centralized repository of generated audit reports, alignment spreadsheets, and benchmark summaries.")

    rep_col1, rep_col2, rep_col3 = st.columns(3)

    with rep_col1:
        st.markdown("""
        <div class="module-card">
            <div class="module-num" style="color: #7545FF;">REPORTS 01</div>
            <div class="module-title">🎙️ Single Test Report</div>
            <div class="module-desc">
                Download structured TXT diagnostic summaries and word-level Levenshtein alignment CSV tables.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.get("transcript"):
            st.success("Latest single evaluation report available!")
        else:
            st.caption("No single evaluation executed in this session.")

    with rep_col2:
        st.markdown("""
        <div class="module-card">
            <div class="module-num" style="color: #21B8FF;">REPORTS 02</div>
            <div class="module-title">🔬 Comparison Report</div>
            <div class="module-desc">
                Download clean vs. noisy degradation comparisons, delta metrics, and acoustic signal tables.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.get("compare_results"):
            st.success("Comparison report available!")
        else:
            st.caption("No clean vs. noisy comparison executed yet.")

    with rep_col3:
        st.markdown("""
        <div class="module-card">
            <div class="module-num" style="color: #28D98A;">REPORTS 03</div>
            <div class="module-title">🧪 Benchmark Bundle</div>
            <div class="module-desc">
                Download complete benchmark evidence bundles, sample-level matrices, and aggregate CSVs.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.get("benchmark_results"):
            st.success("Benchmark evidence available!")
        else:
            st.caption("No benchmark run executed yet.")


# -----------------------------------------------------------------------------
# VIEW 7: ℹ️ ABOUT NADHAM QA
# -----------------------------------------------------------------------------
elif st.session_state["nav_selection"] == "ℹ️ About":
    st.markdown("### ℹ️ About NADHAM QA — Speech Intelligence Platform")
    st.markdown("""
    <div class="dashboard-card">
        <h3 style="color: #FFFFFF; margin-top: 0;">🎙️ The Kerala-First Speech Intelligence Mission</h3>
        <p style="color: #94A3B8; font-size: 14.5px; line-height: 1.7;">
            <strong>NADHAM QA</strong> is an enterprise evaluation platform designed to benchmark Indic speech recognition models with true linguistic precision, specifically tailored for <strong>Gnani Prisma STT (v2.5)</strong>.
        </p>
        <h4 style="color: #21B8FF; margin-top: 20px;">🌟 Why Malayalam Needs Specialized Evaluation:</h4>
        <ol style="color: #E2E8F0; font-size: 14px; line-height: 1.8;">
            <li><strong>Malayalam Chillu Ambiguity:</strong> Modern Unicode represents chillu letters atomically (<code>ൺ</code>, <code>ൻ</code>, <code>ർ</code>, <code>ൽ</code>, <code>ൾ</code>, <code>ൿ</code>), whereas legacy keyboards generate decomposed consonant + virama + Zero-Width Joiner (ZWJ). Standard NFC normalization fails to equate them; NADHAM QA canonicalizes them to prevent artificial error inflation.</li>
            <li><strong>Zero-Width Formatting Controls:</strong> Zero-Width Spaces (<code>\u200B</code>) and Joiners that glue words together are handled cleanly.</li>
            <li><strong>Domain-Critical Entities:</strong> Naive punctuation stripping destroys decimals (<code>3.14</code> ➔ <code>314</code>) and dates. NADHAM QA identifies and preserves 7 high-risk critical entity types.</li>
        </ol>
        <h4 style="color: #28D98A; margin-top: 20px;">⚙️ Dual-Granularity Evaluation Methodology:</h4>
        <p style="color: #94A3B8; font-size: 14px; line-height: 1.7;">
            NADHAM QA implements the exact <strong>Wagner-Fischer Dynamic Programming algorithm</strong> for word-level Word Error Rate (WER) alongside Character Error Rate (CER) evaluated over <strong>Unicode UAX #29 extended grapheme clusters</strong> (whitespace excluded).
        </p>
        <h4 style="color: #C084FC; margin-top: 20px;">🛡️ Enterprise Safety Guardrails:</h4>
        <ul style="color: #E2E8F0; font-size: 14px; line-height: 1.8;">
            <li>Client-side rejection of 0-byte (empty) audio files to safeguard API quotas.</li>
            <li>25 MB upload ceiling to mitigate memory exhaustion.</li>
            <li>Sanitization of upstream HTML errors (e.g. Cloudflare 504 Gateway Timeouts).</li>
            <li>Session state invalidation on each new test to eliminate stale UI metrics.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Global App Footer & Branding
# -----------------------------------------------------------------------------
st.markdown("""
<div class="app-footer">
    <div class="footer-copy">
        Built with ❤️ for Malayalam AI Innovation · Powered by <a href="https://gnani.ai" target="_blank" style="color: #21B8FF; text-decoration: none; font-weight: 600;">Gnani Prisma v2.5</a>
    </div>
    <div class="footer-links">
        <a href="https://github.com/saviosinto123/NADHAM-QA" target="_blank" class="footer-link">GitHub Repository</a>
        <span class="footer-sep">·</span>
        <a href="https://github.com/saviosinto123/NADHAM-QA/blob/main/README.md" target="_blank" class="footer-link">Documentation</a>
        <span class="footer-sep">·</span>
        <a href="https://gnani.ai" target="_blank" class="footer-link">Gnani AI</a>
    </div>
</div>
""", unsafe_allow_html=True)
