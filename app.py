import os
import re
import requests
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
# Gnani Prisma STT API Client
# -----------------------------------------------------------------------------
def call_gnani(audio, language):
    api_key = os.getenv("GNANI_API_KEY")

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
# State Management Initialization
# -----------------------------------------------------------------------------
if "eval_history" not in st.session_state:
    st.session_state["eval_history"] = []

if "api_status" not in st.session_state:
    st.session_state["api_status"] = "Ready (Unverified Live)"


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
            if computed_metrics:
                st.session_state["eval_history"].append({
                    "wer": computed_metrics["wer"],
                    "errors": computed_metrics["errors"],
                    "ref_words": computed_metrics["reference_words"],
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
    avg_wer_val = f"{sum(e['wer'] for e in st.session_state['eval_history']) / total_evals:.2f}%"
    correct_words_val = f"{latest_item['correct']} / {latest_item['ref_words']}"
    total_evals_val = str(total_evals)
else:
    latest_wer_val = "—"
    avg_wer_val = "—"
    correct_words_val = "—"
    total_evals_val = "0"

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Latest WER", latest_wer_val, help="Word Error Rate of the most recent evaluation in this session.")
m_col2.metric("Correct Words", correct_words_val, help="Tokens recognized correctly vs reference words.")
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

    if metrics:

        st.markdown("### Accuracy Metrics")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Word Error Rate",
            f"{metrics['wer']:.2f}%"
        )

        c2.metric(
            "Word Errors",
            metrics["errors"]
        )

        c3.metric(
            "Reference Words",
            metrics["reference_words"]
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

        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        audio_name = st.session_state.get("audio_name", "audio_recording")

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

        st.markdown("### 📥 Diagnostic Reports & Export")
        col_d1, col_d2 = st.columns(2)

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

# -----------------------------------------------------------------------------
# About NADHAM QA Section (Expandable)
# -----------------------------------------------------------------------------
with st.expander("ℹ️ About NADHAM QA — Kerala-First Speech Intelligence", expanded=False):
    st.markdown("""
    ### 🎙️ The Kerala-First Speech Intelligence Mission
    **NADHAM QA** is an enterprise evaluation platform designed to benchmark Indic speech recognition models with true linguistic precision, specifically tailored for **Gnani Prisma STT (v2.5)**.

    #### 🌟 Why Malayalam Needs Specialized Evaluation:
    1. **Malayalam Chillu Ambiguity:** Modern Unicode represents chillu letters atomically (`ൺ`, `ൻ`, `ർ`, `ൽ`, `ൾ`, `ൿ`), whereas legacy keyboards generate decomposed consonant + virama (`്`) + Zero-Width Joiner (`ZWJ`). Standard NFC normalization fails to equate them; NADHAM QA canonicalizes them to prevent artificial error inflation.
    2. **Zero-Width Controls:** Zero-Width Spaces (`\\u200B`) and Joiners (`\\u200D`/`\\u200C`) that glue words together are handled cleanly.
    3. **Entity Preservation:** Standard punctuation filters destroy decimals (`3.14` → `314`) and dates (`15/08/1947` → `15081947`). NADHAM QA preserves numeric entities and normalizes currency symbols (`₹`, `$`).

    #### ⚙️ Evaluation Methodology:
    NADHAM QA implements the exact **Wagner-Fischer Dynamic Programming algorithm** to compute word-level Levenshtein distance, decomposing errors strictly into:
    $$\\text{WER} = \\frac{\\text{Substitutions} + \\text{Deletions} + \\text{Insertions}}{\\text{Reference Word Count}} \\times 100\\%$$

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
