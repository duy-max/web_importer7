from page.home_page import Home
from page.login_page import Login
import pytest
from corelib import logger as _logger, utils
import time
from datetime import datetime, timedelta
from corelib import email_handler

logger = _logger.Logger(prefix="test_search", log_level="INFO")

@pytest.mark.download_excel_1
def test_download_excel(page, config, api):
    login = Login(page)
    download_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "Common"
    make_name = "Volkswagen" 
    download_ex.search_information(make_name=make_name, function_name = function_name)
    # edit.fill_notes_box(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected)
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=2)
    resp, data_api, data_first_row = api.run_and_wait_json(
            trigger=lambda: download_ex.download_excel(),
            base_api=config["base_api"],
            path_or_url="/api/function/export-excel-data",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    
    logger.info(f"json reponse: {data_api}")

    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="innovaserver@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="Excel",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    assert resp.status == 200
    assert data_api["message"] == "Waiting for export Database"

    
    logger.info(f"email full: {excel_email}")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_path = utils.download_file(excel_email["download_url"], f"downloaded_excel_{timestamp}.zip")
    assert file_path.exists()
    assert file_path.stat().st_size > 0, f"File is empty: {file_path}"


    assert data_first_row["Function Version"] == excel_email["version"]
    assert make_name == excel_email["make"]
    assert function_name == excel_email["function_name"]



