from page.home_page import Home
from page.login_page import Login
import pytest
from corelib import logger, email_handler
import time
from datetime import datetime, timedelta

logger = logger.Logger(prefix="test_search", log_level="INFO")

@pytest.mark.import_excel_1
def test_import_excel_with_conditions_meet(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username_1"], password=config["password_1"])
    function_name = "Mode06"
    make_name = "Volkswagen"
    test_case = "ConditionsMeet"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=2)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case= test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg

    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import: {importing_infor}")
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

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    # assert data["data"]["release_note"] == release_notes_expected
    # assert data["data"]["rad_note"] == rd_notes_expected
    # assert data["data"]["lib_log"] == lib_log_expected
    # assert "Successfully update release_note" in data["message"]
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(5)

    # assert ui
    draft_infor,_ = import_ex.get_draft_version_infor()
    logger.info(f"draft infor: {draft_infor}")
    actual_time_draft_str = draft_infor["Date"]
    actual_time_draft = datetime.strptime(actual_time_draft_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time_draft - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time_draft}"
    assert official_latest_infor["Function Version"] != draft_infor["Function Version"]
    assert draft_infor["Status"] == "DRAFT"
    assert draft_infor["R&D Note"] == "View"
    assert draft_infor["Log Changes"] == "View"
    assert draft_infor["Release Note"] == "View"
    assert draft_infor["Lib Log"] == "View"

@pytest.mark.import_excel_empty_file
def test_import_excel_with_empty_zip_file(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "Mode06"
    make_name = "Volkswagen"
    test_case = "Empty"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=2)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case=test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import first: {importing_infor}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="sqlimporter@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="NOT FOUND",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    # assert data["data"]["release_note"] == release_notes_expected
    # assert data["data"]["rad_note"] == rd_notes_expected
    # assert data["data"]["lib_log"] == lib_log_expected
    # assert "Successfully update release_note" in data["message"]
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(2)

    # assert ui
    draft_infor = import_ex.get_draft_version_infor()
    assert draft_infor is None

@pytest.mark.skip(reason="Feature not ready yet")
def test_import_excel_with_zip_file_beyond_limit(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "Mode06"
    make_name = "Volkswagen"
    test_case = "Beyond100Mb"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=2)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case=test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import first: {importing_infor}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="sqlimporter@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="NOT FOUND",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    # assert data["data"]["release_note"] == release_notes_expected
    # assert data["data"]["rad_note"] == rd_notes_expected
    # assert data["data"]["lib_log"] == lib_log_expected
    # assert "Successfully update release_note" in data["message"]
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(2)

    # assert ui
    draft_infor = import_ex.get_draft_version_infor()
    assert draft_infor is None

@pytest.mark.skip(reason="Feature not ready yet")
def test_import_excel_with_zip_file_equal_limit(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "Mode06"
    make_name = "Volkswagen"
    test_case = "Equal100Mb"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=2)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case=test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import first: {importing_infor}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="sqlimporter@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="NOT FOUND",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    # assert data["data"]["release_note"] == release_notes_expected
    # assert data["data"]["rad_note"] == rd_notes_expected
    # assert data["data"]["lib_log"] == lib_log_expected
    # assert "Successfully update release_note" in data["message"]
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(2)

    # assert ui
    draft_infor = import_ex.get_draft_version_infor()
    assert draft_infor is None

@pytest.mark.import_excel
def test_import_excel_close_icon(page, config):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Mitsubishi"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    import_ex.import_excel(make_name=make_name, function_name=function_name, is_close= True)
    # assert


@pytest.mark.import_excel_delete
def test_import_excel_delete_icon(page, config):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "Ymme"
    make_name = "Volkswagen"
    test_case = "DeleteFile"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    import_ex.import_excel(make_name=make_name, function_name=function_name, test_case=test_case, is_remove=True)
    # assert
    notify_msg = import_ex.get_form_error_msg()
    assert "Please upload your file" in notify_msg


@pytest.mark.import_excel
def test_import_excel_remove_file(page, config):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Mitsubishi"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    import_ex.import_excel(make_name=make_name, function_name=function_name, is_remove=True)
    # assert -> file name dissapear after remove
    import_ex.import_excel(make_name=make_name, function_name=function_name)
    # assert -> file name display



@pytest.mark.excel_add_row
def test_import_excel_with_new_row_add(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Volkswagen"
    test_case = "RowAdded"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=30)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case= test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg

    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import: {importing_infor}")
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="innovaserver@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="Insert DB to Server",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    # assert data["data"]["release_note"] == release_notes_expected
    # assert data["data"]["rad_note"] == rd_notes_expected
    # assert data["data"]["lib_log"] == lib_log_expected
    # assert "Successfully update release_note" in data["message"]
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(5)

    # assert ui
    draft_infor,_ = import_ex.get_draft_version_infor()
    log_changes = import_ex.get_sections_pro_db_info(section="log_changes")
    logger.info(f"draft infor: {draft_infor}")
    actual_time_draft_str = draft_infor["Date"]
    actual_time_draft = datetime.strptime(actual_time_draft_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time_draft - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time_draft}"
    assert official_latest_infor["Function Version"] != draft_infor["Function Version"]
    assert draft_infor["Status"] == "DRAFT"
    assert draft_infor["R&D Note"] == "View"
    assert draft_infor["Log Changes"] == "View"
    assert draft_infor["Release Note"] == "View"
    assert draft_infor["Lib Log"] == "View"

    # assert log changes ui 
    assert log_changes["Log Changes"] != "No Log Changes available"

@pytest.mark.excel_edit_row
def test_import_excel_edit_row(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Volkswagen"
    test_case = "RowEdited"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=30)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case= test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg

    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import: {importing_infor}")
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="innovaserver@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="Insert DB to Server",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(5)

    # assert ui
    draft_infor,_ = import_ex.get_draft_version_infor()
    log_changes = import_ex.get_sections_pro_db_info(section="log_changes")
    logger.info(f"draft infor: {draft_infor}")
    actual_time_draft_str = draft_infor["Date"]
    actual_time_draft = datetime.strptime(actual_time_draft_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time_draft - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time_draft}"
    assert official_latest_infor["Function Version"] != draft_infor["Function Version"]
    assert draft_infor["Status"] == "DRAFT"
    assert draft_infor["R&D Note"] == "View"
    assert draft_infor["Log Changes"] == "View"
    assert draft_infor["Release Note"] == "View"
    assert draft_infor["Lib Log"] == "View"

    # assert log changes ui 
    assert log_changes["Log Changes"] != "No Log Changes available"

@pytest.mark.excel_delete_row
def test_import_excel_delete_row(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Volkswagen"
    test_case = "RowDeleted"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=30)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case= test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg

    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import: {importing_infor}")
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="innovaserver@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="Insert DB to Server",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(5)

    # assert ui
    draft_infor,_ = import_ex.get_draft_version_infor()
    log_changes = import_ex.get_sections_pro_db_info(section="log_changes")
    logger.info(f"draft infor: {draft_infor}")
    actual_time_draft_str = draft_infor["Date"]
    actual_time_draft = datetime.strptime(actual_time_draft_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time_draft - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time_draft}"
    assert official_latest_infor["Function Version"] != draft_infor["Function Version"]
    assert draft_infor["Status"] == "DRAFT"
    assert draft_infor["R&D Note"] == "View"
    assert draft_infor["Log Changes"] == "View"
    assert draft_infor["Release Note"] == "View"
    assert draft_infor["Lib Log"] == "View"

    # assert log changes ui 
    assert log_changes["Log Changes"] != "No Log Changes available"

@pytest.mark.excel_missing_id
def test_import_excel_missing_id_column(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Volkswagen"
    test_case = "MissingIDColumn"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=30)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case= test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg

    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import: {importing_infor}")
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="innovaserver@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="Insert DB to Server",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(5)

    # assert ui


@pytest.mark.excel_enum_failed
def test_import_excel_check_enum_failed(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Volkswagen"
    test_case = "CheckEnumFailed"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=30)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case= test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg

    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import: {importing_infor}")
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="innovaserver@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="Insert DB to Server",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(5)

    # assert ui



@pytest.mark.excel_enum_failed
def test_import_excel_check_template_failed(page, config, api):
    login = Login(page)
    import_ex = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "VinDecode"
    make_name = "Volkswagen"
    test_case = "CheckTemplateFailed"
    import_ex.search_information(make_name=make_name, function_name = function_name)
    draft_exists = import_ex.is_draft_existing()
    if draft_exists:
        import_ex.delete_draft_version(is_confirm=True)
        import_ex.reload_page()
        time.sleep(2)
    
    start_utc = email_handler.mark_now_utc() - timedelta(seconds=30)
    resp, data, create_time_exp = api.run_and_wait_json(
            trigger=lambda: import_ex.import_excel(make_name=make_name, function_name=function_name, test_case= test_case, is_confirm=True),
            base_api=config["base_api_import"],
            path_or_url="/api/importdata",
            method="POST",
            expected_status=200,
            timeout=30000,
        )
    logger.info(f"json reponse: {data}")
    infor_msg = import_ex.get_msg_infor()
    logger.info(f"message success: {infor_msg}")
    assert "Please wait for a few minutes; the results will be sent to your email upon completion" in infor_msg

    importing_infor = import_ex.get_data_by_row(row=1, action_include=False)
    logger.info(f"importing in test import: {importing_infor}")
    excel_email = email_handler.wait_for_excel_email(
    imap_server=config["imap_server"],
    imap_port=int(config.get("imap_port", 993)),
    username=config["imap_user"],
    password=config["imap_password"],
    sender_filter="innovaserver@vn.innova.com",
    cutoff_dt_utc=start_utc,
    subject_keyword="Insert DB to Server",
    delivery_wait=8,   # chờ lần đầu 8s cho mail tới
    timeout=240,
    interval=10,
    )

    logger.info(f"email full: {excel_email}")

    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["succeeded"] is True
    assert data["errors"] is None
    
    official_latest_infor = import_ex.get_data_by_row(row=2)
    actual_time_str = importing_infor["Date"]
    actual_time = datetime.strptime(actual_time_str, "%d-%m-%Y %H:%M:%S")
    delta = abs((actual_time - create_time_exp).total_seconds())
    logger.info(f"delta time : {delta}")
    assert delta < 50, f"Time mismatch: expected ~{create_time_exp}, got {actual_time}"
    assert official_latest_infor["Function Version"] != importing_infor["Function Version"]
    assert importing_infor["Status"] == "IMPORTING"
    assert importing_infor["R&D Note"] == ""
    assert importing_infor["Log Changes"] == ""
    assert importing_infor["Release Note"] == ""
    assert importing_infor["Lib Log"] == ""

    
    
    import_ex.reload_page()
    time.sleep(5)

    # assert ui