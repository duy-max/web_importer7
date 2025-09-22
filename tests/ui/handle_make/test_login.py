# tests/test_example.py
from page.login_page import Login
from playwright.sync_api import expect
import time
import pytest
from corelib import logger as _logger

logger = _logger.Logger(prefix="test_search", log_level="INFO")


@pytest.mark.valid_login
def test_login_with_valid_account(page, config, api):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    # login.login_into_website(username=config["username"], password=config["password"])
    resp, data, _= api.run_and_wait_json(
        trigger=lambda: login.login_into_website(username=config["username"], password=config["password"]),
        base_api=config["base_api"],
        path_or_url="/api/auth/local",
        method="POST",
        expected_status=200,
        timeout=30000,
    )
    logger.info(f"json reponse: {data}")
    assert resp.status == 200
    assert data["jwt"] is not None

    assert login.is_handle_make_display() is True


@pytest.mark.empty_both
def test_login_with_empty_username_password(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username="", password="")
    logger.info(f"list: {login.get_username_pass_error_msg()}")
    username_error_msg = login.get_username_pass_error_msg()[0]
    pass_error_msg = login.get_username_pass_error_msg()[1]
    assert "Please input your username!" in username_error_msg
    assert "Please input your password!" in pass_error_msg




@pytest.mark.empty_password
def test_login_with_empty_password(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password="")
    # assert
    error_msg = login.get_form_error_msg()
    assert "Please input your password!" in error_msg

@pytest.mark.empty_username
def test_login_with_empty_username(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username="", password=config["password"])
    error_msg = login.get_form_error_msg()
    assert "Please input your username!" in error_msg

    # assert
@pytest.mark.wrong_pass
def test_login_with_wrong_password(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username=config["username"], password="1234")
    assert login.is_handle_make_display() is False


@pytest.mark.wrong_username
def test_login_with_wrong_username(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username="duy.tr", password=config["password"])
    assert login.is_handle_make_display() is False


@pytest.mark.toggle_eye
def test_login_toggle_eye_icon(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username="", password=config["password"])
    type_before_toggle = login.get_attribute_password()
    login.toggle_eyes_icon()
    type_after_toggle = login.get_attribute_password()
    assert "password" == type_before_toggle.lower()
    assert "text" == type_after_toggle.lower()


@pytest.mark.clear_btn
def test_login_clear_btn(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    login.login_into_website(username="duy.truong", password="1234")
    username_txt = login.clear_form_login()
    assert username_txt == ""


@pytest.mark.skip(reason="Feature not ready yet")
def test_login_forgot_password_link(page, config):
    login = Login(page)
    login.navigate_to_login_page(base_url = config["base_url"])
    # login.toggle_eye_icon()
    # login.login_into_website(username="duy.tr", password=config["password"])
    # assert
    
    
    

