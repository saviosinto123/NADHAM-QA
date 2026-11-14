import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import pytest

# Ensure the app directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import (
    words, evaluate, call_gnani, get_api_key, characters, evaluate_cer,
    extract_critical_entities, compare_critical_entities,
    analyze_audio_quality, compare_clean_noisy,
    generate_comparison_txt_report, generate_comparison_csv,
    extract_sample_id, discover_benchmark_dataset, evaluate_benchmark_batch,
    generate_benchmark_summary_txt, generate_benchmark_sample_csv, generate_benchmark_aggregate_csv
)


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
# 3. Character Error Rate (CER) Tests (Unicode Grapheme Clusters)
# =====================================================================

class TestCERCalculation:
    """Tests for evaluate_cer() and characters() Unicode grapheme cluster segmentation."""

    def test_cer_exact_match(self):
        """Identical reference and hypothesis yields 0.0% CER."""
        ref = "മലയാളം"
        hyp = "മലയാളം"
        res = evaluate_cer(ref, hyp)
        assert res is not None
        assert res["cer"] == 0.0
        assert res["errors"] == 0
        assert res["reference_chars"] == 4
        assert res["recognized_chars"] == 4
        assert all(op[0] == "Correct" for op in res["operations"])

    def test_cer_single_substitution(self):
        """One grapheme substituted: 1 / 4 = 25.0% CER."""
        ref = "മലയാളം"
        hyp = "തലയാളം"
        res = evaluate_cer(ref, hyp)
        assert res is not None
        assert res["cer"] == 25.0
        assert res["errors"] == 1
        assert res["substitutions"] == 1
        assert res["deletions"] == 0
        assert res["insertions"] == 0

    def test_cer_single_deletion(self):
        """One grapheme missing: 1 / 4 = 25.0% CER."""
        ref = "മലയാളം"
        hyp = "മയാളം"
        res = evaluate_cer(ref, hyp)
        assert res is not None
        assert res["cer"] == 25.0
        assert res["errors"] == 1
        assert res["deletions"] == 1

    def test_cer_single_insertion(self):
        """One grapheme inserted: 1 / 2 = 50.0% CER."""
        ref = "മഴ"
        hyp = "മഴവ"
        res = evaluate_cer(ref, hyp)
        assert res is not None
        assert res["cer"] == 50.0
        assert res["errors"] == 1
        assert res["insertions"] == 1

    def test_cer_empty_hypothesis(self):
        """Empty hypothesis (no recognized speech) yields 100% CER (all deletions)."""
        ref = "കേരളം"
        hyp = ""
        res = evaluate_cer(ref, hyp)
        assert res is not None
        assert res["cer"] == 100.0
        assert res["errors"] == 3
        assert res["deletions"] == 3
        assert res["recognized_chars"] == 0

    def test_cer_empty_reference_returns_none(self):
        """Empty or punctuation-only reference safely returns None (avoids division by zero)."""
        assert evaluate_cer("", "മലയാളം") is None
        assert evaluate_cer("   ", "മലയാളം") is None
        assert evaluate_cer("... ,,, ???", "മലയാളം") is None

    def test_cer_malayalam_full_sentence(self):
        """Full Malayalam sentence exact match."""
        sent = "കേരളത്തിലെ കാലാവസ്ഥ മനോഹരമാണ്."
        res = evaluate_cer(sent, sent)
        assert res is not None
        assert res["cer"] == 0.0
        assert res["errors"] == 0

    def test_cer_malayalam_combining_characters(self):
        """Combining vowel signs, viramas and anusvaras bind into single grapheme clusters."""
        # 'നമസ്കാരം': ന (base), മ (base), സ് (virama), കാ (vowel sign), രം (anusvara) = 5 graphemes
        word = "നമസ്കാരം"
        chars = characters(word)
        assert chars == ["ന", "മ", "സ്", "കാ", "രം"]
        res = evaluate_cer(word, word)
        assert res["reference_chars"] == 5
        assert res["cer"] == 0.0

    def test_cer_atomic_vs_legacy_chillu(self):
        """Atomic chillu (U+0D7B) vs legacy decomposed chillu (U+0D28 U+0D4D U+200D) yields 0% CER."""
        atomic_avan = "അവ" + "\u0D7B"
        legacy_avan = "അവ" + "\u0D28\u0D4D\u200D"
        res = evaluate_cer(atomic_avan, legacy_avan)
        assert res is not None
        assert res["cer"] == 0.0
        assert res["errors"] == 0
        assert res["reference_chars"] == 3

    def test_cer_zero_width_characters(self):
        """Text with Zero-Width Spaces (ZWSP) normalizes cleanly with 0% CER."""
        text_zwsp = "മലയാളം\u200Bഭാഷ"
        text_norm = "മലയാളം ഭാഷ"
        res = evaluate_cer(text_zwsp, text_norm)
        assert res is not None
        assert res["cer"] == 0.0
        assert res["errors"] == 0

    def test_cer_exceeding_100_percent(self):
        """High insertion/hallucination rates can legitimately produce CER > 100%."""
        ref = "ആ"
        hyp = "ആകാശം"
        res = evaluate_cer(ref, hyp)
        assert res is not None
        assert res["cer"] == 200.0
        assert res["errors"] == 2
        assert res["insertions"] == 2

    def test_whitespace_exclusion_policy(self):
        """Whitespace is excluded from grapheme cluster count so word segmentation does not inflate CER."""
        ref = "വീട്ടിൽ പോയി"
        chars = characters(ref)
        # 'വീ' (1), 'ട്' (2), 'ടി' (3), 'ൽ' (4), 'പോ' (5), 'യി' (6)
        assert len(chars) == 6
        assert chars == ["വീ", "ട്", "ടി", "ൽ", "പോ", "യി"]
        # Word with space vs conjoined has matching grapheme count
        assert len(characters("വീട്ടിൽ")) + len(characters("പോയി")) == len(chars)


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

    def test_exact_number_match(self):
        """Exact numeric entity matching."""
        res = compare_critical_entities("Count is 42 items", "Count is 42 items")
        assert res["total_items"] == 1
        assert res["matching_items"] == 1
        assert res["accuracy"] == 100.0
        assert res["details"][0]["Status"] == "Match"

    def test_changed_number(self):
        """Changed numeric value detected."""
        res = compare_critical_entities("Price is 100", "Price is 200")
        assert res["total_items"] == 1
        assert res["changed_items"] == 1
        assert res["details"][0]["Status"] == "Changed"
        assert res["details"][0]["Reference Value"] == "100"
        assert res["details"][0]["Recognized Value"] == "200"

    def test_missing_number(self):
        """Number in reference omitted in transcription."""
        res = compare_critical_entities("Room 504 is ready", "Room is ready")
        assert res["total_items"] == 1
        assert res["missing_items"] == 1
        assert res["details"][0]["Status"] == "Missing"

    def test_extra_number(self):
        """Spurious number hallucinated in transcription."""
        res = compare_critical_entities("Room is ready", "Room 504 is ready")
        assert res["total_items"] == 0
        assert res["extra_items"] == 1
        assert res["details"][0]["Status"] == "Extra"

    def test_changed_currency_amount(self):
        """Currency amount discrepancy properly categorized as Currency."""
        res = compare_critical_entities("വില ₹500 ആണ്", "വില ₹5000 ആണ്")
        assert res["total_items"] == 1
        assert res["changed_items"] == 1
        assert res["details"][0]["Category"] == "Currency"
        assert res["details"][0]["Status"] == "Changed"

    def test_indian_comma_formatting_match(self):
        """Indian comma format (1,00,000) matches unformatted 100000 in Currency or Number."""
        res = compare_critical_entities("തുക ₹1,00,000 രൂപ", "തുക ₹100000 രൂപ")
        assert res["matching_items"] == 1
        assert res["details"][0]["Status"] == "Match"

    def test_date_match_and_mismatch(self):
        """Date formats match across separators (- vs /) and detect mismatches."""
        res_m = compare_critical_entities("തീയതി 15/11/2026", "തീയതി 15-11-2026")
        assert res_m["matching_items"] == 1
        assert res_m["details"][0]["Status"] == "Match"

        res_diff = compare_critical_entities("തീയതി 15/11/2026", "തീയതി 20/11/2026")
        assert res_diff["changed_items"] == 1
        assert res_diff["details"][0]["Status"] == "Changed"

    def test_time_match_and_mismatch(self):
        """Time formats match case-insensitively and detect hour/minute changes."""
        res_m = compare_critical_entities("സമയം 10:30 AM", "സമയം 10:30 am")
        assert res_m["matching_items"] == 1

        res_diff = compare_critical_entities("സമയം 10:30 AM", "സമയം 11:30 AM")
        assert res_diff["changed_items"] == 1

    def test_phone_number_mismatch(self):
        """Indian mobile number digit changes detected."""
        res = compare_critical_entities("വിളിക്കുക 9876543210", "വിളിക്കുക 9876543219")
        assert res["changed_items"] == 1
        assert res["details"][0]["Category"] == "Phone Number"

    def test_english_negation_mismatch(self):
        """English negation omission detected as Missing critical entity."""
        res = compare_critical_entities("I do not agree with this", "I do agree with this")
        assert res["missing_items"] == 1
        assert res["details"][0]["Category"] == "Negation"
        assert res["details"][0]["Reference Value"] == "not"

    def test_malayalam_negation_explicit_patterns(self):
        """Malayalam negation omission detected for explicit verbal patterns."""
        res1 = compare_critical_entities("ഇത് ശരിയല്ല", "ഇത് ശരിയാണ്")
        assert res1["missing_items"] == 1
        assert res1["details"][0]["Category"] == "Negation"

        res2 = compare_critical_entities("അവിടെ പോകരുത്", "അവിടെ പോകൂ")
        assert res2["missing_items"] == 1
        assert res2["details"][0]["Category"] == "Negation"

    def test_empty_reference_and_recognized_text(self):
        """Empty inputs produce zero critical items safely."""
        res = compare_critical_entities("", "")
        assert res["total_items"] == 0
        assert res["details"] == []

    def test_false_positive_handling(self):
        """Arbitrary large numbers (not matching mobile phone prefixes) remain Numbers, not Phones."""
        entities = extract_critical_entities("Order ID 1000000000")
        assert len(entities) == 1
        assert entities[0]["category"] == "Number"

    def test_known_name_detection(self):
        """Proper nouns from dataset context are compared reliably."""
        res = compare_critical_entities("എൻ്റെ പേര് സാവിയോ എന്നാണ്", "എൻ്റെ പേര് സാജു എന്നാണ്")
        assert res["changed_items"] == 1
        assert res["details"][0]["Category"] == "Name"

    def test_location_not_mislabeled_as_name(self):
        """Geographical location 'കേരളം' (Kerala) must not be mislabeled as person Name."""
        entities = extract_critical_entities("കേരളം സുന്ദരമാണ്")
        name_entities = [e for e in entities if e["category"] == "Name"]
        assert len(name_entities) == 0

    def test_two_pass_alignment_priority(self):
        """Exact matches are prioritized over greedy Changed pairings."""
        res = compare_critical_entities("Price is 999 and discount is 20", "Price is 20")
        assert res["matching_items"] == 1
        assert res["missing_items"] == 1
        assert res["changed_items"] == 0
        status_by_val = {row["Reference Value"]: row["Status"] for row in res["details"]}
        assert status_by_val["20"] == "Match"
        assert status_by_val["999"] == "Missing"

    def test_currency_not_double_counted_as_number(self):
        """Currency entity does not produce a redundant Number entity."""
        entities = extract_critical_entities("ആകെ ₹500 ആണ്")
        assert len(entities) == 1
        assert entities[0]["category"] == "Currency"

    def test_date_and_time_not_double_counted_as_numbers(self):
        """Date and time values do not produce redundant generic numbers."""
        entities = extract_critical_entities("On 15/11/2026 at 10:30 AM")
        categories = [e["category"] for e in entities]
        assert "Number" not in categories
        assert "Date" in categories
        assert "Time" in categories


# =====================================================================
# 4. Gnani API & Error Handling Tests
# =====================================================================

class TestGnaniAPI:
    """Tests for call_gnani() network call, environment variables, and error responses."""

    def test_get_api_key_env_precedence(self, monkeypatch):
        """get_api_key() prioritizes environment variable when present."""
        monkeypatch.setenv("GNANI_API_KEY", "mock_env_key_xyz")
        assert get_api_key() == "mock_env_key_xyz"

    def test_get_api_key_streamlit_secrets_fallback(self, monkeypatch):
        """get_api_key() falls back safely to st.secrets if env variable is absent."""
        import streamlit as st
        monkeypatch.delenv("GNANI_API_KEY", raising=False)
        with patch.object(st, "secrets", {"GNANI_API_KEY": "mock_st_secret_abc"}):
            assert get_api_key() == "mock_st_secret_abc"

    def test_get_api_key_missing_both_returns_none(self, monkeypatch):
        """get_api_key() returns None when neither env nor st.secrets contains the key."""
        import streamlit as st
        monkeypatch.delenv("GNANI_API_KEY", raising=False)
        with patch.object(st, "secrets", {}, create=True):
            assert get_api_key() is None

    def test_missing_api_key_raises_value_error(self, monkeypatch):
        """If GNANI_API_KEY is missing everywhere, ValueError must be raised."""
        import streamlit as st
        monkeypatch.delenv("GNANI_API_KEY", raising=False)
        with patch.object(st, "secrets", {}, create=True):
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


# =====================================================================
# 6. Audio Quality Analysis Tests (Step 4)
# =====================================================================

def make_test_wav(duration_s=1.0, sr=16000, channels=1, sampwidth=2, frequency=440.0, amplitude=0.5, silence=False, clip=False):
    """Helper fixture to generate in-memory PCM WAV bytes for acoustic tests."""
    import io, wave, numpy as np
    n_samples = int(duration_s * sr)
    if n_samples == 0:
        samples = np.zeros(0, dtype=np.float32)
    elif silence:
        samples = np.zeros(n_samples, dtype=np.float32)
    else:
        t = np.linspace(0, duration_s, n_samples, endpoint=False)
        sine = np.sin(2 * np.pi * frequency * t) * (1.5 if clip else amplitude)
        if clip:
            sine = np.clip(sine, -1.0, 1.0)
        samples = sine

    if channels > 1 and n_samples > 0:
        samples = np.column_stack([samples] * channels)

    int_samples = np.clip(samples * 32767, -32768, 32767).astype(np.int16)
    bio = io.BytesIO()
    with wave.open(bio, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sr)
        wf.writeframes(int_samples.tobytes())
    return bio.getvalue()


class TestAudioQualityAnalysis:
    """Tests for analyze_audio_quality() local acoustic measurements."""

    def test_valid_pcm_wav_metadata(self):
        """Standard 16kHz mono PCM WAV extracts duration, sample rate, channels correctly."""
        wav_bytes = make_test_wav(duration_s=2.5, sr=16000, channels=1)
        res = analyze_audio_quality(wav_bytes, filename="speech.wav")
        assert res["supported"] is True
        assert res["duration_s"] == 2.5
        assert res["sample_rate"] == 16000
        assert res["channels"] == 1
        assert res["channels_desc"] == "Mono"
        assert res["clipping_pct"] == 0.0
        assert res["silence_pct"] == 0.0

    def test_stereo_wav_metadata(self):
        """Stereo 44.1kHz PCM WAV correctly reports 2 channels and Stereo descriptor."""
        wav_bytes = make_test_wav(duration_s=1.0, sr=44100, channels=2)
        res = analyze_audio_quality(wav_bytes, filename="stereo.wav")
        assert res["supported"] is True
        assert res["channels"] == 2
        assert res["channels_desc"] == "Stereo"
        assert res["sample_rate"] == 44100

    def test_unsupported_audio_format_mp3(self):
        """Non-WAV compressed formats (MP3) return supported=False safely without crashing."""
        mp3_simulated = b"ID3\x04\x00\x00\x00\x00\x00\x23TIT2\x00\x00\x00\x09\x00\x00\x03TestSong"
        res = analyze_audio_quality(mp3_simulated, filename="recording.mp3")
        assert res["supported"] is False
        assert "requires uncompressed PCM WAV" in res["error"]
        assert res["duration_s"] is None

    def test_empty_and_none_audio(self):
        """Empty audio (0 bytes) and None input safely return supported=False."""
        res_empty = analyze_audio_quality(b"")
        assert res_empty["supported"] is False
        assert "empty (0 bytes)" in res_empty["error"]

        res_none = analyze_audio_quality(None)
        assert res_none["supported"] is False
        assert "No audio data" in res_none["error"]

    def test_malformed_wav_data(self):
        """Corrupted or truncated WAV header returns supported=False safely without raising."""
        malformed = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00truncated"
        res = analyze_audio_quality(malformed, filename="corrupt.wav")
        assert res["supported"] is False
        assert "requires uncompressed PCM WAV" in res["error"]

    def test_clipping_detection(self):
        """Saturated waveforms exceeding threshold produce measured clipping percentage."""
        wav_clipped = make_test_wav(duration_s=1.0, sr=16000, clip=True)
        res = analyze_audio_quality(wav_clipped)
        assert res["supported"] is True
        assert res["clipping_pct"] > 5.0

    def test_silence_percentage_calculation(self):
        """Audio with 50% silence produces exactly 50% measured silence percentage."""
        import io, wave, numpy as np
        sr = 16000
        silence_samples = np.zeros(sr, dtype=np.float32)
        t = np.linspace(0, 1, sr, endpoint=False)
        tone_samples = np.sin(2 * np.pi * 440 * t) * 0.5
        combined = np.concatenate([silence_samples, tone_samples])
        int_samples = (combined * 32767).astype(np.int16)

        bio = io.BytesIO()
        with wave.open(bio, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(int_samples.tobytes())

        res = analyze_audio_quality(bio.getvalue())
        assert res["supported"] is True
        assert res["duration_s"] == 2.0
        assert res["silence_pct"] == 50.0

    def test_zero_duration_wav(self):
        """WAV file with valid headers but 0 frames returns 0.0s duration safely."""
        wav_zero = make_test_wav(duration_s=0.0, sr=16000)
        res = analyze_audio_quality(wav_zero)
        assert res["supported"] is True
        assert res["duration_s"] == 0.0


# =====================================================================
# 7. Clean vs Noisy Comparison Tests (Step 4)
# =====================================================================

class TestCleanNoisyComparison:
    """Tests for compare_clean_noisy() benchmark engine and reporting."""

    def test_clean_better_than_noisy_wer(self):
        """Clean transcript with fewer errors correctly identifies Clean as better."""
        ref = "നമസ്കാരം സുഹൃത്തേ ഇന്ന് നല്ലൊരു ദിവസമാണ്"
        clean_hyp = "നമസ്കാരം സുഹൃത്തേ ഇന്ന് നല്ലൊരു ദിവസമാണ്" # 0% WER
        noisy_hyp = "നമസ്കാരം സുഹൃത്തേ ഇന്ന് നല്ലൊരു ദിവസം"    # 20% WER

        res = compare_clean_noisy(ref, clean_hyp, noisy_hyp)
        assert res["clean_wer"] == 0.0
        assert res["noisy_wer"] == 20.0
        assert res["delta_wer"] == 20.0
        assert res["clean_errors"] == 0
        assert res["noisy_errors"] == 1
        assert res["delta_errors"] == 1
        assert res["better_recording"] == "clean"
        assert "Clean recording performed better" in res["interpretation"]

    def test_inverse_result_noisy_better(self):
        """Noisy transcript with fewer errors correctly identifies Noisy without bias."""
        ref = "വില ₹500 രൂപയാണ്"
        clean_hyp = "വില രൂപയാണ്"       # Missing 500
        noisy_hyp = "വില ₹500 രൂപയാണ്" # Exact match

        res = compare_clean_noisy(ref, clean_hyp, noisy_hyp)
        assert res["clean_wer"] > res["noisy_wer"]
        assert res["delta_wer"] < 0
        assert res["better_recording"] == "noisy"
        assert "Noisy recording achieved" in res["interpretation"]

    def test_identical_recordings_tie(self):
        """Equal performance across both recordings yields a tie outcome."""
        ref = "കേരളം സുന്ദരമാണ്"
        res = compare_clean_noisy(ref, "കേരളം സുന്ദരമാണ്", "കേരളം സുന്ദരമാണ്")
        assert res["better_recording"] == "tie"
        assert res["delta_wer"] == 0.0
        assert res["delta_cer"] == 0.0
        assert "Identical performance" in res["interpretation"]

    def test_cer_difference_calculation(self):
        """CER difference (delta_cer) accurately tracks character edit discrepancies."""
        ref = "പരീക്ഷണം"
        clean_hyp = "പരീക്ഷണം" # 0% CER
        noisy_hyp = "പരീക്ഷ"   # Deleted ണം
        res = compare_clean_noisy(ref, clean_hyp, noisy_hyp)
        assert res["clean_cer"] == 0.0
        assert res["noisy_cer"] > 0.0
        assert res["delta_cer"] > 0.0

    def test_critical_information_comparison(self):
        """Critical entity retention discrepancies between clean and noisy are quantified."""
        ref = "തുക ₹1,00,000 ആണ് തീയതി 15/11/2026"
        clean_hyp = "തുക ₹1,00,000 ആണ് തീയതി 15/11/2026" # 100% Critical
        noisy_hyp = "തുക ₹50,000 ആണ് തീയതി"              # Changed ₹, Missing date

        res = compare_clean_noisy(ref, clean_hyp, noisy_hyp)
        assert res["clean_crit"]["accuracy"] == 100.0
        assert res["noisy_crit"]["accuracy"] < 100.0
        assert res["clean_crit"]["matching_items"] == 2
        assert res["noisy_crit"]["matching_items"] == 0

    def test_comparison_table_structure(self):
        """Comparison table includes all key metrics and acoustic parameters."""
        ref = "ടെസ്റ്റ് ഓഡിയോ"
        cq = {"supported": True, "duration_s": 2.0, "rms_dbfs": -15.0, "peak_dbfs": -3.0, "clipping_pct": 0.0, "silence_pct": 10.0}
        nq = {"supported": True, "duration_s": 2.0, "rms_dbfs": -10.0, "peak_dbfs": -1.0, "clipping_pct": 0.5, "silence_pct": 5.0}

        res = compare_clean_noisy(ref, "ടെസ്റ്റ് ഓഡിയോ", "ടെസ്റ്റ് ഓഡിയോ", cq, nq)
        metric_names = [r["Metric"] for r in res["table_rows"]]
        assert "Word Error Rate (WER)" in metric_names
        assert "Character Error Rate (CER)" in metric_names
        assert "Total Word Errors" in metric_names
        assert "Audio RMS Energy" in metric_names
        assert "Peak Amplitude" in metric_names
        assert "Clipping Percentage" in metric_names
        assert "Silence Percentage" in metric_names

    def test_comparison_txt_report(self):
        """Generated comparison TXT report contains both transcripts, interpretation, and table."""
        ref = "ഇത് ഒരു പരീക്ഷണമാണ്"
        res = compare_clean_noisy(ref, "ഇത് ഒരു പരീക്ഷണമാണ്", "ഇത് പരീക്ഷണമാണ്")
        res["clean_transcript"] = "ഇത് ഒരു പരീക്ഷണമാണ്"
        res["noisy_transcript"] = "ഇത് പരീക്ഷണമാണ്"

        report = generate_comparison_txt_report(
            res, ref, "clean.wav", "noisy.wav", "Malayalam", "req-c1", "req-n2"
        )
        assert "CLEAN VS. NOISY SPEECH RECOGNITION COMPARISON REPORT" in report
        assert "Clean Audio:        clean.wav" in report
        assert "Noisy Audio:        noisy.wav" in report
        assert "req-c1" in report
        assert "req-n2" in report
        assert "Shared Ground Truth Reference:" in report
        assert "Clean Recording Transcript:" in report
        assert "Noisy Recording Transcript:" in report

    def test_comparison_csv_export(self):
        """Generated comparison CSV export parses cleanly with matching metric rows."""
        import pandas as pd, io
        ref = "ടെസ്റ്റ്"
        res = compare_clean_noisy(ref, "ടെസ്റ്റ്", "ടെസ്റ്റ്")
        csv_bytes = generate_comparison_csv(res)
        df = pd.read_csv(io.BytesIO(csv_bytes))
        assert "Metric" in df.columns
        assert "Clean Recording" in df.columns
        assert "Noisy Recording" in df.columns
        assert "Delta (Noisy - Clean)" in df.columns
        assert len(df) >= 8

    def test_api_mock_two_requests_clean_noisy(self):
        """Verify two separate mocked API requests can be executed for clean and noisy audio."""
        class MockFile:
            def __init__(self, name, data):
                self.name = name
                self.data = data
                self.type = "audio/wav"
            def getvalue(self):
                return self.data

        clean_f = MockFile("clean.wav", b"RIFFcleanWAVE")
        noisy_f = MockFile("noisy.wav", b"RIFFnoisyWAVE")

        with patch("requests.post") as mock_post:
            resp1 = MagicMock()
            resp1.status_code = 200
            resp1.json.return_value = {"success": True, "transcript": "നമസ്കാരം", "request_id": "c-101"}

            resp2 = MagicMock()
            resp2.status_code = 200
            resp2.json.return_value = {"success": True, "transcript": "നമസ്കാരം സുഹൃത്തേ", "request_id": "n-202"}

            mock_post.side_effect = [resp1, resp2]

            res_c = call_gnani(clean_f, "ml-IN")
            res_n = call_gnani(noisy_f, "ml-IN")

            assert res_c["transcript"] == "നമസ്കാരം"
            assert res_n["transcript"] == "നമസ്കാരം സുഹൃത്തേ"
            assert mock_post.call_count == 2

    def test_empty_transcripts_clean_noisy_comparison(self):
        """Both transcripts empty safely computes 100% WER and delta_wer == 0."""
        res = compare_clean_noisy("നമസ്കാരം സുഹൃത്തേ", "", "")
        assert res["clean_wer"] == 100.0
        assert res["noisy_wer"] == 100.0
        assert res["delta_wer"] == 0.0
        assert res["better_recording"] == "tie"

    def test_empty_reference_clean_noisy_comparison(self):
        """Empty reference string returns 0.0 metrics safely without ZeroDivisionError."""
        res = compare_clean_noisy("", "നമസ്കാരം", "ഹലോ")
        assert res["clean_wer"] == 0.0
        assert res["noisy_wer"] == 0.0
        assert res["delta_wer"] == 0.0


# =====================================================================
# 11. Step 5 — Benchmark Dataset Discovery Tests
# =====================================================================

class TestBenchmarkDatasetDiscovery:
    """Tests for dataset discovery, sample ID extraction, and validation."""

    def test_extract_sample_id_extensions(self):
        """Extract clean sample IDs across various extensions and repeated suffixes."""
        assert extract_sample_id("ML_NORMAL_01.mp3.mp3") == "ML_NORMAL_01"
        assert extract_sample_id("ML_NORMAL_01.mp3.txt") == "ML_NORMAL_01"
        assert extract_sample_id("sample_test.wav") == "sample_test"
        assert extract_sample_id("path/to/nested/ML_NORMAL_05.ogg") == "ML_NORMAL_05"
        assert extract_sample_id("") == ""
        assert extract_sample_id(None) == ""

    def test_discover_benchmark_dataset_real_repo(self):
        """Discovers the 5 genuine Malayalam benchmark samples in dataset/."""
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        dataset_dir = os.path.join(repo_root, "dataset")
        info = discover_benchmark_dataset(dataset_dir)

        assert info["total_discovered"] == 5
        assert info["valid_count"] == 5
        assert info["invalid_count"] == 0
        assert info["has_paired_noise"] is False
        assert info["normal_condition_count"] == 5
        assert info["noisy_condition_count"] == 0

        expected_ids = [f"ML_NORMAL_0{i}" for i in range(1, 6)]
        discovered_ids = [s["sample_id"] for s in info["samples"]]
        assert discovered_ids == expected_ids

        for s in info["samples"]:
            assert s["status"] == "valid"
            assert s["audio_path"] is not None
            assert os.path.exists(s["audio_path"])
            assert s["audio_size_bytes"] > 0
            assert len(s["reference_transcript"]) > 0

    def test_discover_missing_audio(self, tmp_path):
        """Detects samples where reference transcript exists but audio file is missing."""
        d_dir = tmp_path / "dataset"
        t_dir = d_dir / "transcripts"
        n_dir = d_dir / "normal"
        t_dir.mkdir(parents=True)
        n_dir.mkdir(parents=True)

        (t_dir / "SAMPLE_01.txt").write_text("ടെസ്റ്റ് വാചകം", encoding="utf-8")

        info = discover_benchmark_dataset(str(d_dir))
        assert info["total_discovered"] == 1
        assert info["valid_count"] == 0
        assert info["invalid_count"] == 1
        assert info["samples"][0]["status"] == "missing_audio"

    def test_discover_missing_transcript(self, tmp_path):
        """Detects samples where audio exists but reference transcript is missing."""
        d_dir = tmp_path / "dataset"
        t_dir = d_dir / "transcripts"
        n_dir = d_dir / "normal"
        t_dir.mkdir(parents=True)
        n_dir.mkdir(parents=True)

        (n_dir / "SAMPLE_01.mp3").write_bytes(b"\xff\xfb\x90\x00")

        info = discover_benchmark_dataset(str(d_dir))
        assert info["total_discovered"] == 1
        assert info["valid_count"] == 0
        assert info["invalid_count"] == 1
        assert info["samples"][0]["status"] == "missing_transcript"

    def test_discover_empty_transcript(self, tmp_path):
        """Detects samples where transcript file exists but contains only whitespace or empty text."""
        d_dir = tmp_path / "dataset"
        t_dir = d_dir / "transcripts"
        n_dir = d_dir / "normal"
        t_dir.mkdir(parents=True)
        n_dir.mkdir(parents=True)

        (n_dir / "SAMPLE_01.mp3").write_bytes(b"\xff\xfb\x90\x00")
        (t_dir / "SAMPLE_01.txt").write_text("   \n\t  ", encoding="utf-8")

        info = discover_benchmark_dataset(str(d_dir))
        assert info["total_discovered"] == 1
        assert info["valid_count"] == 0
        assert info["invalid_count"] == 1
        assert info["samples"][0]["status"] == "empty_transcript"

    def test_discover_empty_audio(self, tmp_path):
        """Detects 0-byte empty audio files."""
        d_dir = tmp_path / "dataset"
        t_dir = d_dir / "transcripts"
        n_dir = d_dir / "normal"
        t_dir.mkdir(parents=True)
        n_dir.mkdir(parents=True)

        (n_dir / "SAMPLE_01.mp3").write_bytes(b"")
        (t_dir / "SAMPLE_01.txt").write_text("സാധുവായ ടെസ്റ്റ്", encoding="utf-8")

        info = discover_benchmark_dataset(str(d_dir))
        assert info["total_discovered"] == 1
        assert info["valid_count"] == 0
        assert info["invalid_count"] == 1
        assert info["samples"][0]["status"] == "invalid_audio"

    def test_discover_paired_noise_status_true_when_noisy_folder_present(self, tmp_path):
        """Detects paired noise availability when noisy directory contains audio."""
        d_dir = tmp_path / "dataset"
        n_dir = d_dir / "normal"
        noisy_dir = d_dir / "noisy"
        t_dir = d_dir / "transcripts"
        n_dir.mkdir(parents=True)
        noisy_dir.mkdir(parents=True)
        t_dir.mkdir(parents=True)

        (n_dir / "SAMPLE_01.mp3").write_bytes(b"\xff\xfb\x90\x00")
        (noisy_dir / "SAMPLE_01.mp3").write_bytes(b"\xff\xfb\x90\x00")
        (t_dir / "SAMPLE_01.txt").write_text("ടെസ്റ്റ്", encoding="utf-8")

        info = discover_benchmark_dataset(str(d_dir))
        assert info["has_paired_noise"] is True


# =====================================================================
# 12. Step 5 — Benchmark Batch Evaluation Tests
# =====================================================================

class TestBenchmarkBatchEvaluation:
    """Tests for batch evaluation, aggregate metric calculation, and error resilience."""

    def test_evaluate_batch_exact_aggregate_formulas(self):
        """Verify Aggregate WER and CER use global error quotients (sum of errors / sum of units)."""
        samples = [
            {
                "sample_id": "S1",
                "audio_filename": "s1.mp3",
                "audio_path": "dummy1.mp3",
                "reference_transcript": "നമസ്കാരം സുഹൃത്തേ",  # 2 words
                "status": "valid"
            },
            {
                "sample_id": "S2",
                "audio_filename": "s2.mp3",
                "audio_path": "dummy2.mp3",
                "reference_transcript": "കേരളത്തിലെ പ്രകൃതി സൗന്ദര്യം അതിമനോഹരമാണ്",  # 4 words
                "status": "valid"
            }
        ]

        def mock_caller(audio_bytes, filename="", language="Malayalam"):
            if filename == "s1.mp3":
                return {"success": True, "transcript": "നമസ്കാരം", "request_id": "REQ-1"}
            return {"success": True, "transcript": "കേരളത്തിലെ പ്രകൃതി ഭംഗി അതിമനോഹരമാണ്", "request_id": "REQ-2"}

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"dummy_audio")):
            with patch("os.path.exists", return_value=True):
                batch_res = evaluate_benchmark_batch(samples, api_caller=mock_caller)

        assert batch_res["summary"]["total_samples"] == 2
        assert batch_res["summary"]["successful_samples"] == 2
        assert batch_res["summary"]["failed_samples"] == 0
        assert batch_res["summary"]["benchmark_success_rate"] == 100.0

        # Sample 1: ref=2 words, hyp=1 word (1 deletion). errors=1, WER=50.0%
        # Sample 2: ref=4 words, hyp=4 words (1 substitution). errors=1, WER=25.0%
        # Total ref words = 2 + 4 = 6
        # Total word errors = 1 + 1 = 2
        # Exact Aggregate WER = 2 / 6 * 100 = 33.33%
        # Arithmetic mean would be (50.0 + 25.0) / 2 = 37.5%, which is NOT the aggregate WER!
        assert batch_res["aggregate"]["total_ref_words"] == 6
        assert batch_res["aggregate"]["total_word_errors"] == 2
        assert batch_res["aggregate"]["aggregate_wer"] == 33.33

        # Confirm character aggregate
        tot_ref_chars = sum(r["ref_graphemes"] for r in batch_res["sample_results"])
        tot_char_errs = sum(r["char_errors"] for r in batch_res["sample_results"])
        assert batch_res["aggregate"]["total_ref_graphemes"] == tot_ref_chars
        assert batch_res["aggregate"]["total_char_errors"] == tot_char_errs
        expected_cer = round((tot_char_errs / tot_ref_chars) * 100, 2)
        assert batch_res["aggregate"]["aggregate_cer"] == expected_cer

    def test_evaluate_batch_partial_api_failure(self):
        """Failed sample is safely tracked with status='Failed' and excluded from aggregate sums."""
        samples = [
            {
                "sample_id": "S1",
                "audio_filename": "s1.mp3",
                "audio_path": "dummy1.mp3",
                "reference_transcript": "നമസ്കാരം സുഹൃത്തേ",
                "status": "valid"
            },
            {
                "sample_id": "S2",
                "audio_filename": "s2.mp3",
                "audio_path": "dummy2.mp3",
                "reference_transcript": "കേരളം",
                "status": "valid"
            }
        ]

        def mock_caller(audio_bytes, filename="", language="Malayalam"):
            if filename == "s1.mp3":
                return {"success": True, "transcript": "നമസ്കാരം സുഹൃത്തേ", "request_id": "REQ-1"}
            raise Exception("504 Gateway Timeout from Upstream STT")

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"dummy_audio")):
            with patch("os.path.exists", return_value=True):
                batch_res = evaluate_benchmark_batch(samples, api_caller=mock_caller)

        assert batch_res["summary"]["total_samples"] == 2
        assert batch_res["summary"]["successful_samples"] == 1
        assert batch_res["summary"]["failed_samples"] == 1
        assert batch_res["summary"]["benchmark_success_rate"] == 50.0

        failed_sample = batch_res["sample_results"][1]
        assert failed_sample["status"] == "Failed"
        assert "504 Gateway Timeout" in failed_sample["error_message"]
        assert failed_sample["wer"] is None
        assert failed_sample["cer"] is None

        # S2 should not contaminate aggregate reference words or errors
        assert batch_res["aggregate"]["total_ref_words"] == 2
        assert batch_res["aggregate"]["total_word_errors"] == 0
        assert batch_res["aggregate"]["aggregate_wer"] == 0.0

    def test_evaluate_batch_all_failures(self):
        """All samples fail safely; aggregates return None without ZeroDivisionError."""
        samples = [
            {
                "sample_id": "S1",
                "audio_filename": "s1.mp3",
                "audio_path": "dummy1.mp3",
                "reference_transcript": "ടെസ്റ്റ്",
                "status": "valid"
            }
        ]

        def mock_caller(audio_bytes, filename="", language="Malayalam"):
            raise ConnectionError("Network unreachable")

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"dummy_audio")):
            with patch("os.path.exists", return_value=True):
                batch_res = evaluate_benchmark_batch(samples, api_caller=mock_caller)

        assert batch_res["summary"]["successful_samples"] == 0
        assert batch_res["summary"]["failed_samples"] == 1
        assert batch_res["summary"]["benchmark_success_rate"] == 0.0
        assert batch_res["aggregate"]["aggregate_wer"] is None
        assert batch_res["aggregate"]["aggregate_cer"] is None
        assert batch_res["aggregate"]["total_ref_words"] == 0

    def test_evaluate_batch_skips_invalid_status_samples(self):
        """Sample with status != 'valid' is skipped without invoking API."""
        samples = [
            {
                "sample_id": "S_INV",
                "audio_filename": "missing.mp3",
                "audio_path": None,
                "reference_transcript": "",
                "status": "missing_audio",
                "error_detail": "Audio file not found"
            }
        ]

        mock_caller = MagicMock()
        batch_res = evaluate_benchmark_batch(samples, api_caller=mock_caller)

        assert mock_caller.call_count == 0
        assert batch_res["summary"]["skipped_samples"] == 1
        assert batch_res["sample_results"][0]["status"] == "Skipped"

    def test_evaluate_batch_empty_selection(self):
        """Empty input list returns empty result safely."""
        batch_res = evaluate_benchmark_batch([], api_caller=MagicMock())
        assert batch_res["summary"]["total_samples"] == 0
        assert batch_res["summary"]["successful_samples"] == 0
        assert batch_res["aggregate"]["aggregate_wer"] is None

    def test_evaluate_batch_progress_callback(self):
        """Progress callback is called for each sample and final completion."""
        samples = [
            {
                "sample_id": "S1",
                "audio_filename": "s1.mp3",
                "audio_path": "dummy1.mp3",
                "reference_transcript": "ടെസ്റ്റ്",
                "status": "valid"
            }
        ]
        calls = []

        def callback(cur, tot, sid):
            calls.append((cur, tot, sid))

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"dummy_audio")):
            with patch("os.path.exists", return_value=True):
                evaluate_benchmark_batch(
                    samples,
                    progress_callback=callback,
                    api_caller=lambda b, **kw: {"success": True, "transcript": "ടെസ്റ്റ്"}
                )

        assert len(calls) == 2
        assert calls[0] == (0, 1, "S1")
        assert calls[1] == (1, 1, "Completed")


# =====================================================================
# 13. Step 5 — Benchmark Reporting & Export Tests
# =====================================================================

class TestBenchmarkReporting:
    """Tests for TXT and CSV benchmark reports."""

    @pytest.fixture
    def mock_benchmark_data(self):
        batch_results = {
            "summary": {
                "total_samples": 2,
                "successful_samples": 2,
                "failed_samples": 0,
                "skipped_samples": 0,
                "benchmark_success_rate": 100.0,
                "language": "Malayalam",
                "timestamp": "2026-11-14T10:00:00"
            },
            "aggregate": {
                "aggregate_wer": 16.67,
                "total_ref_words": 6,
                "total_hyp_words": 6,
                "total_word_errors": 1,
                "substitutions": 1,
                "deletions": 0,
                "insertions": 0,
                "aggregate_cer": 8.33,
                "total_ref_graphemes": 24,
                "total_hyp_graphemes": 24,
                "total_char_errors": 2,
                "char_substitutions": 2,
                "char_deletions": 0,
                "char_insertions": 0,
                "aggregate_critical_match_rate": 100.0,
                "total_critical_expected": 2,
                "total_critical_matched": 2,
                "total_critical_changed": 0,
                "total_critical_missing": 0,
                "total_critical_extra": 0,
                "avg_latency_sec": 1.25
            },
            "sample_results": [
                {
                    "sample_id": "ML_NORMAL_01",
                    "audio_filename": "ML_NORMAL_01.mp3.mp3",
                    "reference": "എന്റെ പേര് സാവിയോ എന്നാണ്",
                    "hypothesis": "എന്റെ പേര് സാവിയോ എന്നാണ്",
                    "status": "Success",
                    "latency_sec": 1.2,
                    "request_id": "REQ-01",
                    "ref_words": 4,
                    "hyp_words": 4,
                    "word_errors": 0,
                    "substitutions": 0,
                    "deletions": 0,
                    "insertions": 0,
                    "wer": 0.0,
                    "ref_graphemes": 14,
                    "hyp_graphemes": 14,
                    "char_errors": 0,
                    "char_substitutions": 0,
                    "char_deletions": 0,
                    "char_insertions": 0,
                    "cer": 0.0,
                    "critical_expected": 1,
                    "critical_matched": 1,
                    "critical_changed": 0,
                    "critical_missing": 0,
                    "critical_extra": 0,
                    "critical_match_rate": 100.0,
                    "error_message": None
                },
                {
                    "sample_id": "ML_NORMAL_02",
                    "audio_filename": "ML_NORMAL_02.mp3.mp3",
                    "reference": "ഇന്ന് രാവിലെ കോളേജിൽ പോയി",
                    "hypothesis": "ഇന്ന് രാവിലെ സ്കൂളിൽ പോയി",
                    "status": "Success",
                    "latency_sec": 1.3,
                    "request_id": "REQ-02",
                    "ref_words": 2,
                    "hyp_words": 2,
                    "word_errors": 1,
                    "substitutions": 1,
                    "deletions": 0,
                    "insertions": 0,
                    "wer": 50.0,
                    "ref_graphemes": 10,
                    "hyp_graphemes": 10,
                    "char_errors": 2,
                    "char_substitutions": 2,
                    "char_deletions": 0,
                    "char_insertions": 0,
                    "cer": 20.0,
                    "critical_expected": 1,
                    "critical_matched": 1,
                    "critical_changed": 0,
                    "critical_missing": 0,
                    "critical_extra": 0,
                    "critical_match_rate": 100.0,
                    "error_message": None
                }
            ]
        }
        dataset_info = {
            "total_discovered": 2,
            "valid_count": 2,
            "invalid_count": 0,
            "has_paired_noise": False,
            "normal_condition_count": 2
        }
        return batch_results, dataset_info

    def test_generate_benchmark_summary_txt_structure(self, mock_benchmark_data):
        """TXT report includes dataset inventory, aggregates, sample rows, and limitation notice."""
        batch_results, dataset_info = mock_benchmark_data
        txt = generate_benchmark_summary_txt(batch_results, dataset_info)

        assert "MALAYALAM SPEECH RECOGNITION BENCHMARK REPORT" in txt
        assert "1. DATASET INVENTORY" in txt
        assert "Total Discovered Samples : 2" in txt
        assert "2. AGGREGATE RECOGNITION & ENTITY METRICS" in txt
        assert "Aggregate Word Error Rate (WER)        : 16.67%" in txt
        assert "Aggregate Character Error Rate (CER)   : 8.33%" in txt
        assert "3. SAMPLE-LEVEL EVALUATION BREAKDOWN" in txt
        assert "ML_NORMAL_01" in txt
        assert "ML_NORMAL_02" in txt
        assert "PAIRED NOISE STATUS: UNAVAILABLE" in txt.upper()
        assert "METHODOLOGICAL NOTE & LIMITATIONS" in txt

    def test_summary_txt_security_no_api_key_leak(self, mock_benchmark_data):
        """TXT report must never contain API keys, Bearer tokens, or passwords."""
        batch_results, dataset_info = mock_benchmark_data
        txt = generate_benchmark_summary_txt(batch_results, dataset_info)

        assert "api_key" not in txt.lower()
        assert "bearer" not in txt.lower()
        assert "secret" not in txt.lower()

    def test_generate_benchmark_sample_csv_content(self, mock_benchmark_data):
        """Sample CSV contains required headers and correct sample data."""
        import csv
        import io
        batch_results, _ = mock_benchmark_data
        csv_str = generate_benchmark_sample_csv(batch_results)

        reader = list(csv.reader(io.StringIO(csv_str)))
        headers = reader[0]

        assert "sample_id" in headers
        assert "audio_filename" in headers
        assert "wer_pct" in headers
        assert "cer_pct" in headers
        assert "critical_match_rate_pct" in headers
        assert len(reader) == 3

        row1 = reader[1]
        assert row1[headers.index("sample_id")] == "ML_NORMAL_01"
        assert row1[headers.index("wer_pct")] == "0.0"

    def test_generate_benchmark_aggregate_csv_content(self, mock_benchmark_data):
        """Aggregate CSV contains required metric rows and descriptions."""
        import csv
        import io
        batch_results, _ = mock_benchmark_data
        csv_str = generate_benchmark_aggregate_csv(batch_results)

        reader = list(csv.reader(io.StringIO(csv_str)))
        headers = reader[0]
        assert headers == ["metric", "value", "unit", "description"]

        metrics_map = {row[0]: row[1] for row in reader[1:]}
        assert metrics_map["total_samples"] == "2"
        assert metrics_map["successful_samples"] == "2"
        assert metrics_map["aggregate_wer"] == "16.67"
        assert metrics_map["aggregate_cer"] == "8.33"


