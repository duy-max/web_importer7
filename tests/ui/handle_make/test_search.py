# tests/test_example.py
from page.home_page import Home
from page.login_page import Login
import pytest
from corelib import logger

logger = logger.Logger(prefix="test_search", log_level="INFO")


# using page argument from fixture  (conftest.py)
@pytest.mark.search_valid
def test_search_with_valid_conditions(page, config, api):
    login = Login(page)
    search = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    feature = "Common"   
    make_enm = 39  # mapping of Honda
    make_name = "Volkswagen"
    resp, data, _ = api.run_and_wait_json(
        trigger=lambda: search.search_information(make_name=make_name, function_name=feature),
        base_api=config["base_api"],
        path_or_url="/api/version/function_make",
        method="GET",
        query={"feature": feature, "make_enm": make_enm},
        expected_status=200,
        timeout=30000,
    )
    logger.info(f"json reponse: {data}")
    # assert api
    assert data is not None
    assert resp.status == 200

    # assert ui
    assert search.is_production_db_display() is True


@pytest.mark.search_invalid_make_name
def test_search_with_invalid_make_name(page, config):
    login = Login(page)
    search = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    make_name = "Lambo"
    search.search_information(make_name=make_name,by_fill=True)
    # assert validate
    error_msg = search.get_form_error_msg()
    logger.info(f"error msg: {error_msg}")
    assert "Please choose existing make" in error_msg

@pytest.mark.search_invalid_function_name
def test_search_with_invalid_function_name(page, config):
    login = Login(page)
    search = Home(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password=config["password"])
    function_name = "Huracan"
    search.search_information(function_name=function_name,by_fill=True)
    # assert validate
    error_msg = search.get_form_error_msg()
    logger.info(f"error msg: {error_msg}")
    assert "Please choose existing function" in error_msg