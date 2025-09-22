from page.home_page import Home
from page.login_page import Login
import pytest
from corelib import logger
import time
from datetime import datetime

logger = logger.Logger(prefix="test_search", log_level="INFO")

@pytest.mark.edit
def test_edit_draft_version(page, config, api):
    login = Login(page)
    edit = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Volkswagen"
    edit.search_information(make_name=make_name, function_name = feature)
    edit.clone_version()
    edit.reload_page()
    time.sleep(4)
    # edit.action_function(function_name="edit")
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"update rd note at {generate_time}"
    release_notes_expected = f"update release note at {generate_time}"
    lib_log_expected = f"update lib log at {generate_time}"
    # edit.fill_notes_box(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected)
    resp, data, _ = api.run_and_wait_json(
            trigger=lambda: edit.edit_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected, is_save=True),
            base_api=config["base_api"],
            path_or_url="/api/version/update_release_note",
            method="PUT",
            expected_status=200,
            timeout=30000,
        )

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["data"]["release_note"] == release_notes_expected
    assert data["data"]["rad_note"] == rd_notes_expected
    assert data["data"]["lib_log"] == lib_log_expected
    assert "Successfully update release_note" in data["message"]

    # delete.reload_page()
    time.sleep(2)

    # assert ui
    rd_notes_section = edit.get_sections_info(section="rd_note")
    assert rd_notes_section["R&D Note"] == rd_notes_expected

    release_notes_section = edit.get_sections_info(section="release_note")
    assert release_notes_section["Release Note"] == release_notes_expected
    
    lib_log_section = edit.get_sections_info(section="lib_log")
    assert lib_log_section["Lib Log"] == lib_log_expected

@pytest.mark.edit_some_field
def test_edit_some_field_draft_version(page, config, api):
    login = Login(page)
    edit = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Volkswagen"
    edit.search_information(make_name=make_name, function_name = feature)
    edit.clone_version()
    edit.reload_page()
    time.sleep(4)
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"update rd note at {generate_time}"
    lib_log_expected = f"update lib log at {generate_time}"
    # get 'release notes' before editing
    release_notes_before_edit = edit.get_sections_info(section="release_note")
    logger.info(f"release note: {release_notes_before_edit["Release Note"]}")

    resp, data, _ = api.run_and_wait_json(
            trigger=lambda: edit.edit_draft_version(rd_notes=rd_notes_expected, lib_log=lib_log_expected, is_save=True),
            base_api=config["base_api"],
            path_or_url="/api/version/update_release_note",
            method="PUT",
            expected_status=200,
            timeout=30000,
        )

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["data"]["rad_note"] == rd_notes_expected
    assert data["data"]["lib_log"] == lib_log_expected
    assert "Successfully update release_note" in data["message"]

    # delete.reload_page()
    time.sleep(2)

    # assert ui
    rd_notes_section = edit.get_sections_info(section="rd_note")
    assert rd_notes_section["R&D Note"] == rd_notes_expected
    
    lib_log_section = edit.get_sections_info(section="lib_log")
    assert lib_log_section["Lib Log"] == lib_log_expected
    release_notes_after_edit = edit.get_sections_info(section="release_note")
    logger.info(f"release note: {release_notes_after_edit["Release Note"]}")

    assert release_notes_before_edit["Release Note"] == release_notes_after_edit["Release Note"]




@pytest.mark.edit_empty
def test_edit_all_fields_with_empty(page, config, api):
    login = Login(page)
    edit = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Volkswagen"
    edit.search_information(make_name=make_name, function_name = feature)
    edit.clone_version()
    edit.reload_page()
    time.sleep(4)
    # get notes before editing
    rd_notes_expected = edit.get_sections_info(section="rd_note")
    lib_log_expected = edit.get_sections_info(section="lib_log")
    release_notes_expected = edit.get_sections_info(section="release_note")
    resp, data, _ = api.run_and_wait_json(
            trigger=lambda: edit.edit_draft_version(is_save=True),
            base_api=config["base_api"],
            path_or_url="/api/version/update_release_note",
            method="PUT",
            expected_status=200,
            timeout=30000,
        )

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    # assert data["data"]["rad_note"] == rd_notes_expected
    # assert data["data"]["lib_log"] == lib_log_expected
    assert "Successfully update release_note" in data["message"]

    # delete.reload_page()
    time.sleep(2)

    # assert ui
    rd_notes_section = edit.get_sections_info(section="rd_note")
    assert rd_notes_section["R&D Note"] == rd_notes_expected["R&D Note"]

    release_notes_section = edit.get_sections_info(section="release_note")
    assert release_notes_section["Release Note"] == release_notes_expected["Release Note"]
    
    lib_log_section = edit.get_sections_info(section="lib_log")
    assert lib_log_section["Lib Log"] == lib_log_expected["Lib Log"]

@pytest.mark.edit_cancel
def test_edit_cancel(page, config):
    login = Login(page)
    edit = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Volkswagen"
    edit.search_information(make_name=make_name, function_name = feature)
    edit.clone_version()
    edit.reload_page()
    time.sleep(4)
    rd_notes_before_edit = edit.get_sections_info(section="rd_note")
    release_notes_before_edit = edit.get_sections_info(section="release_note")
    lib_log_before_edit = edit.get_sections_info(section="lib_log")
    generate_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rd_notes_expected = f"update rd note at {generate_time}"
    release_notes_expected = f"update release note at {generate_time}"
    lib_log_expected = f"update lib log at {generate_time}"
    edit.edit_draft_version(rd_notes=rd_notes_expected, release_notes=release_notes_expected, lib_log=lib_log_expected, is_cancel=True)
    # assert
    rd_notes_after_edit = edit.get_sections_info(section="rd_note")
    release_notes_after_edit = edit.get_sections_info(section="release_note")
    lib_log_after_edit = edit.get_sections_info(section="lib_log")
    
    assert rd_notes_before_edit["R&D Note"] == rd_notes_after_edit["R&D Note"]
    assert release_notes_before_edit["Release Note"] == release_notes_after_edit["Release Note"]
    assert lib_log_before_edit["Lib Log"] == lib_log_after_edit["Lib Log"]