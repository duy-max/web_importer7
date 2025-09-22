from locators import login as login_lcts
from corelib.web_handler import WebHandler
from corelib import logger

class Login(WebHandler):
    def __init__(self, page):
        super().__init__(page)
        self.LCT = login_lcts
        self.logger = logger.Logger(prefix="WebHandler", log_level= "INFO")

    def navigate_to_login_page(self, base_url: str):
        self.goto_page(base_url + "/login")
    
    def login_into_website(self, username: str, password: str):
        self.fill_element(self.LCT.USERNAME, username)
        self.fill_element(self.LCT.PASSWORD, password)
        self.click_element(self.LCT.LOGIN_BTN)
    
    def get_form_error_msg(self):
        return self.get_text(self.LCT.FORM_ERROR_MSG)
    
    def toggle_eyes_icon(self):
        self.click_element(self.LCT.EYES_ICON)
    
    def get_attribute_password(self):
        return self.get_value_attribute(self.LCT.PASSWORD, attribute_name="type")

    def is_handle_make_display(self):
        return self.is_visible(self.LCT.HANDLE_MAKE, timeout=3000)

    def get_username_pass_error_msg(self):
        return self.get_texts(self.LCT.FORM_ERROR_MSG)
    
    def clear_form_login(self):
        self.click_element(self.LCT.CLEAR_BTN)
        username_txt = self.get_value_attribute(self.LCT.USERNAME, attribute_name="value")
        return username_txt