# Web Importer – Automation Test Documentation

This document describes the testing goals, architecture, environments, and key UI+API end‑to‑end test cases implemented in this project.

Repository structure (high level):
- Core framework:
  - [`corelib.web_handler.WebHandler`](corelib/web_handler.py)
  - [`corelib.api_handler.ApiClient`](corelib/api_handler.py)
  - [`corelib.email_handler`](corelib/email_handler.py)
  - [`corelib.utils`](corelib/utils.py), [`corelib.logger`](corelib/logger.py)
- Page Objects:
  - [`page.login_page.Login`](page/login_page.py)
  - [`page.home_page.Home`](page/home_page.py)
- Locators:
  - [`locators.login`](locators/login.py), [`locators.home`](locators/home.py)
- Tests:
  - UI tests: [tests/ui/](tests/ui)
  - Perf tests: [tests/performance/](tests/performance)
- Config/fixtures/tools:
  - [config.yaml](config.yaml), [conftest.py](conftest.py), [run.py](run.py)

## 1) Overview
- Objective:
  - Validate end‑to‑end user journeys on Web Importer across UI and API layers.
  - Ensure critical workflows (login, search, clone, edit, release, import/export Excel, delete) behave correctly and synchronously reflect backend state.
  - Verify email‑based Excel export/import flows and downloadable artifacts.
- Scope:
  - Web UI E2E using Playwright.
  - API assertions synchronized with UI actions (via in‑test network waits).
  - Email parsing and file download validation (Excel import/export flows).
  - Performance smoke testing for key APIs (k6).
- Test types:
  - UI functional, API integration, UI+API end‑to‑end, basic performance (k6), smoke/regression subsets.

## 2) Logic Code (Architecture & Main Flows)

Core architecture follows Page Object Model + thin core libraries to standardize UI operations, API waits, and email/file utilities.

- Page Objects
  - [`page.login_page.Login`](page/login_page.py): Encapsulates navigation to login page and login flow using WebHandler wrappers.
  - [`page.home_page.Home`](page/home_page.py): Encapsulates main actions:
    - Search, clone, edit, release, delete draft.
    - Import/Download Excel.
    - UI validations: table row parsing, details sections (“R&D Note”, “Release Note”, “Lib Log”, “Log Changes”), notification/bell messages.
    - Helpers frequently used by tests: `search_information`, `clone_version`, `edit_draft_version`, `release_draft_version`, `delete_draft_version`, `get_data_by_row`, `get_draft_version_infor`, `get_sections_pro_db_info`, `import_excel`, `download_excel`, `get_msg_infor`, `get_latest_bell_notification`. All are sourced from [`page.home_page.Home`](page/home_page.py).

- Locators
  - Centralized selectors live in [`locators.home`](locators/home.py), [`locators.login`](locators/login.py). Page Objects reference these for maintainability.

- Web/UI actions wrapper
  - [`corelib.web_handler.WebHandler`](corelib/web_handler.py): Reliable wrappers around Playwright with logging and expectations (e.g. `click_element`, `fill_element`, `expect_*`, `fill_all`, `goto_page`). Tests and POM call these to reduce flakiness and standardize waits, e.g.:
    - Assertions: `expect_checked`, `expect_enabled`, `expect_contains_text`, etc.
    - Bulk utilities: `fill_all` for filling repeated inputs robustly.

- API synchronization
  - [`corelib.api_handler.ApiClient`](corelib/api_handler.py): Orchestrates “trigger UI action → wait for specific network call → assert JSON”.
    - `run_and_wait_json(trigger=..., path_or_url=..., method=..., query=..., expected_status=...)` calls the UI action (trigger) and blocks until a matching response is captured. Returns `(resp, data, meta)` or `(resp, data)` depending on the flow.
    - Matching predicate supports base API override (e.g., import endpoints use `base_api_import`).
    - Used across tests to bind UI interactions (clone/edit/release/import/export) to the exact backend call and payload.

- Email utilities
  - [`corelib.email_handler`](corelib/email_handler.py): IMAP polling + parsing for Excel export/import email confirmations.
    - `wait_for_excel_email(...)` waits and returns parsed details (subject, sender, extracted Download link).
    - `parse_excel_email_details(...)` extracts make/function/version/enum version and download URL from HTML or text.

- Utilities
  - [`corelib.utils`](corelib/utils.py):
    - `read_config_file` to load [config.yaml](config.yaml).
    - `download_file(url, path)` to fetch artifacts.
    - `find_import_file(make_name, function_name, test_case, folder="test_data")` to locate test ZIPs for import; supports exact/loose matches by normalized stems (see snippet in the file).
  - Logging setup via [`corelib.logger`](corelib/logger.py).

- Test Orchestration
  - Fixtures in [conftest.py](conftest.py):
    - Browser/context/page lifecycle with video recording to videos/.
    - `config` fixture loads [config.yaml](config.yaml).
    - `api` fixture provides a preconfigured [`corelib.api_handler.ApiClient`](corelib/api_handler.py).
    - `--headless` option for CI/headless runs.
  - [run.py](run.py): Wrapper to execute pytest with HTML reporting per run.

How UI+API tests flow:
1) Use [`page.login_page.Login`](page/login_page.py) to navigate and authenticate.
2) Use [`page.home_page.Home`](page/home_page.py) to perform a UI action (e.g., clone/import/edit).
3) Wrap the UI action inside `ApiClient.run_and_wait_json(...)` to capture the specific backend request/response.
4) Assert the API status and payload.
5) Refresh/read UI and assert visible state, table content, timestamps, and details sections.
6) For Excel flows, poll mailbox via [`corelib.email_handler`](corelib/email_handler.py) and optionally download files via [`corelib.utils.download_file`](corelib/utils.py).

Minimal example pattern:
```python
# Orchestrate UI + API in one step
resp, data, meta = api.run_and_wait_json(
    trigger=lambda: home.clone_version(),           # 1) UI action
    base_api=config["base_api"],                    # 2) backend base
    path_or_url="/api/version/clone-data",         # 3) specific endpoint
    method="POST",
    expected_status=200,
    timeout=30000,
)
assert resp.status == 200
# Then assert UI via Home helpers...
```
## 3) Test Environment
- Programming language and frameworks
    - Python 3.12+ (recommended)
    - Pytest
    - Playwright (Python)
    - pytest‑html (HTML reports). Allure plugin is present but not actively configured.
    - k6 (TypeScript) for performance smoke tests.
- Tooling and runners
    - run.py – wraps pytest with per‑run HTML reports under reports/report_<timestamp>/.
    - Dockerfiles for UI/perf jobs: Dockerfile.ui, Dockerfile.perf.
    - GitLab CI pipeline: .gitlab-ci.yml, gitlab-ci-registry.yml.
- Configuration
    - config.yaml holds:
        - base_url, base_api, base_api_import
        - username/password (+ alternate credentials)
        - IMAP settings: imap_server, imap_port, imap_user, imap_password
        - Sensitive values should be injected via CI variables.
- Optional dependencies for perf tests
    - Node + esbuild (to bundle k6 TypeScript tests if needed).
## 4) Test Cases (UI + API E2E)
Only listing cases that validate both UI and API in tests/ui/:

1) Clone – Valid Conditions
- Name: test_clone_version_with_valid_conditions
- Objective: Cloning a version produces a Draft with correct metadata and UI reflects the change.
- Preconditions:
    - Valid credentials in config.yaml.
    - Target make/function has at least one official version.
- Steps:
    1) Login via page.login_page.Login.
    2) Search target via page.home_page.Home.search_information.
    3) API wait while triggering clone:
        - api.run_and_wait_json(trigger=lambda: home.clone_version(), path_or_url="/api/version/clone-data", method="POST")
    4) Refresh UI, assert bell notification and Draft row via page.home_page.Home.get_draft_version_infor.
    5) Validate timestamp delta vs API createdAt, status “DRAFT”, and details sections visibility.
- Expected Result:
    - API 200; payload has new Draft, correct from_version, make_version, and timestamps.
    - UI shows a new Draft row with matching time/version; actions include Edit/Release/Delete.
- Code: tests/ui/test_clone_version.py
2) Clone – Dev DB
- Name: test_clone_version_with_valid_conditions_dev_db
- Objective: Validate cloning on specific “Production Database/Dev DB” path with UI alignment.
- Preconditions: Same as above; environment supports DB type switching if applicable.
- Steps:
    - As above, but trigger clone with dev/DB type option in UI; wait API with clone-data.
    - Assert date formatting conversion (UTC → local) matches UI value.
- Expected Result:
    - API 200; new Draft metadata consistent; UI date equals formatted local time; actions available.
- Code: tests/ui/test_clone_version.py
3) Edit Draft – Update All Fields
- Name: test_edit_draft_version
- Objective: Update RD/Release/Lib notes via UI; assert API update and UI sections.
- Preconditions: Draft exists (create via clone in test).
- Steps:
    1) Login and search.
    2) Clone → reload.
    3) Trigger edit_draft_version(rd_notes=..., release_notes=..., lib_log=..., is_save=True) in UI while waiting API:
        - path_or_url="/api/version/update_release_note", method PUT.
    4) Assert API success; refresh and open sections via get_sections_pro_db_info.
- Expected Result:
    - API 200 with success message; UI sections show updated content.
- Code: tests/ui/test_edit.py
4) Edit Draft – Update Some Fields
- Name: test_edit_some_field_draft_version
- Objective: Update a subset of fields; ensure API and UI reflect only the changes.
- Preconditions: Draft exists.
- Steps: Same pattern as (3) but only some fields filled before save.
- Expected Result:
    - API 200; UI sections reflect updated fields; unchanged fields remain intact.
- Code: tests/ui/test_edit.py
5) Edit Draft – Save Empty (Clear All)
- Name: test_edit_all_fields_with_empty
- Objective: Save empty notes and confirm API/UI clear state.
- Preconditions: Draft exists and has content to clear.
- Steps:
    - Trigger edit_draft_version(is_save=True) with empty fields; wait API PUT to /api/version/update_release_note.
    - Reload and verify empty state in sections.
- Expected Result:
    - API 200 (contains “Successfully update release_note”); UI sections show expected empty values.
- Code: tests/ui/test_edit.py
6) Delete Draft
- Name: test_delete_version
- Objective: Delete a Draft through UI while asserting underlying DELETE API.
- Preconditions: Create Draft first (clone).
- Steps:
    1) Clone (assert POST /api/version/clone-data).
    2) Wait, reload; capture draft id from clone payload.
    3) Trigger delete and wait API DELETE /api/versions/{id}.
    4) Reload, ensure Draft row disappears.
- Expected Result:
    - API 200 on delete; UI no longer shows Draft.
- Code: tests/ui/test_delete.py
7) Search – Valid Conditions
- Name: test_search_with_valid_conditions
- Objective: Search via UI and confirm API returns expected data set.
- Preconditions: Valid function/make params exist.
- Steps:
    - Trigger search_information(...) while waiting GET /api/version/function_make?feature=...&make_enm=....
    - Assert UI displays Production DB table/headers.
- Expected Result:
    - API 200 with non‑null payload; UI table becomes visible with results.
- Code: tests/ui/test_search.py
8) Import Excel – Conditions Meet
- Name: test_import_excel_with_conditions_meet
- Objective: Import a valid ZIP and validate API acceptance, UI row status, and email.
- Preconditions:
    - Ensure no Draft exists (delete if needed).
    - Test ZIP available (resolved by corelib.utils.find_import_file).
    - IMAP credentials configured for mailbox polling.
- Steps:
    1) Login → search.
    2) Mark start time via email handler to bound email search.
    3) Trigger UI import_excel(..., is_confirm=True) while waiting POST /api/importdata (use base_api_import).
    4) Verify UI shows “Please wait…” info; table row 1 shows “IMPORTING” with new function version and expected timestamp delta.
    5) Wait for Excel email via corelib.email_handler.wait_for_excel_email.
    6) Reload UI, verify Draft row content and details sections (View links and non‑empty Log Changes).
- Expected Result:
    - API 200; succeeded=True, errors=None.
    - Email with subject containing “Excel” is received with download link.
    - UI shows Draft row with correct status/time and details sections available.
- Code: tests/ui/test_import_excel.py
9) Import Excel – Empty ZIP
- Name: test_import_excel_with_empty_zip_file
- Objective: Validate system behavior with empty ZIP (still accepted and processed async).
- Preconditions: Similar to (8), file exists (Empty.zip).
- Steps:
    - Same orchestration as (8).
- Expected Result:
    - API 200; succeeded=True, errors=None.
    - Email received; UI row transitions accordingly; eventually no lingering Draft after reload (as asserted in test).
- Code: tests/ui/test_import_excel.py
10) Import Excel – Add Row
- Name: test_import_excel_with_new_row_add
- Objective: Validate import that adds new rows changes function version and Draft appears with expected metadata.
- Preconditions: Similar to (8).
- Steps:
    - Import with test case “AddRow”; wait /api/importdata, then email; assert table row 1 “IMPORTING”, then reload and validate Draft row content and “Log Changes”.
- Expected Result:
    - API 200; succeeded=True.
    - Email received; UI Draft row with “DRAFT” status and details sections available; “Log Changes” not empty.
- Code: tests/ui/test_import_excel.py
11) Import Excel – Edit Row
- Name: test_import_excel_edit_row
- Objective: Validate import that edits rows; confirm version/time updates and Draft details.
- Preconditions/Steps: Similar to (10).
- Expected Result:
    - API 200; email received; UI shows updated Draft with “View” details; “Log Changes” is not empty.
- Code: tests/ui/test_import_excel.py
12) Import Excel – Delete Row
- Name: test_import_excel_delete_row
- Objective: Validate import that deletes rows; confirm Draft contents/time and change logs.
- Preconditions/Steps: Similar to (10).
- Expected Result:
    - API 200; email received; UI Draft shows “DRAFT”, details available; “Log Changes” not empty.
- Code: tests/ui/test_import_excel.py
13) Import Excel – Missing ID Column
- Name: test_import_excel_missing_id_column
- Objective: Import where a required column is missing; system still processes and emails results; timestamps verified.
- Preconditions: Similar to (8) with respective ZIP.
- Steps:
    - Same orchestration; subject filter may contain “Insert DB to Server”.
- Expected Result:
    - API 200; succeeded=True; email received; UI timestamps within expected delta; importing row fields for notes are empty as asserted.
- Code: tests/ui/test_import_excel.py
14) Import Excel – Check Enum Failed
- Name: test_import_excel_check_enum_failed
- Objective: Validate failure scenario on enum checks; ensure pipeline responds and UI/email behavior holds.
- Preconditions/Steps: Similar to (8) with “CheckEnumFailed” ZIP.
- Expected Result:
    - API 200; (payload asserts in test); email received; UI notes columns empty while processing; reload assertions follow.
- Code: tests/ui/test_import_excel.py
15) Import Excel – Check Template Failed
- Name: test_import_excel_check_template_failed
- Objective: Invalid template scenario; similar validations.
- Preconditions/Steps: Similar to (14) with “CheckTemplateFailed” ZIP.
- Expected Result:
    - API 200; email received; UI fields empty in importing row; reload assertions follow.
- Code: tests/ui/test_import_excel.py
16) Download Excel
- Name: test_download_excel
- Objective: Trigger “Download Excel”, assert API request, validate email arrival, and download the file.
- Preconditions:
    - Valid IMAP credentials.
    - Search to a valid make/function where export is available.
- Steps:
    1) Login → search.
    2) Mark email start time.
    3) API wait around download_excel() for POST /api/function/export-excel-data.
    4) Poll for email with subject containing “Excel”; parse download URL.
    5) Download file via corelib.utils.download_file.
- Expected Result:
    - API 200; email with a downloadable link received; file downloads successfully.
- Code: tests/ui/test_download.py
Notes on time validations:

- Many tests compare UI time with server time allowing delta (e.g., < 30–50s) after converting API createdAt (UTC) to local time. This is asserted via standard Python datetime operations inside the tests (see examples in tests/ui/test_clone_version.py and tests/ui/test_import_excel.py).
## 5) References to Important Code
- Page Objects:
    - page.home_page.Home
    - page.login_page.Login
- Core libs:
    - corelib.web_handler.WebHandler
    - corelib.api_handler.ApiClient
    - corelib.email_handler
    - corelib.utils, corelib.logger
- Locators:
    - locators.home, locators.login
- Fixtures/runner:
    - conftest.py, run.py, config.yaml
## 6) How to Execute Locally (Quick)
- Create venv and install deps, then install Playwright browsers:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install
# Linux CI
python -m playwright install --with-deps
```
- Run all UI tests with HTML report (timestamped):
```bash 
python run.py
```
- Run by markers (examples):
```bash
python run.py -i smoke
python run.py -i import_excel_1 download_excel_1
```
- Headless
```bash
python run.py --headless
```
## 7) CI/CD Summary
- Defined in .gitlab-ci.yml.
- Typical stages: build image (optional) → run headless UI tests (Playwright image) → publish artifacts (reports/, videos/) → optionally run k6 perf.
- Docker usage for UI:
```bash
docker build -f [Dockerfile.ui](http://_vscodecontentref_/6) -t importer-tests:ui .
docker run --rm \
  -v "$PWD/reports:/app/reports" \
  -v "$PWD/videos:/app/videos" \
  -v "$PWD/config.yaml:/app/config.yaml" \
  importer-tests:ui python [run.py](http://_vscodecontentref_/7) --headless -i smoke
```