from page.home_page import Home
from page.login_page import Login
import pytest
from corelib import logger
import time

logger = logger.Logger(prefix="test_search", log_level="INFO")

@pytest.mark.delete_valid
def test_delete_version(page, config, api):
    login = Login(page)
    delete = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Volkswagen"
    delete.search_information(make_name=make_name, function_name = feature)

    resp_clone, data_clone, _ = api.run_and_wait_json(
        trigger=lambda: delete.clone_version(),
        base_api=config["base_api"],
        path_or_url="/api/version/clone-data",
        method="POST",
        expected_status=200,
        timeout=30000,
    )
    logger.info(f"json reponse: {data_clone}")
    delete_id = data_clone["newVersion"]["id"]
    delete.reload_page()
    time.sleep(4)
    # delete.action_function(function_name="delete")

    if delete_id:
        resp, data, _ = api.run_and_wait_json(
            trigger=lambda: delete.delete_draft_version(is_confirm=True),
            base_api=config["base_api"],
            path_or_url=f"/api/versions/{delete_id}",
            method="DELETE",
            expected_status=200,
            timeout=30000,
        )
    else:
        logger.info(f"Can't not extract id from clone version")

    msg_successful = delete.get_msg_infor()
    assert "Delete successful" in msg_successful
    
    # assert api
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data is not None
    
    delete.reload_page()
    time.sleep(2)
    
    # assert ui
    draft_infor = delete.get_data_by_row(row = 1)
    assert draft_infor["Status"] != "DRAFT"
    
@pytest.mark.delete_visi
def test_delete_btn_visibility(page, config):
    login = Login(page)
    delete = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Volkswagen"
    delete.search_information(make_name=make_name, function_name = feature)
    if delete.is_draft_existing():
        assert delete.is_delete_btn_visibility() is True
    else:
        assert delete.is_delete_btn_visibility() is False

@pytest.mark.delete_cancel
def test_delete_btn_cancel(page, config):
    login = Login(page)
    delete = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"
    make_name = "Volkswagen"
    delete.search_information(make_name=make_name, function_name = feature)
    delete.clone_version()
    delete.reload_page()
    time.sleep(2)
    delete.delete_draft_version(is_cancel=True)
    data_first_row = delete.get_data_by_row(row = 1)
    assert data_first_row["Status"] == "DRAFT"