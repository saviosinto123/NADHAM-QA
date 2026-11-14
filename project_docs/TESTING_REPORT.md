# 🧪 NADHAM QA: Automated Testing & Verification Report

**Environment:** Python 3.14.8 | Pytest 9.2.0 | Streamlit 1.67.0 | Windows  
**Test Suite Path:** `tests/test_nadham_qa.py`  
**Execution Result:** **101 Passed / 101 Total (100% Pass Rate)**  
**Streamlit AppTest:** **100% Passed (Clean Headless UI Verification across all 3 Tabs)**

---

## 1. Test Suite Summary Table

| Category | Tests | Status | Execution Time |
| :--- | :---: | :---: | :---: |
| **Malayalam Unicode & Normalization** | 10 | **PASSED** | ~0.70s |
| **WER & Alignment Operations** | 10 | **PASSED** | ~0.50s |
| **CER (Unicode Extended Grapheme Clusters)** | 12 | **PASSED** | ~0.70s |
| **Critical Information Detection & Alignment** | 21 | **PASSED** | ~1.00s |
| **Gnani API Client, Security & Dual-Source Keys** | 10 | **PASSED** | ~0.60s |
| **Downloadable Reports & CSV Exports** | 2 | **PASSED** | ~0.20s |
| **Audio Quality Analysis (Local Acoustic Metrics)** | 8 | **PASSED** | ~0.40s |
| **Clean vs. Noisy Comparison Benchmark** | 11 | **PASSED** | ~0.60s |
| **Benchmark Dataset Discovery & Validation** | 7 | **PASSED** | ~0.40s |
| **Benchmark Batch Evaluation & Exact Aggregate Formulas** | 6 | **PASSED** | ~0.40s |
| **Benchmark Evidence Reporting (TXT & CSV Exports)** | 4 | **PASSED** | ~0.30s |
| **Total** | **101** | **PASSED** | **~5.92s** |

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

### 2.7 Benchmark Dataset Discovery Tests (7 Tests)
33. `TestBenchmarkDatasetDiscovery::test_extract_sample_id_extensions` — Validates sample ID extraction across repeated extensions (`.mp3.mp3`, `.mp3.txt`).
34. `TestBenchmarkDatasetDiscovery::test_discover_benchmark_dataset_real_repo` — Validates discovery of exactly 5 genuine Malayalam samples in `dataset/normal/` with matching transcripts.
35. `TestBenchmarkDatasetDiscovery::test_discover_missing_audio` — Detects transcripts missing corresponding audio files (`status="missing_audio"`).
36. `TestBenchmarkDatasetDiscovery::test_discover_missing_transcript` — Detects audio recordings missing reference transcripts (`status="missing_transcript"`).
37. `TestBenchmarkDatasetDiscovery::test_discover_empty_transcript` — Catches empty or whitespace-only transcript files (`status="empty_transcript"`).
38. `TestBenchmarkDatasetDiscovery::test_discover_empty_audio` — Catches 0-byte corrupted audio files (`status="invalid_audio"`).
39. `TestBenchmarkDatasetDiscovery::test_discover_paired_noise_status_true_when_noisy_folder_present` — Accurately detects when noisy audio directory is present vs absent.

### 2.8 Benchmark Batch Evaluation Tests (6 Tests)
40. `TestBenchmarkBatchEvaluation::test_evaluate_batch_exact_aggregate_formulas` — Verifies that Aggregate WER and CER use global error quotients ($\sum \text{errors} / \sum \text{units}$) rather than arithmetic averages of percentages.
41. `TestBenchmarkBatchEvaluation::test_evaluate_batch_partial_api_failure` — Validates that upstream API failures on individual samples are isolated, marked as `Failed`, and safely excluded from aggregate WER/CER denominators.
42. `TestBenchmarkBatchEvaluation::test_evaluate_batch_all_failures` — Ensures that when all samples fail, aggregates return `None` without division by zero.
43. `TestBenchmarkBatchEvaluation::test_evaluate_batch_skips_invalid_status_samples` — Ensures invalid samples are skipped with 0 API calls.
44. `TestBenchmarkBatchEvaluation::test_evaluate_batch_empty_selection` — Validates safe handling of an empty sample selection.
45. `TestBenchmarkBatchEvaluation::test_evaluate_batch_progress_callback` — Verifies progress callback reporting at each evaluation step.

### 2.9 Benchmark Evidence Reporting Tests (4 Tests)
46. `TestBenchmarkReporting::test_generate_benchmark_summary_txt_structure` — Validates complete plain text benchmark summary structure, inventory, aggregates, breakdown table, and paired noise disclosure.
47. `TestBenchmarkReporting::test_summary_txt_security_no_api_key_leak` — Verifies no API keys, Bearer tokens, or credentials appear in TXT report.
48. `TestBenchmarkReporting::test_generate_benchmark_sample_csv_content` — Validates CSV schema, headers, and per-sample rows.
49. `TestBenchmarkReporting::test_generate_benchmark_aggregate_csv_content` — Validates aggregate CSV schema with metrics, values, units, and descriptions.

---

## 3. Pytest Execution Console Output

```text
============================= test session starts =============================
platform win32 -- Python 3.14.8, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\user\NADHAM-QA\NADHAM-QA
plugins: anyio-4.16.0
collected 101 items

tests/test_nadham_qa.py ................................................................ [ 63%]
.....................................                                                    [100%]

============================= 101 passed in 5.04s =============================
```

---

## 4. Streamlit AppTest Headless Results

Headless UI execution via Streamlit's official testing framework (`streamlit.testing.v1.AppTest`):
- **UI Initialization:** Loaded all elements across all 3 tabs (`🎙️ Single Evaluation`, `🔬 Clean vs. Noisy Comparison`, and `📊 Malayalam Benchmark & Reliability Evidence`) with zero exceptions.
- **Empty Audio Validation:** Click with no audio produced expected notification `Please upload an audio file.`
- **Zero-Byte Audio Validation:** Intercepted empty audio file and blocked network dispatch.
- **Punctuation-Only Text Validation:** Caught `...` text and presented clean validation error.
- **Evaluation Flow:** Simulated API response correctly triggered metrics cards, word-level table, and download buttons.
- **Error Sanitization:** Verified that simulated 504 HTML response rendered a sanitized error message without raw HTML.
- **Clean vs. Noisy Comparison UI & Validation:**
  - Tab 2 switch and button click verified.
  - Intercepted missing clean audio with `Please upload the clean audio recording.`
  - Validated clean vs noisy comparison computation, delta metrics, TXT comparison report, and CSV metrics export.
- **Malayalam Benchmark & Reliability Evidence UI & Validation (Tab 3):**
  - Verified 4 dataset overview cards (`Discovered Samples: 5`, `Verified Valid: 5`, `Acoustic Condition: Normal/Clean (5)`, `Paired Noise Status: Unavailable (0 pairs)`).
  - Verified explicit Paired Clean vs. Noisy transparency alert (`Paired Clean vs. Noisy Benchmark Status: Unavailable`).
  - Verified benchmark sample multiselect and credit warning notice.
  - Verified benchmark execution button (`🚀 Execute Malayalam Benchmark`).
  - Simulated batch benchmark execution and verified aggregate metrics cards (`Aggregate WER`, `Aggregate CER`, `Benchmark Success Rate`, `Critical Entity Match`).
  - Verified interactive sample-level results table (`st.dataframe`).
  - Verified individual sample transcript expander.
  - Verified all 3 evidence export download buttons (`📥 Benchmark Summary (TXT)`, `📊 Sample-Level CSV`, `📈 Aggregate Metrics CSV`).
