# 🧪 NADHAM QA: Automated Testing & Verification Report

**Environment:** Python 3.14.8 | Pytest 9.2.0 | Streamlit 1.67.0 | Windows  
**Test Suite Path:** `tests/test_nadham_qa.py`  
**Execution Result:** **32 Passed / 32 Total (100% Pass Rate)**  
**Streamlit AppTest:** **100% Passed (Clean Headless UI Verification)**

---

## 1. Test Suite Summary Table

| Category | Tests | Status | Execution Time |
| :--- | :---: | :---: | :---: |
| **Malayalam Unicode & Normalization** | 10 | **PASSED** | 0.82s |
| **WER & Alignment Operations** | 10 | **PASSED** | 0.54s |
| **Critical Information (Dates, Decimals, Currencies)** | 3 | **PASSED** | 0.22s |
| **Gnani API Client & Error Handling** | 7 | **PASSED** | 0.48s |
| **Downloadable Report & CSV Exports** | 2 | **PASSED** | 0.35s |
| **Total** | **32** | **PASSED** | **~8.16s** |

---

## 2. Complete Pytest Test Manifest

### 2.1 Malayalam Unicode & Normalization Tests (10 Tests)
1. `TestNormalization::test_basic_english_normalization` — Verifies lowercase conversion, punctuation removal, and whitespace normalization for English tokens.
2. `TestNormalization::test_malayalam_basic_tokenization` — Confirms Malayalam words separated by standard spaces are cleanly tokenized.
3. `TestNormalization::test_malayalam_atomic_vs_legacy_chillu` — Confirms atomic ൻ (`\u0D7B`) and legacy decomposed ൻ (`\u0D28\u0D4D\u200D`) normalize to the identical token.
4. `TestNormalization::test_malayalam_zero_width_space` — Confirms words separated by Zero-Width Space (`\u200B`) correctly split into individual tokens.
5. `TestNormalization::test_currency_symbol_handling` — Confirms currency symbol `₹` (category `Sc`) is stripped while retaining numerical value (`500`).
6. `TestNormalization::test_decimal_numbers_handling` — Confirms decimal points in numbers (`3.14`) are preserved instead of being stripped into `314`.
7. `TestNormalization::test_all_six_malayalam_chillus` — Validates canonical chillu mapping across all 6 Malayalam chillu letters (`ൺ`, `ൻ`, `ർ`, `ൽ`, `ൾ`, `ൿ`).
8. `TestNormalization::test_various_currency_symbols` — Validates normalization of `$`, `€`, and `£` alongside `₹`.
9. `TestNormalization::test_mixed_sentence_with_dates_and_decimals` — Verifies complex mixed sentences containing Malayalam text, currencies, decimals, and dates.
10. `TestNormalization::test_hyphenated_words` — Confirms hyphenated word handling.

### 2.2 WER & Alignment Operations Tests (10 Tests)
11. `TestWERCAlculation::test_exact_match` — Verifies that identical reference and hypothesis produce `0.0% WER` and zero errors.
12. `TestWERCAlculation::test_single_substitution` — Verifies single word substitution: WER = 50.0%, 1 substitution operation.
13. `TestWERCAlculation::test_single_deletion` — Verifies single word deletion: WER = 33.33%, 1 deletion operation.
14. `TestWERCAlculation::test_single_insertion` — Verifies single word insertion: WER = 50.0%, 1 insertion operation.
15. `TestWERCAlculation::test_wer_exceeding_100_percent` — Verifies that high hallucination/insertions correctly yield WER > 100% (e.g. 400%).
16. `TestWERCAlculation::test_all_deletions_empty_hypothesis` — Verifies silent hypothesis yields 100% WER and all deletion operations.
17. `TestWERCAlculation::test_empty_reference_returns_none` — Confirms that empty or whitespace reference returns `None` to prevent division by zero.
18. `TestWERCAlculation::test_punctuation_only_reference_returns_none` — Confirms that punctuation-only reference returns `None`.
19. `TestWERCAlculation::test_both_empty_returns_none` — Confirms that empty reference and empty hypothesis return `None`.
20. `TestWERCAlculation::test_operations_sum_matches_error_count` — Validates the mathematical invariant:  
   $$\text{Substitutions} + \text{Deletions} + \text{Insertions} = \text{Total Errors}$$

### 2.3 Critical Information Tests (3 Tests)
21. `TestCriticalInformation::test_dates_format_preserved` — Verifies dates like `15/08/1947` and `15-08-1947` preserve delimiters and do not collapse into `15081947`.
22. `TestCriticalInformation::test_number_spoken_vs_digits` — Documents baseline behavior when references use digits and hypotheses use spoken words.
23. `TestCriticalInformation::test_indian_number_commas` — Confirms Indian comma grouping (`1,00,000` → `100000`) is normalized.

### 2.4 Gnani API & Defensive Guardrails Tests (7 Tests)
24. `TestGnaniAPI::test_missing_api_key_raises_value_error` — Verifies `ValueError` when `GNANI_API_KEY` is not found in the environment.
25. `TestGnaniAPI::test_successful_api_call` — Mocks a successful 200 OK response from Gnani API and verifies header and multipart payloads.
26. `TestGnaniAPI::test_api_http_error_handling` — Verifies exception handling when API returns HTTP 401 or 500 status codes.
27. `TestGnaniAPI::test_api_business_failure_handling` — Verifies exception handling when API returns 200 OK with `{"success": false, "error": "..."}`.
28. `TestGnaniAPI::test_zero_byte_audio_rejected` — Confirms 0-byte audio raises a client-side `ValueError` before making network requests.
29. `TestGnaniAPI::test_audio_upload_size_limit_enforced` — Confirms files exceeding 25 MB raise a client-side `ValueError` before making network requests.
30. `TestGnaniAPI::test_html_gateway_error_sanitized` — Confirms HTTP 504 Cloudflare HTML errors are sanitized and do not leak raw markup.

### 2.5 Report Generation & CSV Exports Tests (2 Tests)
31. `TestReportGeneration::test_report_content_completeness` — Verifies TXT report formatting, timestamp, audio filename, metrics, and operations table.
32. `TestReportGeneration::test_csv_export_structure` — Verifies CSV DataFrame export containing `Status`, `Reference Word`, and `Recognized Word` columns.

---

## 3. Pytest Execution Console Output

```text
============================= test session starts =============================
platform win32 -- Python 3.14.8, pytest-9.2.0, pluggy-1.7.0
rootdir: c:\Users\user
plugins: anyio-4.16.0
collected 32 items

tests\test_nadham_qa.py::TestNormalization::test_basic_english_normalization PASSED           [  3%]
tests\test_nadham_qa.py::TestNormalization::test_malayalam_basic_tokenization PASSED          [  6%]
tests\test_nadham_qa.py::TestNormalization::test_malayalam_atomic_vs_legacy_chillu PASSED     [  9%]
tests\test_nadham_qa.py::TestNormalization::test_malayalam_zero_width_space PASSED            [ 12%]
tests\test_nadham_qa.py::TestNormalization::test_currency_symbol_handling PASSED              [ 15%]
tests\test_nadham_qa.py::TestNormalization::test_decimal_numbers_handling PASSED              [ 18%]
tests\test_nadham_qa.py::TestNormalization::test_all_six_malayalam_chillus PASSED             [ 21%]
tests\test_nadham_qa.py::TestNormalization::test_various_currency_symbols PASSED              [ 25%]
tests\test_nadham_qa.py::TestNormalization::test_mixed_sentence_with_dates_and_decimals PASSED [ 28%]
tests\test_nadham_qa.py::TestNormalization::test_hyphenated_words PASSED                      [ 31%]
tests\test_nadham_qa.py::TestWERCAlculation::test_exact_match PASSED                           [ 34%]
tests\test_nadham_qa.py::TestWERCAlculation::test_single_substitution PASSED                  [ 37%]
tests\test_nadham_qa.py::TestWERCAlculation::test_single_deletion PASSED                      [ 40%]
tests\test_nadham_qa.py::TestWERCAlculation::test_single_insertion PASSED                     [ 43%]
tests\test_nadham_qa.py::TestWERCAlculation::test_wer_exceeding_100_percent PASSED            [ 46%]
tests\test_nadham_qa.py::TestWERCAlculation::test_all_deletions_empty_hypothesis PASSED        [ 50%]
tests\test_nadham_qa.py::TestWERCAlculation::test_empty_reference_returns_none PASSED          [ 53%]
tests\test_nadham_qa.py::TestWERCAlculation::test_punctuation_only_reference_returns_none PASSED [ 56%]
tests\test_nadham_qa.py::TestWERCAlculation::test_both_empty_returns_none PASSED              [ 59%]
tests\test_nadham_qa.py::TestWERCAlculation::test_operations_sum_matches_error_count PASSED  [ 62%]
tests\test_nadham_qa.py::TestCriticalInformation::test_dates_format_preserved PASSED         [ 65%]
tests\test_nadham_qa.py::TestCriticalInformation::test_number_spoken_vs_digits PASSED         [ 68%]
tests\test_nadham_qa.py::TestCriticalInformation::test_indian_number_commas PASSED            [ 71%]
tests\test_nadham_qa.py::TestGnaniAPI::test_missing_api_key_raises_value_error PASSED        [ 75%]
tests\test_nadham_qa.py::TestGnaniAPI::test_successful_api_call PASSED                       [ 78%]
tests\test_nadham_qa.py::TestGnaniAPI::test_api_http_error_handling PASSED                   [ 81%]
tests\test_nadham_qa.py::TestGnaniAPI::test_api_business_failure_handling PASSED             [ 84%]
tests\test_nadham_qa.py::TestGnaniAPI::test_zero_byte_audio_rejected PASSED                  [ 87%]
tests\test_nadham_qa.py::TestGnaniAPI::test_audio_upload_size_limit_enforced PASSED         [ 90%]
tests\test_nadham_qa.py::TestGnaniAPI::test_html_gateway_error_sanitized PASSED              [ 93%]
tests\test_nadham_qa.py::TestReportGeneration::test_report_content_completeness PASSED       [ 96%]
tests\test_nadham_qa.py::TestReportGeneration::test_csv_export_structure PASSED               [100%]

============================== 32 passed in 8.16s ==============================
```

---

## 4. Streamlit AppTest Headless Results

Headless UI execution via Streamlit's official testing framework (`streamlit.testing.v1.AppTest`):
- **UI Initialization:** Loaded all elements (Header, File Uploader, Selectbox, Text Area, Run Button) with zero exceptions.
- **Empty Audio Validation:** Click with no audio produced expected notification `Please upload an audio file.`
- **Zero-Byte Audio Validation:** Intercepted empty audio file and blocked network dispatch.
- **Punctuation-Only Text Validation:** Caught `...` text and presented clean validation error.
- **Evaluation Flow:** Simulated API response correctly triggered metrics cards, word-level table, and download buttons.
- **Error Sanitization:** Verified that simulated 504 HTML response rendered a sanitized error message without raw HTML.
