from page.home_page import Home
from page.login_page import Login
import pytest
from corelib import logger
import time
from datetime import datetime

logger = logger.Logger(prefix="test_search", log_level="INFO")

@pytest.mark.release
def test_release_draft_version(page, config, api):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Honda"
    release.search_information(make_name=make_name, function_name = feature)
    release.clone_version()
    release.reload_page()
    time.sleep(3)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"release rd note at {generate_time}"
    release_notes_expected = f"release release note at {generate_time}"
    lib_log_expected = f"release lib log at {generate_time}"
    release.release_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected, is_confirm=True)
    # resp, data, _ = api.run_and_wait_json(
    #         trigger=lambda: release.release_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected, is_confirm=True),
    #         path_or_url="",
    #         method="",
    #         expected_status=200,
    #         timeout=30000,
    #     )

    # assert api
    # logger.info(f"json reponse: {data}")
    # assert resp.status == 200
    # assert data["data"]["release_note"] == release_notes_expected
    # assert data["data"]["rad_note"] == rd_notes_expected
    # assert data["data"]["lib_log"] == lib_log_expected
    # assert "Successfully update release_note" in data["message"]

    # delete.reload_page()
    time.sleep(2)

    # assert ui
    # rd_notes_section = release.get_sections_pro_db_info(section="rd_note")
    # assert rd_notes_section["R&D Note"] == rd_notes_expected

    # release_notes_section = release.get_sections_pro_db_info(section="release_note")
    # assert release_notes_section["Release Note"] == release_notes_expected
    
    # lib_log_section = release.get_sections_pro_db_info(section="lib_log")
    # assert lib_log_section["Lib Log"] == lib_log_expected


@pytest.mark.skip(reason="Feature not ready yet")
def test_release_draft_version_dev_db(page, config, api):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Ymme"
    make_name = "Volkswagen"
    release.search_information(make_name=make_name, function_name = feature)
    db_type = "Production Database"
    release.clone_version(is_dev_db=True, db_type= db_type)
    release.reload_page()
    time.sleep(3)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"release rd note at {generate_time}"
    release_notes_expected = f"release release note at {generate_time}"
    lib_log_expected = f"release lib log at {generate_time}"
    release.release_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected, is_dev_db=True, is_confirm=True)

@pytest.mark.release
def test_release_cancel(page, config):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Honda"
    release.search_information(make_name=make_name, function_name = feature)
    release.clone_version()
    release.reload_page()
    time.sleep(3)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"release rd note at {generate_time}"
    release_notes_expected = f"release release note at {generate_time}"
    lib_log_expected = f"release lib log at {generate_time}"
    release.release_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected, is_cancel=True)
    # assert

@pytest.mark.release
def test_release_close_icon(page, config):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Honda"
    release.search_information(make_name=make_name, function_name = feature)
    release.clone_version()
    release.reload_page()
    time.sleep(3)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"release rd note at {generate_time}"
    release_notes_expected = f"release release note at {generate_time}"
    lib_log_expected = f"release lib log at {generate_time}"
    release.release_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected, is_close=True)
    # assert

@pytest.mark.release
def test_release_with_empty_rd_note(page, config):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Honda"
    release.search_information(make_name=make_name, function_name = feature)
    release.clone_version()
    release.reload_page()
    time.sleep(3)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # rd_notes_expected = f"release rd note at {generate_time}"
    release_notes_expected = f"release release note at {generate_time}"
    lib_log_expected = f"release lib log at {generate_time}"
    release.release_draft_version(release_notes=release_notes_expected, lib_log=lib_log_expected, is_confirm=True)
   # assert

@pytest.mark.release
def test_release_with_empty_release_note(page, config):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Honda"
    release.search_information(make_name=make_name, function_name = feature)
    release.clone_version()
    release.reload_page()
    time.sleep(3)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"release rd note at {generate_time}"
    # release_notes_expected = f"release release note at {generate_time}"
    lib_log_expected = f"release lib log at {generate_time}"
    release.release_draft_version(rd_notes=rd_notes_expected, lib_log=lib_log_expected, is_confirm=True)
    # assert
@pytest.mark.release
def test_release_with_empty_lib_log(page, config):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Honda"
    release.search_information(make_name=make_name, function_name = feature)
    release.clone_version()
    release.reload_page()
    time.sleep(3)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"release rd note at {generate_time}"
    release_notes_expected = f"release release note at {generate_time}"
    # lib_log_expected = f"release lib log at {generate_time}"
    release.release_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, is_confirm=True)
    # assert

@pytest.mark.release
def test_release_with_empty_all_fields(page, config):
    login = Login(page)
    release = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Honda"
    release.search_information(make_name=make_name, function_name = feature)
    release.clone_version()
    release.reload_page()
    time.sleep(3)
    release.release_draft_version(is_confirm=True)
    # assert