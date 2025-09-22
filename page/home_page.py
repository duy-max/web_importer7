from locators import home as lcts
from corelib.web_handler import WebHandler
from corelib import utils
from datetime import datetime
import time

class Home(WebHandler):
    def __init__(self, page):
        super().__init__(page)
        self.LCT = lcts
    
    def search_information(self, make_name: str="", function_name: str="", by_fill: bool = False):
        self.click_element(self.LCT.HANDLE_MAKE)
        if by_fill:
            self.fill_element(self.LCT.MAKE_BOX, make_name)
            self.fill_element(self.LCT.FUNCTION_BOX,  function_name)
    
        else:
            self.click_element(self.LCT.MAKE_BOX)
            self.clicks(self.LCT.MAKE_DROPDOWN, 
                        on_elements= lambda _, e: self.get_text(e).lower() == make_name.lower(),
                        stop_on_first= True,
                        )
            self.click_element(self.LCT.FUNCTION_BOX)
            self.clicks(self.LCT.FUNCTION_DROPDOWN, 
                        on_elements= lambda _, e: self.get_text(e).lower() == function_name.lower(),
                        stop_on_first= True,
                        )
        self.click_element(self.LCT.SEARCH_BTN) 

       

    def is_production_db_display(self):
        return self.is_visible(self.LCT.PRODUCTION_DB)
    
    def is_clone_version_visibility(self):
        return self.is_visible(self.LCT.CLONE_VERSION_BTN_PRO_DB, timeout=5000)
    
    def is_delete_btn_visibility(self):
        self.clicks(self.LCT.ARROWS_DOWN_ICON_PRO_DB, on_elements=lambda i, _: i == 0, stop_on_first=True)
        return self.is_visible(self.LCT.DELETE_ACTION, timeout=5000)
    
    def is_draft_existing(self, is_dev_db: bool = False):
        data_row_1 = self.get_data_by_row(row = 1, action_include=False, is_dev_db=is_dev_db)
        self.logger.info(f"data row 1: {data_row_1}")
        if not data_row_1:
            return False
        return data_row_1["Status"] == "DRAFT"
    
    def clone_version(self, is_confirm: bool = True, is_cancel: bool = False, is_close:bool = False, 
                      is_dev_db: bool = False, db_type: str = "", from_version: None | str = ""):
        # add logic check "Draft" if exist -> delete -> clone
        draft_exists = self.is_draft_existing(is_dev_db = is_dev_db)
        if draft_exists:
            self.delete_draft_version(is_confirm=True, is_dev_db=is_dev_db)
            time.sleep(2)
            self.reload_page()
        if is_dev_db:
            self.click_element(self.LCT.CLONE_VERSION_BTN_DEV_DB)
            version_radio_idx = self.click_random_index(self.LCT.VERSIONS_RDBTN)
            version_txt = self.get_text_by_index(self.LCT.VERSIONS_TEXT, version_radio_idx)
            self.click_element(self.LCT.DB_TYPE_DROPDOWN)
            self.clicks(self.LCT.DB_TYPE_ITEMS,
                        on_elements= lambda _, e: self.get_text(e).lower() == db_type.lower(),
                        stop_on_first=True
                        )
            if isinstance(from_version, str):
                self.click_element(self.LCT.FROM_VERSION_DROPDOWN)
                if from_version.strip():  # non-empty string
                    self.clicks(
                        self.LCT.FROM_VERSION_ITEMS,
                        on_elements=lambda _, e: self.get_text(e).lower() == from_version.lower(),
                        stop_on_first=True
                    )
                else:  # empty string
                    self.clicks(
                        self.LCT.FROM_VERSION_ITEMS,
                        on_elements=lambda i, _: i == 0,
                        stop_on_first=True
                    )  
        else:
            self.click_element(self.LCT.CLONE_VERSION_BTN_PRO_DB)
            version_radio_idx = self.click_random_index(self.LCT.VERSIONS_RDBTN)
            version_txt = self.get_text_by_index(self.LCT.VERSIONS_TEXT, version_radio_idx)
       
        if is_close:
            self.click_element(self.LCT.X_ICON)
        if is_cancel:
            self.click_element(self.LCT.CANCEL_BTN)
        if is_confirm:
            self.click_element(self.LCT.CONFIRM_BTN)
            expected_time = datetime.now()
            self.logger.info(f"version update expected: {version_txt}, expected_time={expected_time}")
            result = {
                "version_update": version_txt,
                "version_created_date": expected_time
            }
            return result

    def get_msg_infor(self):
        return self.get_text(self.LCT.SUCCESSFUL_MSG)
    
    def get_draft_version_infor(self, is_dev_db: bool = False):
        # headers = self.get_texts(self.LCT.HEADERS_PRO_DB)
        status_locator   = self.LCT.DRAFT_STATUS_DEV_DB if is_dev_db else self.LCT.DRAFT_STATUS_PRO_DB
        headers_locator  = self.LCT.HEADERS_DEV_DB if is_dev_db else self.LCT.HEADERS_PRO_DB
        cells_locator    = self.LCT.CELLS_DEV_DB if is_dev_db else self.LCT.CELLS_PRO_DB
        arrows_locator   = self.LCT.ARROWS_DOWN_ICON_DEV_DB if is_dev_db else self.LCT.ARROWS_DOWN_ICON_PRO_DB
        action_column    = self.LCT.ACTION_COLUMN_DEV_DB if is_dev_db else self.LCT.ACTION_COLUMN_PRO_DB
        draft_info = None
        if self.is_visible(status_locator, timeout=10000):
            draft_info = self.get_tabular_data(headers_locator, locators=cells_locator, row=1)
            self.logger.info(f"value of draft info: {draft_info}")

            self.clicks(arrows_locator, on_elements=lambda i, _: i == 0, stop_on_first=True)

            action_info = {
                self.get_text(action_column): self.get_texts(self.LCT.ACTION_ITEMS)
            }
            self.logger.info(f"value of action info: {action_info}")

            draft_info.update(action_info)
            # ĐÓNG action để không làm lệch index các cell cho lần đọc sau
            self.clicks(arrows_locator, on_elements=lambda i, _: i == 0, stop_on_first=True)
            self.logger.info(f"value of draft info full: {draft_info}")
        return draft_info
  

    
    def get_data_by_row(self, row: int | None = None, action_include: bool = True, is_dev_db: bool = False):
        # chọn locator theo môi trường
        headers_locator = self.LCT.HEADERS_DEV_DB if is_dev_db else self.LCT.HEADERS_PRO_DB
        cells_locator   = self.LCT.CELLS_DEV_DB if is_dev_db else self.LCT.CELLS_PRO_DB
        arrows_locator  = self.LCT.ARROWS_DOWN_ICON_DEV_DB if is_dev_db else self.LCT.ARROWS_DOWN_ICON_PRO_DB
        action_column   = self.LCT.ACTION_COLUMN_DEV_DB if is_dev_db else self.LCT.ACTION_COLUMN_PRO_DB

        data = self.get_tabular_data(headers_locator, locators=cells_locator, row=row)

        if action_include:
            self.clicks(arrows_locator, on_elements=lambda i, _: i == (row - 1), stop_on_first=True)
            action_info = {
                self.get_text(action_column): self.get_texts(self.LCT.ACTION_ITEMS)
            }
            self.logger.info(f"value of action info: {action_info}")
            data.update(action_info)
            self.logger.info(f"value of draft info full: {data}")
        return data

    def get_sections_info(self, section: str, is_dev_db:bool = False):
    # map section name -> index
        section_map = {
            "rd_note": 0,
            "log_changes": 1,
            "release_note": 2,
            "lib_log": 3,
        }

        if section not in section_map:
            raise ValueError(f"Invalid section '{section}'. Must be one of {list(section_map.keys())}")

        # click button theo index map
    # chọn locator theo flag
        locator = (
            self.LCT.DRAFT_VIEWS_BTN_DEV_DB
            if is_dev_db
            else self.LCT.DRAFT_VIEWS_BTN_PRO_DB
        )

    # click button theo index map
        self.clicks(
            locator,
            on_elements=lambda i, _: i == section_map[section],
            stop_on_first=True,
        )

        self.logger.info(f"value of section map: {section_map[section]}")

        # lấy các field dạng "Key: Value" trong <p>
        detail_fields = self.get_texts(self.LCT.LOG_CHANGE_DETAIL_FIELDS)
        detail_info = utils.parse_fields_to_dict(detail_fields)

        # lấy log changes riêng
        log_changes_title = self.get_text(self.LCT.LOG_CHANGE_TITLE).rstrip(":").strip()
        log_changes_content = self.get_text(self.LCT.LOG_CHANGE_CONTENTS)

        # gộp lại (giữ nguyên key gốc, không replace khoảng trắng)
        detail_info[log_changes_title.strip()] = log_changes_content

        self.logger.info(f"value of {section} info: {detail_info}")
        self.click_element(self.LCT.CLOSE_SECTION_ICON)
        time.sleep(2)
        return detail_info
    
    # def get_sections_dev_db_info(self, section: str):
    # # map section name -> index
    #     section_map = {
    #         "rd_note": 0,
    #         "log_changes": 1,
    #         "release_note": 2,
    #         "lib_log": 3,
    #     }

    #     if section not in section_map:
    #         raise ValueError(f"Invalid section '{section}'. Must be one of {list(section_map.keys())}")

    #     # click button theo index map
    #     self.clicks(
    #         self.LCT.DRAFT_VIEWS_BTN_DEV_DB,
    #         on_elements=lambda i, _: i == section_map[section],
    #         stop_on_first=True,
    #     )

    #     self.logger.info(f"value of section map: {section_map[section]}")

    #     # lấy các field dạng "Key: Value" trong <p>
    #     detail_fields = self.get_texts(self.LCT.LOG_CHANGE_DETAIL_FIELDS)
    #     detail_info = utils.parse_fields_to_dict(detail_fields)

    #     # lấy log changes riêng
    #     log_changes_title = self.get_text(self.LCT.LOG_CHANGE_TITLE).rstrip(":").strip()
    #     log_changes_content = self.get_text(self.LCT.LOG_CHANGE_CONTENTS)

    #     # gộp lại (giữ nguyên key gốc, không replace khoảng trắng)
    #     detail_info[log_changes_title.strip()] = log_changes_content

    #     self.logger.info(f"value of {section} info: {detail_info}")
    #     self.click_element(self.LCT.CLOSE_SECTION_ICON)
    #     time.sleep(2)
    #     return detail_info

    
    def delete_draft_version(self, is_confirm: bool = False, is_cancel: bool = False, is_dev_db:bool = False):
        locator = (
            self.LCT.ARROWS_DOWN_ICON_DEV_DB
            if is_dev_db
            else self.LCT.ARROWS_DOWN_ICON_PRO_DB
        )

        self.clicks(locator, on_elements=lambda i, _: i == 0, stop_on_first=True)
        self.click_element(self.LCT.DELETE_ACTION)
        if is_confirm:
            self.click_element(self.LCT.OK_CONFIRM_BTN)
        if is_cancel:
            self.click_element(self.LCT.CANCEL_CONFIRM_BTN)
    
    def edit_draft_version(self, rd_notes: str = "", release_notes: str ="", lib_log:str="" , is_save: bool = False, is_cancel: bool = False):
        self.clicks(self.LCT.ARROWS_DOWN_ICON_PRO_DB, on_elements=lambda i, _: i == 0, stop_on_first=True)
        self.click_element(self.LCT.EDIT_ACTION)
        self.fill_element(self.LCT.RD_NOTES_BOX, rd_notes)
        self.fill_element(self.LCT.RELEASE_NOTES_BOX, release_notes)
        self.fill_element(self.LCT.LIB_LOG_BOX, lib_log)
        if is_save:
            self.click_element(self.LCT.SAVE_ACTION_BTN)
        if is_cancel:
            self.click_element(self.LCT.CANCEL_ACTION_BTN)
            self.click_element(self.LCT.OK_CONFIRM_BTN)
    
    def release_draft_version(self, rd_notes: str = "", release_notes: str ="", lib_log:str="" , is_confirm: bool = False, 
                              is_cancel: bool = False, is_close: bool = False, is_dev_db: bool = False):
        locator = (
            self.LCT.ARROWS_DOWN_ICON_DEV_DB
            if is_dev_db
            else self.LCT.ARROWS_DOWN_ICON_PRO_DB
        )
        self.clicks(locator, on_elements=lambda i, _: i == 0, stop_on_first=True)
        
        self.click_element(self.LCT.RELEASE_ACTION)
        self.fill_element(self.LCT.RD_NOTE_RELEASE, rd_notes)
        self.fill_element(self.LCT.RELEASE_NOTE_RELEASE, release_notes)
        self.fill_element(self.LCT.LIB_LOG_RELEASE, lib_log)
        if is_confirm:
            self.click_element(self.LCT.CONFIRM_BTN)
        if is_cancel:
            self.click_element(self.LCT.CANCEL_BTN)
        if is_close:
            self.click_element(self.LCT.X_ICON)

    def import_excel(self, make_name: str, function_name: str ,test_case: str, common_version: str="", is_confirm: bool = False, 
                     is_remove: bool = False, is_close = False):
        self.click_element(self.LCT.IMPORT_EXCEL_BTN_PRO_DB)
        self.click_element(self.LCT.COMMON_VER_DROPDOWN)
        if common_version:
            self.clicks(self.LCT.COMMON_VERS_LIST, 
                        on_elements= lambda _, e: self.get_text(e).lower().strip() == common_version.lower().strip(),
                        stop_on_first= True,
                        )
        else:
            self.clicks(self.LCT.COMMON_VERS_LIST, 
                        on_elements= lambda i, _: i == 0,
                        stop_on_first= True,
                        )
        # self.click_element(self.LCT.UPLOAD_BTN)
        file_path = utils.find_import_file(make_name=make_name, function_name=function_name, test_case=test_case)
        self.page.set_input_files("input[type=file]", str(file_path))
        self.logger.info(f"[import_excel] set_input_files -> {file_path}")
        create_time = datetime.now()
        if is_confirm:
            self.click_element(self.LCT.CONFIRM_BTN)
        if is_remove:
            self.click_element(self.LCT.REMOVE_FILE_UPLOAD_ICON)
        if is_close:
            self.click_element(self.LCT.X_ICON)
        return create_time

    def download_excel(self):
        draft_exists = self.is_draft_existing()
        if draft_exists:
            self.delete_draft_version(is_confirm=True)
            time.sleep(2)
            self.reload_page()
        data_first_row = self.get_data_by_row(row = 1, action_include=False)
        self.logger.info(f"data row 1: {data_first_row}")
        self.clicks(self.LCT.ARROWS_DOWN_ICON_PRO_DB, on_elements=lambda i, _: i == 0, stop_on_first=True)
        self.click_element(self.LCT.DOWNLOAD_EXCEL_BTN_PRO_DB)
        return data_first_row

    def check_notification(self, notification_name:str):
        noti_map = {
            'error':0,
            'bell':1
        }
        self.clicks(self.LCT.ICONS_NOTIFICATION,
                    on_elements= lambda i, _: i == noti_map[notification_name],
                    stop_on_first=True
                    )
    
    def get_latest_bell_notification(self):
        self.click_element(self.LCT.BELL_ICON)
        title = self.get_texts(self.LCT.NOTIFICATION_TITLES,
                       on_elements= lambda i, _: i == 0
                       )
        self.logger.info(f"title notification: {title}")
        content = self.get_texts(self.LCT.NOTIFICATION_CONTENTS,
                       on_elements= lambda i, _: i == 0
                       )
        self.logger.info(f"content notification: {content}")

        self.click_element(self.LCT.BELL_ICON)
        return {"title": title,
                "content": content}
    
    def get_form_error_msg(self):
        return self.get_text(self.LCT.FORM_ERROR_MSG)