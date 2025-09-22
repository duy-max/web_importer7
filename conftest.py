# Pytest fixtures and test setup for Playwright (browser, context, page configuration)

import pytest
from playwright.sync_api import sync_playwright
from corelib.utils import read_config_file
from corelib.logger import setup_global_logging
from pathlib import Path
from corelib.api_handler import ApiClient
from datetime import datetime
import os
from corelib import logger as _logger

logger = _logger.Logger(prefix="Fixture")
# Thiết lập logging toàn cục -> ghi về 1 file duy nhất
@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    proj_root = Path(__file__).resolve().parent
    print(f"project root is: {proj_root}")
    log_file = proj_root / "logs" / "tests.log"
    setup_global_logging(log_file=log_file, level="INFO")


@pytest.fixture(scope="session")
def config():
    cf_file_path = Path(__file__).resolve().parent / "config.yaml"
    print(f"config file path  is: {cf_file_path}")
    return read_config_file(cf_file_path)
    
# Fixture 1: Khởi tạo browser
# mở 1 browser cho cả session test → tiết kiệm tài nguyên.
# @pytest.fixture(scope="session")
# def browser():
#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless = False
           
#         )  
#         yield browser
#         browser.close()
@pytest.fixture(scope="session")
def browser(request):
    headless = request.config.getoption("--headless")
    logger.info(f"gia tri headless: {headless}")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless
        )
        yield browser
        browser.close()

# Fixture 2: Khởi tạo context (mỗi test case dùng 1 context mới) 
# mỗi test có context mới → tách biệt cookies/storage.
# @pytest.fixture(scope="function")
# def context(browser):
#     context = browser.new_context(
#         # viewport=config.get("viewport", {"width": 1280, "height": 720})
#         viewport = None
#     )
#     yield context
#     context.close()

# Fixture 3: Khởi tạo page (mỗi test case dùng 1 tab/page)
# mỗi test có tab riêng → tránh xung đột.
# @pytest.fixture(scope="function")
# def page(context):
#     page = context.new_page()
#     page.set_viewport_size({"width": 1920, "height": 1080})
#     yield page
#     page.close()


@pytest.fixture
def api(page, config):
    base_api = config.get("base_api", "https://importers.cartek.com.vn")
    return ApiClient(page, base_api=base_api, log_level="INFO")

@pytest.fixture
def api_import(page, config):
    return ApiClient(page, base_api=config.get("base_api_import"))



# Pytest hook: lưu kết quả từng phase (setup/call/teardown) vào request.node
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# Fixture 2: Khởi tạo context (mỗi test case dùng 1 context mới)
@pytest.fixture(scope="function")
def context(browser):
    proj_root = Path(__file__).resolve().parent
    raw_dir = proj_root / "videos" / ".raw"   # nơi Playwright ghi video gốc
    raw_dir.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(
        viewport=None,  # cho phép maximize
        record_video_dir=str(raw_dir),
        record_video_size={"width": 1920, "height": 1080},
    )
    yield context
    context.close()


# Fixture 3: Khởi tạo page (mỗi test case dùng 1 tab/page)
@pytest.fixture(scope="function")
def page(context, request):
    page = context.new_page()
    page.set_viewport_size({"width": 1920, "height": 1080})

    yield page

    # Xác định trạng thái test: pass/fail
    status = "fail"
    rep = getattr(request.node, "rep_call", None)
    logger.info(f"value of rep.passed:{rep.passed}")
    if rep and rep.passed:
        status = "pass"

    test_name = request.node.name or "unknown_test"
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")

    # Đóng page trước khi save_as
    try:
        page.close()
    except Exception:
        pass

    try:
        video = page.video  # có nếu context bật record_video_dir
    except Exception:
        video = None

    if video:
        videos_dir = Path(request.config.rootpath) / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        dst = videos_dir / f"{status}_{test_name}_{ts}.webm"
        try:
            video.save_as(str(dst))   # xuất file với tên mong muốn
            try:
                video.delete()        # xóa file .raw gốc
            except Exception:
                pass
            logger.info(f"Saved video: {dst}")
        except Exception as e:
            logger.info(f"Could not save video: {e}")

def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )