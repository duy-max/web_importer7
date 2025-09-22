# Web Importer Automation Tests

A Python-based automation test suite for end-to-end Web UI, API-assisted validations, and performance testing of the Web Importer platform.

## 1) Overview
This project automates critical user journeys and workflows:
- Web UI regression and smoke tests (login, search, clone/edit/release/delete versions, import/download Excel).
- API-assisted synchronization to assert backend responses alongside UI.
- Email parsing and file download validation for Excel export/import flows.
- Performance smoke testing for key API endpoints.

Core technologies:
- Python 3.x, Pytest
- Playwright (Python) for UI E2E
- k6 for API performance (TypeScript test)
- pytest-html for reporting
- Docker (optional) for reproducible runs
- GitLab CI/CD

Key framework modules:
- Page Object Model: [`page.home_page.Home`](page/home_page.py), [`page.login_page.Login`](page/login_page.py)
- Locator repository: [locators/](locators/home.py) ([`locators.home`](locators/home.py), [`locators.login`](locators/login.py))
- Web/UI actions wrapper: [`corelib.web_handler.WebHandler`](corelib/web_handler.py)
- Network sync helper: [`corelib.api_handler.ApiClient`](corelib/api_handler.py)
- Email utilities: [`corelib.email_handler`](corelib/email_handler.py)
- Utilities/logging: [`corelib.utils`](corelib/utils.py), [`corelib.logger`](corelib/logger.py)

## 2) Project Structure
- [tests/](tests)
  - [tests/ui/](tests/ui): UI tests (login/search/clone/edit/release/delete/import/download).
  - [tests/performance/api/login.test.ts](tests/performance/api/login.test.ts): k6 performance smoke test.
- [page/](page): Page Objects
  - [`page.login_page.Login`](page/login_page.py): Login flows.
  - [`page.home_page.Home`](page/home_page.py): Main feature actions (search, clone, edit, release, import/export).
- [locators/](locators): Centralized selectors for pages (Ant Design UI).
- [corelib/](corelib)
  - [`corelib.web_handler.WebHandler`](corelib/web_handler.py): Reliable Playwright wrappers (click/fill/expect/waits, table helpers, etc.).
  - [`corelib.api_handler.ApiClient`](corelib/api_handler.py): Wait-and-capture API responses during UI steps (run_and_wait_json/response).
  - [`corelib.email_handler`](corelib/email_handler.py): IMAP polling, parsing “Download Excel” links.
  - [`corelib.utils`](corelib/utils.py): Config loader, file utilities (e.g. [`corelib.utils.find_import_file`](corelib/utils.py), [`corelib.utils.download_file`](corelib/utils.py)).
  - [`corelib.logger`](corelib/logger.py): Structured logging.
- [test_data/](test_data): Test ZIPs used in Import Excel scenarios. Naming aligns with [`corelib.utils.find_import_file`](corelib/utils.py).
- [config.yaml](config.yaml): Environment and credentials (base URLs, API endpoints, IMAP).
- [conftest.py](conftest.py): Pytest fixtures (browser/context/page), global logging, CLI options, video recording to [videos/](videos).
- [run.py](run.py): Thin wrapper to run pytest with HTML reports per run.
- [run_pytest_100.sh](run_pytest_100.sh): Loop-runner (100 rounds) for stability checks.
- [requirements.txt](requirements.txt): Python dependencies.
- [Dockerfile.ui](Dockerfile.ui), [Dockerfile.perf](Dockerfile.perf): Docker builds for UI/perf jobs.
- [.gitlab-ci.yml](.gitlab-ci.yml), [gitlab-ci-registry.yml](gitlab-ci-registry.yml): CI/CD pipeline definitions.
- [report.html](report.html): Example pytest report artifact (for local preview).

## 3) Installation / Setup
Prerequisites:
- Python 3.12+ recommended
- pip
- k6 (for performance test) https://k6.io/docs/get-started/installation/
- Docker (optional, for containerized runs)

Install dependencies:
```bash
# optional but recommended
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt

# Install Playwright browsers (once per machine/agent)
python -m playwright install
# Linux container/CI: include system deps if needed
python -m playwright install --with-deps
```

Configuration:
- Update [config.yaml](config.yaml) to match your environment. Example:
```yaml
base_url: "https://webimporter.innovavietnam.com"
base_api: "https://importers.cartek.com.vn"
base_api_import: "https://importers.cartek.com.vn"

username: "your_user@example.com"
password: "your_password"

username_1: "alt_user@example.com"
password_1: "alt_password"

imap_server: "imap.gmail.com"
imap_port: 993
imap_user: "email_user@example.com"
imap_password: "app_or_imap_password"
```
Notes:
- IMAP credentials are required for tests that validate “Download Excel” emails.
- Secrets should be injected via CI variables; avoid committing them.

## 4) How to Run Tests
Using the project runner:
```bash
# run all UI tests (default reports to reports/report_YYYY-mm-dd_HH-MM-SS/report.html)
python run.py

# run by marker(s)
python run.py -i smoke
python run.py -i import_excel_1 download_excel_1

# exclude markers
python run.py -e slow

# run a specific test file
python run.py tests/ui/test_login.py

# run headless
python run.py --headless
```

Run directly with pytest:
```bash
pytest -m "smoke" --html reports/report.html --self-contained-html
pytest tests/ui/test_import_excel.py::test_import_excel_with_conditions_meet --html reports/report.html --self-contained-html
```

k6 performance test:
```bash
# Option A: bundle TS to JS, then run
npx esbuild tests/performance/api/login.test.ts --bundle --platform=browser --outfile=dist/login.test.js
k6 run dist/login.test.js

# Option B: if your environment supports TS directly for k6 (via tooling)
k6 run tests/performance/api/login.test.ts
```

Docker (UI tests):
```bash
# build
docker build -f Dockerfile.ui -t importer-tests:ui .

# run (mount reports/videos, optionally mount a custom config.yaml)
docker run --rm \
  -v "$PWD/reports:/app/reports" \
  -v "$PWD/videos:/app/videos" \
  -v "$PWD/config.yaml:/app/config.yaml" \
  importer-tests:ui python run.py --headless -i smoke
```

## 5) Reports
- HTML report: generated per run by [run.py](run.py) into reports/report_<timestamp>/report.html
- Example artifact for quick preview: [report.html](report.html)
- Videos: recorded by fixtures in [conftest.py](conftest.py) to [videos/](videos). Filenames include pass/fail and test name.
- Email/download artifacts: downloaded files go to downloads/ via [`corelib.utils.download_file`](corelib/utils.py).

## 6) CI/CD Pipeline
- Defined in [.gitlab-ci.yml](.gitlab-ci.yml) (and [gitlab-ci-registry.yml](gitlab-ci-registry.yml)).
- Typical stages:
  1) Build (optional Docker image using [Dockerfile.ui](Dockerfile.ui))
  2) Run UI tests headless (Playwright browsers installed on runner or image)
  3) Publish artifacts (reports/, videos/)
  4) Optionally run perf tests (k6) via [Dockerfile.perf](Dockerfile.perf)

Example job snippet:
```yaml
ui_tests:
  image: mcr.microsoft.com/playwright/python:v1.47.0-focal
  stage: test
  script:
    - pip install -r requirements.txt
    - python -m playwright install --with-deps
    - python run.py --headless -i smoke
  artifacts:
    when: always
    paths:
      - reports/
      - videos/
    expire_in: 7 days
```

## 7) Conventions / Best Practices
- Test naming: files and functions must start with test_*. Use descriptive, behavior-driven names.
- Use Page Object Model:
  - All selectors belong in [locators/](locators/home.py).
  - All UI actions belong in Page Objects ([`page.home_page.Home`](page/home_page.py), [`page.login_page.Login`](page/login_page.py)).
- Prefer framework wrappers over raw Playwright:
  - Assertions/waits: [`corelib.web_handler.WebHandler.expect_*`](corelib/web_handler.py)
  - Table parsing/helpers from WebHandler instead of manual DOM parsing.
- Synchronize UI with API where meaningful:
  - Use [`corelib.api_handler.ApiClient.run_and_wait_json`](corelib/api_handler.py) to trigger UI and assert response payloads/status.
- Test data:
  - ZIP naming used by [`corelib.utils.find_import_file`](corelib/utils.py) → Make_Function[_TestCase].zip (case/spacing-insensitive).
- Keep sleeps minimal; rely on WebHandler’s waits (expect_visible/hidden/enabled/contains).

Minimal example:
```python
from page.login_page import Login
from page.home_page import Home
from corelib.api_handler import ApiClient

def test_clone_smoke(page, config):
    login = Login(page)
    home = Home(page)
    api = ApiClient(page, base_api=config["base_api"])

    login.navigate_to_login_page(base_url=config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    home.search_information(make_name="Volkswagen", function_name="VinDecode")

    resp, data, version_meta = api.run_and_wait_json(
        trigger=lambda: home.clone_version(),
        path_or_url="/api/version/clone-data",
        method="POST",
        expected_status=200,
        timeout=30000,
    )
    assert resp.status == 200
    assert data["newVersion"]["status"] == "Draft"
```

## 8) Troubleshooting & Contact
Common issues:
- Playwright browsers missing → run:
```bash
python -m playwright install --with-deps
```
- Headless issues in CI → ensure sandbox/deps are installed or use the official Playwright image.
- IMAP login fails → use app passwords; verify imap_server/port/SSL; allow less secure app access if required by provider.
- File not found during Import Excel → verify ZIP exists in [test_data/](test_data) and matches naming for [`corelib.utils.find_import_file`](corelib/utils.py).
- Long paths/permissions on Windows/OneDrive → run from a shorter local path if needed.

Maintainers:
- QA Automation Team (update with actual owner)
- Open issues via your GitLab project and attach [reports/](reports) and [videos/](videos) artifacts for failures.