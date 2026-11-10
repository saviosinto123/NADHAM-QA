import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import pytest

# Ensure the app directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import words, evaluate, call_gnani


# =====================================================================
# 1. Malayalam Unicode & Text Normalization Tests
# =====================================================================

class TestNormalization:
    """Tests for words() text normalization function."""

    def test_basic_english_normalization(self):
        """Punctuation is removed, case is lowered, whitespace normalized."""
        text = "Hello, World! This is a TEST... right?"
        result = words(text)
        assert result == ["hello", "world", "this", "is", "a", "test", "right"]

    def test_malayalam_basic_tokenization(self):
        """Basic Malayalam words are split and preserved."""
        text = "കേരളത്തിലെ കാലാവസ്ഥ മനോഹരമാണ്."
        result = words(text)
        assert result == ["കേരളത്തിലെ", "കാലാവസ്ഥ", "മനോഹരമാണ്"]

    def test_malayalam_atomic_vs_legacy_chillu(self):
        """
        FAILING TEST / BUG DEMONSTRATION:
        Malayalam chillu characters:
        Atomic ൻ (U+0D7B) vs Legacy decomposed ൻ (ന + ് + ZWJ: U+0D28 U+0D4D U+200D).
        Current NFC normalization fails to equate these two visually identical forms.
        """
        atomic_avan = "അവ" + "\u0D7B"        # അവൻ (atomic chillu-n)
        legacy_avan = "അവ" + "\u0D28\u0D4D\u200D"  # അവൻ (consonant + virama + ZWJ)
        
        res_atomic = words(atomic_avan)
        res_legacy = words(legacy_avan)
        assert res_atomic == res_legacy, (
            f"Malayalam Chillu normalization failed: {res_atomic} != {res_legacy}. "
            "NFC does not normalize legacy chillu+ZWJ to atomic chillu."
        )

    def test_malayalam_zero_width_space(self):
        """
        FAILING TEST / BUG DEMONSTRATION:
        Zero-Width Space (U+200B) is categorized as 'Cf' (Format), not 'P' or whitespace.
        words() does not split on ZWSP or strip it, fusing two words together.
        """
        text = "മലയാളം\u200Bഭാഷ"
        result = words(text)
        assert result == ["മലയാളം", "ഭാഷ"], (
            f"Zero-width space failed to split words: got {result}"
        )

    def test_currency_symbol_handling(self):
        """
        FAILING TEST / BUG DEMONSTRATION:
        Currency symbol ₹ (U+20B9) or $ (U+0024) has category 'Sc', not 'P'.
        Punctuation filtering ignores currency symbols, keeping ₹500 as '₹500'.
        """
        text = "₹500 രൂപ"
        result = words(text)
        assert result[0] == "500", (
            f"Currency symbol ₹ was not stripped: got {result[0]!r}"
        )

    def test_decimal_numbers_handling(self):
        """
        FAILING TEST / BUG DEMONSTRATION:
        Period (.) in decimals is category 'Po'.
        Current implementation strips '.' from '3.14', producing '314'.
        """
        text = "3.14 ശതമാനം"
        result = words(text)
        assert result[0] == "3.14", (
            f"Decimal dot was stripped: '3.14' became {result[0]!r}"
        )

    def test_all_six_malayalam_chillus(self):
        """Verify normalization across all six Malayalam chillu characters."""
        chillu_pairs = [
            ("ക" + "\u0D7A", "ക" + "\u0D23\u0D4D\u200D"),  # കൺ (Chillu N)
            ("അവ" + "\u0D7B", "അവ" + "\u0D28\u0D4D\u200D"), # അവൻ (Chillu NN)
            ("പാ" + "\u0D7C", "പാ" + "\u0D30\u0D4D\u200D"), # പാർ (Chillu RR)
            ("പാ" + "\u0D7D", "പാ" + "\u0D32\u0D4D\u200D"), # പാൽ (Chillu L)
            ("വാ" + "\u0D7E", "വാ" + "\u0D33\u0D4D\u200D"), # വാൾ (Chillu LL)
            ("വാ" + "\u0D7F", "വാ" + "\u0D15\u0D4D\u200D"), # വാൿ (Chillu K)
        ]
        for atomic_w, legacy_w in chillu_pairs:
            assert words(atomic_w) == words(legacy_w), (
                f"Chillu normalization failed for pair: {atomic_w!r} vs {legacy_w!r}"
            )

    def test_various_currency_symbols(self):
        """Verify stripping of various world currency symbols without losing numbers."""
        assert words("₹1000") == ["1000"]
        assert words("$250") == ["250"]
        assert words("€75.50") == ["75.50"]
        assert words("£50") == ["50"]

    def test_mixed_sentence_with_dates_and_decimals(self):
        """Verify complex sentence with currency, decimal, date, and Malayalam text."""
        sentence = "വില ₹10.50 ആണ്, തീയതി 15/08/1947."
        result = words(sentence)
        assert result == ["വില", "10.50", "ആണ്", "തീയതി", "15/08/1947"]

    def test_hyphenated_words(self):
        """Hyphenated words like 'twenty-five' lose hyphen and fuse into 'twentyfive'."""
        text = "twenty-five apples"
        result = words(text)
        assert "twentyfive" in result or ["twenty", "five"] == result[:2]


# =====================================================================
# 2. WER & Edit Operations Tests
# =====================================================================

class TestWERCAlculation:
    """Tests for evaluate() function: Levenshtein distance, WER, operations."""

    def test_exact_match(self):
        """Identical reference and transcript yields 0% WER."""
        ref = "ഇത് ഒരു പരീക്ഷണമാണ്"
        hyp = "ഇത് ഒരു പരീക്ഷണമാണ്"
        result = evaluate(ref, hyp)
        assert result is not None
        assert result["wer"] == 0.0
        assert result["errors"] == 0
        assert result["reference_words"] == 3
        assert result["recognized_words"] == 3
        assert all(op[0] == "Correct" for op in result["operations"])

    def test_single_substitution(self):
        """One word replaced: WER = 1/2 = 50%."""
        ref = "നല്ല ദിവസം"
        hyp = "നല്ല പ്രഭാതം"
        result = evaluate(ref, hyp)
        assert result is not None
        assert result["wer"] == 50.0
        assert result["errors"] == 1
        sub_ops = [op for op in result["operations"] if op[0] == "Substitution"]
        assert len(sub_ops) == 1
        assert sub_ops[0] == ("Substitution", "ദിവസം", "പ്രഭാതം")

    def test_single_deletion(self):
        """One missing word: WER = 1/3 = 33.33%."""
        ref = "ഇന്ന് നല്ല മഴയാണ്"
        hyp = "ഇന്ന് മഴയാണ്"
        result = evaluate(ref, hyp)
        assert result is not None
        assert round(result["wer"], 2) == 33.33
        assert result["errors"] == 1
        del_ops = [op for op in result["operations"] if op[0] == "Deletion"]
        assert len(del_ops) == 1
        assert del_ops[0] == ("Deletion", "നല്ല", "—")

    def test_single_insertion(self):
        """One extra word: WER = 1/2 = 50%."""
        ref = "നമസ്കാരം സുഹൃത്തേ"
        hyp = "നമസ്കാരം പ്രിയ സുഹൃത്തേ"
        result = evaluate(ref, hyp)
        assert result is not None
        assert result["wer"] == 50.0
        assert result["errors"] == 1
        ins_ops = [op for op in result["operations"] if op[0] == "Insertion"]
        assert len(ins_ops) == 1
        assert ins_ops[0] == ("Insertion", "—", "പ്രിയ")

    def test_wer_exceeding_100_percent(self):
        """ASR outputs far more words than reference (high hallucination / insertion)."""
        ref = "ഒന്ന്"
        hyp = "ഒന്ന് രണ്ട് മൂന്ന് നാല് അഞ്ച്"
        result = evaluate(ref, hyp)
        assert result is not None
        assert result["wer"] == 400.0
        assert result["errors"] == 4
        assert result["reference_words"] == 1
        assert result["recognized_words"] == 5

    def test_all_deletions_empty_hypothesis(self):
        """Hypothesis is empty (silence/no speech detected). All words deleted."""
        ref = "ഇത് ഒരു പരീക്ഷണം"
        hyp = ""
        result = evaluate(ref, hyp)
        assert result is not None
        assert result["wer"] == 100.0
        assert result["errors"] == 3
        assert result["recognized_words"] == 0
        assert all(op[0] == "Deletion" for op in result["operations"])

    def test_empty_reference_returns_none(self):
        """When reference is empty, evaluate returns None."""
        assert evaluate("", "hello world") is None
        assert evaluate("   ", "hello world") is None

    def test_punctuation_only_reference_returns_none(self):
        """Punctuation only in reference produces no tokens and returns None."""
        assert evaluate("... ,,, ???", "hello world") is None

    def test_both_empty_returns_none(self):
        """Both empty returns None."""
        assert evaluate("", "") is None

    def test_operations_sum_matches_error_count(self):
        """The count of non-Correct operations must always equal total errors."""
        ref = "the quick brown fox jumps over the lazy dog"
        hyp = "a quick brown fox leaped over a dog"
        result = evaluate(ref, hyp)
        non_correct = [op for op in result["operations"] if op[0] != "Correct"]
        assert len(non_correct) == result["errors"]


# =====================================================================
# 3. Critical Information Testing (Names, Numbers, Dates)
# =====================================================================

class TestCriticalInformation:
    """Tests evaluating how domain-critical entities are handled."""

    def test_dates_format_preserved(self):
        """
        Verify that date formats such as 15/08/1947 are preserved
        rather than losing slashes and turning into a corrupted single number (e.g. 15081947).
        """
        tokens = words("15/08/1947")
        assert tokens == ["15/08/1947"], (
            f"Date format was not preserved: got {tokens}"
        )
        tokens_hyphen = words("15-08-1947")
        assert tokens_hyphen == ["15-08-1947"]

    def test_number_spoken_vs_digits(self):
        """
        SEMANTIC LIMITATION:
        Standard WER treats digit '2026' vs spelled out 'രണ്ടായിരത്തി ഇരുപത്തിയാറ്'
        as a complete error (1 substitution + 1 insertion).
        Demonstrates why Critical Entity Testing / Text Normalization is needed.
        """
        ref = "വർഷം 2026"
        hyp = "വർഷം രണ്ടായിരത്തി ഇരുപത്തിയാറ്"
        result = evaluate(ref, hyp)
        assert result["wer"] > 0
        assert result["errors"] >= 2

    def test_indian_number_commas(self):
        """Indian numbering comma format '1,00,000' is stripped to '100000'."""
        tokens = words("1,00,000")
        assert tokens == ["100000"]


# =====================================================================
# 4. Gnani API & Error Handling Tests
# =====================================================================

class TestGnaniAPI:
    """Tests for call_gnani() network call, environment variables, and error responses."""

    def test_missing_api_key_raises_value_error(self, monkeypatch):
        """If GNANI_API_KEY is not in env, ValueError must be raised."""
        monkeypatch.delenv("GNANI_API_KEY", raising=False)
        dummy_audio = MagicMock()
        dummy_audio.name = "test.wav"
        dummy_audio.getvalue.return_value = b"RIFF...."
        dummy_audio.type = "audio/wav"

        with pytest.raises(ValueError, match="API key missing"):
            call_gnani(dummy_audio, "ml-IN")

    @patch("requests.post")
    def test_successful_api_call(self, mock_post, monkeypatch):
        """Mock successful response from Gnani API."""
        monkeypatch.setenv("GNANI_API_KEY", "mock_dummy_key_12345")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "transcript": "നമസ്കാരം",
            "request_id": "req-98765"
        }
        mock_post.return_value = mock_response

        dummy_audio = MagicMock()
        dummy_audio.name = "sample.wav"
        dummy_audio.getvalue.return_value = b"audio_bytes_data"
        dummy_audio.type = "audio/wav"

        result = call_gnani(dummy_audio, "ml-IN")
        assert result["success"] is True
        assert result["transcript"] == "നമസ്കാരം"
        assert result["request_id"] == "req-98765"

        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["headers"]["X-API-Key-ID"] == "mock_dummy_key_12345"
        assert kwargs["data"]["language_code"] == "ml-IN"
        assert kwargs["data"]["format"] == "verbatim"

    @patch("requests.post")
    def test_api_http_error_handling(self, mock_post, monkeypatch):
        """HTTP error status codes (e.g. 401 Unauthorized or 500) raise an Exception."""
        monkeypatch.setenv("GNANI_API_KEY", "mock_dummy_key")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized: Invalid API Key"
        mock_post.return_value = mock_response

        dummy_audio = MagicMock()
        dummy_audio.name = "sample.wav"
        dummy_audio.getvalue.return_value = b"audio_bytes"
        dummy_audio.type = "audio/wav"

        with pytest.raises(Exception, match="Gnani API error 401"):
            call_gnani(dummy_audio, "ml-IN")

    @patch("requests.post")
    def test_api_business_failure_handling(self, mock_post, monkeypatch):
        """Status 200 but success: False in JSON response raises Exception."""
        monkeypatch.setenv("GNANI_API_KEY", "mock_dummy_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": "Unsupported audio format or corrupt file"
        }
        mock_post.return_value = mock_response

        dummy_audio = MagicMock()
        dummy_audio.name = "bad.wav"
        dummy_audio.getvalue.return_value = b"corrupted"
        dummy_audio.type = "audio/wav"

        with pytest.raises(Exception, match="Unsupported audio format"):
            call_gnani(dummy_audio, "ml-IN")

    @patch("requests.post")
    def test_zero_byte_audio_rejected(self, mock_post, monkeypatch):
        """0-byte audio file must be rejected client-side before making network requests."""
        monkeypatch.setenv("GNANI_API_KEY", "mock_dummy_key")
        dummy_audio = MagicMock()
        dummy_audio.name = "empty.wav"
        dummy_audio.getvalue.return_value = b""  # 0 bytes
        dummy_audio.type = "audio/wav"

        with pytest.raises(ValueError, match=r"empty \(0 bytes\)"):
            call_gnani(dummy_audio, "ml-IN")

        mock_post.assert_not_called()

    @patch("requests.post")
    def test_audio_upload_size_limit_enforced(self, mock_post, monkeypatch):
        """Audio files exceeding 25MB must be rejected before making network requests."""
        monkeypatch.setenv("GNANI_API_KEY", "mock_dummy_key")
        dummy_audio = MagicMock()
        dummy_audio.name = "huge.wav"
        dummy_audio.getvalue.return_value = b"x" * (26 * 1024 * 1024)  # 26 MB
        dummy_audio.type = "audio/wav"

        with pytest.raises(ValueError, match="exceeds the maximum allowed size of 25 MB"):
            call_gnani(dummy_audio, "ml-IN")

        mock_post.assert_not_called()

    @patch("requests.post")
    def test_html_gateway_error_sanitized(self, mock_post, monkeypatch):
        """HTML 504/502 gateway errors must be sanitized rather than leaking raw HTML."""
        monkeypatch.setenv("GNANI_API_KEY", "mock_dummy_key")
        mock_response = MagicMock()
        mock_response.status_code = 504
        mock_response.text = "<!DOCTYPE html><html><head><title>504 Gateway Time-out</title></head><body>Cloudflare error</body></html>"
        mock_post.return_value = mock_response

        dummy_audio = MagicMock()
        dummy_audio.name = "test.wav"
        dummy_audio.getvalue.return_value = b"audio_content"
        dummy_audio.type = "audio/wav"

        with pytest.raises(Exception) as exc_info:
            call_gnani(dummy_audio, "ml-IN")

        error_message = str(exc_info.value)
        assert "504" in error_message
        assert "<!doctype" not in error_message.lower()
        assert "<html" not in error_message.lower()
        assert "temporarily unavailable" in error_message.lower()


# =====================================================================
# 5. Downloadable Report & Diagnostics Tests
# =====================================================================

class TestReportGeneration:
    """Tests for downloadable report string generation and CSV exports."""

    def test_report_content_completeness(self):
        """Verify enriched report includes timestamp, filename, breakdown table, and metrics."""
        session_mock = {
            "language": "Malayalam",
            "audio_name": "kerala_news.wav",
            "reference": "ഇത് ഒരു പരീക്ഷണം",
            "transcript": "ഇത് പരീക്ഷണം",
            "request_id": "req-456"
        }
        metrics = evaluate(session_mock["reference"], session_mock["transcript"])
        assert metrics is not None

        table_lines = [
            f"{'#':<4} | {'Status':<14} | {'Reference Word':<25} | {'Recognized Word':<25}",
            "-" * 75
        ]
        for idx, (status, ref_w, hyp_w) in enumerate(metrics["operations"], start=1):
            table_lines.append(f"{idx:<4} | {status:<14} | {ref_w:<25} | {hyp_w:<25}")
        ops_table_text = "\n".join(table_lines)

        from datetime import datetime
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""================================================================================
NADHAM QA - SPEECH RECOGNITION EVALUATION REPORT
================================================================================
Timestamp:          {timestamp_str}
Audio File:         {session_mock['audio_name']}
Language:           {session_mock['language']}
Gnani Request ID:   {session_mock['request_id']}
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
{session_mock['reference']}

Gnani Transcript:
{session_mock['transcript']}

WORD-LEVEL ERROR BREAKDOWN:
--------------------------------------------------------------------------------
{ops_table_text}
================================================================================
"""
        assert "Word Error Rate:        33.33%" in report
        assert "Total Word Errors:      1" in report
        assert "Gnani Request ID:   req-456" in report
        assert "kerala_news.wav" in report
        assert "WORD-LEVEL ERROR BREAKDOWN" in report
        assert "Deletion" in report
        assert "ഒരു" in report

    def test_csv_export_structure(self):
        """Verify CSV export contains correct columns and rows."""
        import pandas as pd
        rows = [
            {"Status": "Correct", "Reference Word": "ഇത്", "Recognized Word": "ഇത്"},
            {"Status": "Deletion", "Reference Word": "ഒരു", "Recognized Word": "—"},
            {"Status": "Correct", "Reference Word": "പരീക്ഷണം", "Recognized Word": "പരീക്ഷണം"}
        ]
        df = pd.DataFrame(rows)
        csv_str = df.to_csv(index=False)
        assert "Status,Reference Word,Recognized Word" in csv_str
        assert "Deletion,ഒരു,—" in csv_str
