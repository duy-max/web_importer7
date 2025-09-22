from page.home_page import Home
from page.login_page import Login
import pytest
from corelib import logger
import time
from datetime import datetime, timezone, timedelta

logger = logger.Logger(prefix="test_search", log_level="INFO")

@pytest.mark.clone_valid
def test_clone_version_with_valid_conditions(page, config, api):
    login = Login(page)
    clone = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "VinDecode"
    make_name = "Volkswagen"
    clone.search_information(make_name=make_name, function_name = feature)

    resp, data, version_update = api.run_and_wait_json(
        trigger=lambda: clone.clone_version(),
        base_api=config["base_api"],
        path_or_url="/api/version/clone-data",
        method="POST",
        expected_status=200,
        timeout=30000,
    )
    msg_successful = clone.get_msg_infor()
    logger.info(f"json reponse: {data}")
    assert "Clone version request submitted successfully." in msg_successful
    
    clone.reload_page()
    time.sleep(4)
    bell_notification = clone.get_latest_bell_notification()
    logger.info(f"notification: {bell_notification}")
    draft_info = clone.get_draft_version_infor()
    logger.info(f"draft infor: {draft_info}")
    official_latest_info = clone.get_data_by_row(row=1, action_include=False)
    logger.info(f"official latest first: {official_latest_info}")
    official_latest_info = clone.get_data_by_row(row=2, action_include=False)
    logger.info(f"official latest seconde: {official_latest_info}")
    # assert api
    assert data is not None
    assert resp.status == 200
    assert data["newVersion"]["status"] == "Draft"
    assert data["newVersion"]["make_version"] == version_update["version_update"]
    assert data["newVersion"]["from_version"] == official_latest_info["Function Version"]
    assert data["newVersion"]["release_note"] is None
    assert data["newVersion"]["lib_log"] is None
    assert data["newVersion"]["rad_note"] is None
    created_at_str = data["newVersion"]["createdAt"] 
    # Parse ISO string from API (UTC)
    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    # Convert to Vietnam time (UTC+7)
    local_time = created_at.astimezone(timezone(timedelta(hours=7)))
    logger.info(f"local time: {local_time}")

    # Format similar to UI
    ui_time = local_time.strftime("%d-%m-%Y %H:%M:%S")
    logger.info(f"ui time: {ui_time}")
    assert ui_time == draft_info["Date"]
    # assert data["newVersion"]["log_changes"] is not None


    
    # assert ui
    # date is set current time
    actual_time_str = draft_info["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    expected_time = version_update["version_created_date"]
    delta = abs((actual_time - expected_time).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 30, f"Time mismatch: expected ~{expected_time}, got {actual_time}"
    # version is set by 
    assert version_update["version_update"] == draft_info["Function Version"]
    # status is set to "Draft"
    assert draft_info["Status"] == "DRAFT"
    # 'R&D Note': 'View', 'Log Changes': 'View', 'Release Note': 'View', 'Lib Log': 'View'
    rd_note = clone.get_sections_info(section="rd_note")
    release_note = clone.get_sections_info(section="release_note")
    lib_log = clone.get_sections_info(section="lib_log")
    assert draft_info["R&D Note"] == "View" and rd_note["R&D Note"] == "No R&D Note available"
    assert draft_info["Release Note"] == "View" and release_note["Release Note"] == "No Release Note available"
    assert draft_info["Lib Log"] == "View" and lib_log["Lib Log"] == "No Lib Log available"

    # check log changes
    # log_changes = clone.get_sections_pro_db_info(section="log_changes")
    # assert draft_info["Log Changes"] == "View" and log_changes["Log Changes"] == "No Log Changes available"

    # action column
    expected_actions = ["Edit", "Release", "Delete"]
    assert set(draft_info["Action"]) == set(expected_actions)

@pytest.mark.skip(reason="Feature not ready yet")
def test_clone_version_with_valid_conditions_dev_db(page, config, api):
    login = Login(page)
    clone = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "VinDecode"
    make_name = "Volkswagen"
    clone.search_information(make_name=make_name, function_name = feature)
    db_type = "Production Database"
    resp, data, version_update = api.run_and_wait_json(
        trigger=lambda: clone.clone_version(is_dev_db=True, db_type = db_type),
        base_api=config["base_api"],
        path_or_url="/api/version/clone-data",
        method="POST",
        expected_status=200,
        timeout=30000,
    )
    msg_successful = clone.get_msg_infor()
    logger.info(f"json reponse: {data}")
    assert "Clone version request submitted successfully." in msg_successful
    
    clone.reload_page()
    time.sleep(4)
    bell_notification = clone.get_latest_bell_notification()
    logger.info(f"notification: {bell_notification}")
    draft_info = clone.get_draft_version_infor(is_dev_db=True)
    # official_latest_info = clone.get_data_by_row(row = 2)
    
    # assert api
    assert data is not None
    assert resp.status == 200
    assert data["newVersion"]["status"] == "Draft"
    assert data["newVersion"]["make_version"] == version_update["version_update"]
    # assert data["newVersion"]["from_version"] == official_latest_info["Function Version"]
    assert data["newVersion"]["release_note"] is None
    assert data["newVersion"]["lib_log"] is None
    assert data["newVersion"]["rad_note"] is None
    created_at_str = data["newVersion"]["createdAt"] 
    # Parse ISO string from API (UTC)
    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    # Convert to Vietnam time (UTC+7)
    local_time = created_at.astimezone(timezone(timedelta(hours=7)))
    logger.info(f"local time: {local_time}")

    # Format similar to UI
    ui_time = local_time.strftime("%d-%m-%Y %H:%M:%S")
    logger.info(f"ui time: {ui_time}")
    assert ui_time == draft_info["Date"]
    # assert data["newVersion"]["log_changes"] is not None


    
    # assert ui
    # date is set current time
    actual_time_str = draft_info["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    expected_time = version_update["version_created_date"]
    delta = abs((actual_time - expected_time).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 30, f"Time mismatch: expected ~{expected_time}, got {actual_time}"
    # version is set by 
    assert version_update["version_update"] == draft_info["Function Version"]
    # status is set to "Draft"
    assert draft_info["Status"] == "DRAFT"
    # 'R&D Note': 'View', 'Log Changes': 'View', 'Release Note': 'View', 'Lib Log': 'View'
    rd_note = clone.get_sections_info(section="rd_note", is_dev_db=True)
    release_note = clone.get_sections_info(section="release_note", is_dev_db=True)
    lib_log = clone.get_sections_info(section="lib_log", is_dev_db=True)
    assert draft_info["R&D Note"] == "View" and rd_note["R&D Note"] == "No R&D Note available"
    assert draft_info["Release Note"] == "View" and release_note["Release Note"] == "No Release Note available"
    assert draft_info["Lib Log"] == "View" and lib_log["Lib Log"] == "No Lib Log available"

    # check log changes
    # log_changes = clone.get_sections_pro_db_info(section="log_changes")
    # assert draft_info["Log Changes"] == "View" and log_changes["Log Changes"] == "No Log Changes available"

    # action column
    expected_actions = ["Edit", "Release", "Delete"]
    assert set(draft_info["Action"]) == set(expected_actions)

@pytest.mark.skip(reason="Feature not ready yet")
def test_clone_version_without_selecting_from_version(page, config, api):
    login = Login(page)
    clone = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "VinDecode"
    make_name = "Volkswagen"
    clone.search_information(make_name=make_name, function_name = feature)
    db_type = "Production Database"
    from_version = None
    clone.clone_version(is_dev_db=True, db_type = db_type, from_version=from_version)
    error_msg = clone.get_form_error_msg()
    assert "'fromVersion' is required" in error_msg



@pytest.mark.clone
def test_clone_version_btn_visibility(page, config):
    login = Login(page)
    clone = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "VinDecode"
    make_name = "Volkswagen"
    clone.search_information(make_name=make_name, function_name = feature)
    if clone.is_draft_existing:
        assert clone.is_clone_version_visibility() is True
    else:
        assert clone.is_clone_version_visibility() is False

@pytest.mark.clone
def test_clone_version_cancel(page, config):
    login = Login(page)
    clone = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "VinDecode"
    make_name = "Volkswagen"
    clone.search_information(make_name=make_name, function_name = feature)
    clone.clone_version(is_confirm=False, is_cancel=True)
    data_first_row = clone.get_data_by_row(row = 1)
    assert data_first_row["Status"] == "OFFICIAL"

@pytest.mark.clone
def test_clone_version_close_icon(page, config):
    login = Login(page)
    clone = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "VinDecode"
    make_name = "Volkswagen"
    clone.search_information(make_name=make_name, function_name = feature)
    clone.clone_version(is_confirm=False, is_close=True)
    data_first_row = clone.get_data_by_row(row = 1)
    assert data_first_row["Status"] == "OFFICIAL"
