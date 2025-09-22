from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import Locator, expect
from corelib import utils, logger
from playwright.sync_api import Response
from typing import Callable, Any
import random
import time


BY_MAP = {
    "role": "get_by_role",
    "text": "get_by_text",
    "placeholder": "get_by_placeholder",
    "label": "get_by_label",
    "alt-text": "get_by_alt_text",
    "title": "get_by_title",
    "test-id": "get_by_test_id",
    "id": "locator",
    "xpath":"locator"
}



DEFAULT_TIMEOUT = 30_000  # 30s

class WebHandler:
    def __init__(self, page):
        self.page = page
        self.logger = logger.Logger(prefix="WebHandler", log_level= "INFO")
    
    def click_element(self, locator: str | Locator, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Fill text into the input with auto-wait and custom timeout.
        """
        try:
            locator_obj = self._resolve_locator(locator)
            # highlight trước khi click
            # self.highlight_element(locator_obj)
            self.highlight_flash_element(locator_obj)
            locator_obj.click(timeout = timeout)
            self.logger.info(f"Clicked: {locator}")
        except PlaywrightTimeoutError:
            raise Exception(f"Timeout {timeout/1000}s khi click {locator}")
    
    def fill_element(self, locator: str | Locator, value: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Fill text vào input với auto-wait + custom timeout.
        """
        try:
            locator_obj = self._resolve_locator(locator)
            locator_obj.fill(value, timeout=timeout)
            self.logger.info(f"Filled '{value}' into: {locator}")

        except PlaywrightTimeoutError:
            raise Exception(f"Timeout {timeout/1000}s khi fill {locator}")
    def highlight_element(self, locator: str | Locator, duration: float = 0.3, repeat: int = 2) -> None:
        """
        Highlight a locator by flashing its border for debugging.
        :param locator: Locator or selector string
        :param duration: Thời gian (giây) mỗi lần nhấp nháy
        :param repeat: Số lần nhấp nháy
        """
        locator_obj = self._resolve_locator(locator)

        script = """
        (element, duration, repeat) => {
            const originalBorder = element.style.border;
            let i = 0;
            function flash() {
                if (i >= repeat * 2) {
                    element.style.border = originalBorder;
                    return;
                }
                element.style.border = (i % 2 === 0) ? '2px solid red' : originalBorder;
                i++;
                setTimeout(flash, duration * 1000);
            }
            flash();
        }
        """
        locator_obj.evaluate(script, {"duration": duration, "repeat": repeat})
        self.logger.info(f"Highlighted: {locator}")
    def highlight_flash_element(
        self, 
        locator: str | Locator, 
        duration: float = 0.3, 
        color: str = "red", 
        border: int = 2, 
        flashes: int = 3
    ) -> None:
        """
        Flash highlight on an element to make it visually stand out (Playwright version).
        """
        locator_obj = self._resolve_locator(locator)

        # Lấy style gốc
        original_style = locator_obj.evaluate("el => el.getAttribute('style') || ''")
        highlight_style = f"{original_style}; border: {border}px dashed {color};"

        for _ in range(flashes):
            # Set highlight style
            locator_obj.evaluate(
                "(el, style) => el.setAttribute('style', style)", 
                highlight_style
            )
            time.sleep(duration)

            # Set lại style cũ
            locator_obj.evaluate(
                "(el, style) => el.setAttribute('style', style)", 
                original_style
            )
            time.sleep(duration)

        self.logger.info(f"Flashed highlight on: {locator}")

    def goto_page(self, url: str, timeout: int  = DEFAULT_TIMEOUT) -> Response | None:
        self.logger.info(f"Navigating to: {url}")
        return self.page.goto(url, timeout=timeout)

    # convert str -> locator object if not locator
    def _resolve_locator(self, target: str | Locator) -> Locator:
        if isinstance(target, Locator):
            return target
        if not isinstance(target, str):
            raise TypeError(f"Unsupported target type: {type(target)}")
        parsed = utils.extract_locator_to_element(target)
        method = parsed["method"]
        args = parsed["args"]
        if method not in BY_MAP:
            raise ValueError(f"Unsupported locator method: {method}")
        return getattr(self.page, BY_MAP[method])(*args)
    
    def expect_disabled(self, target: str | Locator, timeout: int = DEFAULT_TIMEOUT, message: str | None = None) -> None:
        loc = self._resolve_locator(target)
        try:
            expect(loc).to_be_disabled(timeout=timeout)
            self.logger.info(f"disabled: {target}")
        except AssertionError as e:
            self.logger.error(f"[FAIL] disabled: {target} -> {e}")
            raise AssertionError(message or str(e))

    def expect_checked(self, target: str | Locator, timeout: int = DEFAULT_TIMEOUT, message: str | None = None) -> None:
        loc = self._resolve_locator(target)
        try:
            expect(loc).to_be_checked(timeout=timeout)
            self.logger.info(f"[PASS] checked: {target}")
        except AssertionError as e:
            self.logger.error(f"[FAIL] checked: {target} -> {e}")
            raise AssertionError(message or str(e))

    def expect_has_attribute(self, target: str | Locator, name: str, value: str, timeout: int = DEFAULT_TIMEOUT, message: str | None = None) -> None:
        loc = self._resolve_locator(target)
        try:
            expect(loc).to_have_attribute(name, value, timeout=timeout)
            self.logger.info(f"[PASS] attribute {name}='{value}': {target}")
        except AssertionError as e:
            self.logger.error(f"[FAIL] attribute {name}='{value}': {target} -> {e}")
            raise AssertionError(message or str(e))

    def expect_contains_text(self, target: str | Locator, text: str , timeout: int = DEFAULT_TIMEOUT, message: str | None = None) -> None:
        loc = self._resolve_locator(target)
        try:
            expect(loc).to_contain_text(text, timeout=timeout)
            self.logger.info(f"[PASS] contains_text '{text}': {target}")
        except AssertionError as e:
            self.logger.error(f"[FAIL] contains_text '{text}': {target} -> {e}")
            raise AssertionError(message or str(e))
    
    def expect_enabled(self, target: str | Locator, timeout: int = DEFAULT_TIMEOUT, message: str | None = None) -> None:
        loc = self._resolve_locator(target)
        try:
            expect(loc).to_be_enabled(timeout=timeout)
            self.logger.info(f"[PASS] enabled: {target}")
        except AssertionError as e:
            self.logger.error(f"[FAIL] enabled: {target} -> {e}")
            raise AssertionError(message or str(e))
    
    def scroll_into_view(self, target: str | Locator, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Scroll to the specified element. If the target matches multiple elements, scroll to the first one.
        """
        loc = self._resolve_locator(target).first
        try:
            loc.scroll_into_view_if_needed(timeout=timeout)
        except Exception:
            pass
    def press(self, target: str | Locator, key: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        """
        Press a key on the specified element. 
        If the target matches multiple elements, press on the first one.
        
        :param target: locator string or Locator object
        :param key: key to press (e.g. "Enter", "Backspace", "Control+A")
        :param timeout: timeout in ms
        """
        loc = self._resolve_locator(target).first
        try:
            loc.press(key, timeout=timeout)
        except Exception as e:
            self.logger.warning(f"Failed to press {key} on {target}: {e}")
            
    def is_visible(self, target: str | Locator, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """
        Kiểm tra element có visible trong khoảng timeout hay không.
        Trả về True/False thay vì raise luôn, để có thể dùng linh hoạt trong logic.
        """
        loc = self._resolve_locator(target)
        try:
            expect(loc).to_be_visible(timeout=timeout)
            self.logger.info(f"[PASS] visible: {target}")
            return True
        except AssertionError as e:
            self.logger.error(f"[FAIL] visible: {target} -> {e}")
            return False

    def is_invisible(self, target: str | Locator, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """
        Check if element is invisible or not present within timeout.
        Return True/False instead of raising.
        """
        loc = self._resolve_locator(target)
        try:
            expect(loc).to_be_hidden(timeout=timeout)
            self.logger.info(f"[PASS] invisible: {target}")
            return True
        except AssertionError as e:
            self.logger.error(f"[FAIL] invisible: {target} -> {e}")
            return False

    
    def get_text(self, target: str | Locator, timeout: int = DEFAULT_TIMEOUT) -> str:
        
        # get first element 
        loc = self._resolve_locator(target).first
        try:
            return (loc.inner_text(timeout=timeout) or "").strip()
        except Exception:
            return ""
    
    def get_value_attribute(self, target: str | Locator, attribute_name: str, timeout: int = DEFAULT_TIMEOUT) -> str:
        """
        Get the value of a given attribute from the first element matching the locator.
    
        :param target: str | Locator - The locator or selector of the element
        :param attribute_name: str - The name of the attribute to retrieve
        :param timeout: int - Timeout in ms
        :return: str - Value of the attribute (empty string if not found or None)
        """
        loc = self._resolve_locator(target).first
        try:
            value = loc.get_attribute(attribute_name, timeout=timeout)
            return (value or "").strip()
        except Exception:
            return ""

    def _action(
        self,
        target: str | Locator,
        action: Callable[[Locator], Any],
        on_elements: Callable[[int, Locator], bool] = lambda index, loc: True,
        stop_on_first: bool = False,
        timeout: int = DEFAULT_TIMEOUT,
        action_name: str = "action",
    ) -> list[Any]:
        """
        Apply 'action' to elements filtered by on_elements.
        Returns a list of results (if the action returns anything).
        """
        loc = self._resolve_locator(target)
        try:
            loc.first.wait_for(state="attached", timeout=timeout)
        except PlaywrightTimeoutError:
            raise Exception(f"No elements present @ `{target}` within {timeout/1000}s")

        count = loc.count()
        self.logger.info(f"`{target}` has {count} element(s); applying {action_name} conditionally.")
        results: list[Any] = []
        applied = 0

        for i in range(count):
            nth = loc.nth(i)
            self.logger.info(f"text cua locator {nth}: {self.get_text(nth)}")
            try:
                if not on_elements(i, nth):
                    continue
                # if is_scroll:
                #     try:
                #         self.scroll_into_view(nth, timeout=timeout)
                #     except Exception:
                #         pass
                res = action(nth)
                results.append(res)
                applied += 1
                # self.logger.warning(f"{action_name} applied on index {i} @ `{target}`")
                if stop_on_first:
                    break
            except PlaywrightTimeoutError:
                self.logger.error(f"Timeout when {action_name} index {i} @ `{target}`")
            except Exception as e:
                self.logger.error(f"Failed to {action_name} index {i} @ `{target}` -> {e}")

        if applied == 0:
            self.logger.warning(f"No element matched condition for `{target}` during {action_name}.")
        return results
    

    def clicks(
        self,
        target: str | Locator,
        on_elements: Callable[[int, Locator], bool] = lambda index, loc: True,
        stop_on_first: bool = True,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
       Click elements filtered by on_elements.
        """
        return self._action(
            target=target,
            action=lambda l: self.click_element(l),
            on_elements=on_elements,
            stop_on_first=stop_on_first,
            timeout=timeout,
            action_name="click_element",
        )

    def get_texts(self, locator_or_elements: str | Locator, 
        on_elements: Callable[[int, Locator], bool] = lambda index, loc: True,
        stop_on_first: bool = False,
        timeout: int = DEFAULT_TIMEOUT) -> list[str]:
        """
        Get text from multiple elements:
        If a locator is provided → find all elements matching the locator
        If a list/tuple of elements is provided → get text from each element
        Returns a list of texts
        """
        # _action nhận action là callable trên Locator
        return self._action(
            target=locator_or_elements,
            action=lambda l: self.get_text(l),
            on_elements=on_elements,
            timeout= timeout,
            # mặc định lấy tất cả element
            stop_on_first=stop_on_first,    # lấy tất cả element, không dừng
            action_name="get_text"
        )
    # def get_texts(self, locator_or_elements: str | Locator | list) -> list[str]:
    #     """
    #     Get text from multiple elements:
    #     If a locator is provided → find all elements matching the locator
    #     If a list/tuple of elements is provided → get text from each element
    #     Returns a list of texts
    #     """
    #     # _action nhận action là callable trên Locator
    #     return self._action(
    #         target=locator_or_elements,
    #         action=lambda l: self.get_text(l),
    #         # mặc định lấy tất cả element
    #         is_scroll=False,        # không cần scroll khi lấy text
    #         stop_on_first=False,    # lấy tất cả element, không dừng
    #         action_name="get_text"
    #     )

    
    def click_random_index(self, radio_locator: str) -> int:
        """
       Click a random element within the locator and return the index clicked.
        """
        locators = self._resolve_locator(radio_locator)
        count = locators.count()
        if count == 0:
            raise Exception(f"No elements found for {radio_locator}")

        random_index = random.randint(0, count - 1)
        self.logger.info(f"Clicking random element index={random_index}")
        self.logger.info(f"locator click random {locators.nth(random_index)}")
        self.click_element(locators.nth(random_index))
        return random_index
    
    def get_text_by_index(self, text_locator: str, index: int) -> str:
        """
       Get the text of an element by index within the locator, using the existing get_text function.
        """
        loc_text = self._resolve_locator(text_locator)
        if index >= loc_text.count():
            raise Exception(f"Index {index} out of range for {text_locator}")
        
        # Sử dụng get_text của bạn
        self.logger.info(f"locator text random {loc_text.nth(index)}")
        text = self.get_text(loc_text.nth(index))
        self.logger.info(f"Text at index {index}: {text}")
        return text
    
    def reload_page(self, wait_until: str = "domcontentloaded", timeout: int = DEFAULT_TIMEOUT) -> Response | None:
        """
        Reload (F5) current page.
        wait_until: "load" | "domcontentloaded" | "networkidle"
        """
        self.logger.info("Reloading current page")
        try:
            return self.page.reload(wait_until=wait_until, timeout=timeout)
        except PlaywrightTimeoutError:
            raise Exception(f"Timeout {timeout/1000}s when reloading page")

    def forward(self, wait_until: str = "domcontentloaded", timeout: int = DEFAULT_TIMEOUT) -> Response | None:
        """
        Go forward to the next page in history (if any).
        """
        self.logger.info("Navigating forward")
        try:
            return self.page.go_forward(wait_until=wait_until, timeout=timeout)
        except PlaywrightTimeoutError:
            raise Exception(f"Timeout {timeout/1000}s when going forward")

    def backward(self, wait_until: str = "domcontentloaded", timeout: int = DEFAULT_TIMEOUT) -> Response | None:
        """
       Go back to the previous page in history (if any).
        """
        self.logger.info("Navigating backward")
        try:
            return self.page.go_back(wait_until=wait_until, timeout=timeout)
        except PlaywrightTimeoutError:
            raise Exception(f"Timeout {timeout/1000}s when going backward")



    def get_tabular_data(self, header: str | list | tuple, locators: str | Locator, row: int | None =None):
        """
        Get data having table format
        :param header: (list/tuple) list of column name in header
        :param locator_or_elements: (str) sample locator or (list/tuple) list of WebElements
        :param row: (int) row number-th to get, None -> get all rows
        :return: (list) if `row` is None, (dict) if `row` is available, (None) if no data available
        """
        if isinstance(header, (list, tuple)):
            header_texts = list(header)
        else:
        # header là locator
            header_texts = self.get_texts(header)
        _row = utils.soft_format(row, int)
        data = self.get_texts(locators)
        return utils.group_tabular_data(header_texts, data, _row)

    def fill_all(
        self,
        target: str | Locator,
        text: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> int:
        """
        Fill the same text into all elements matching the locator (from index 0 to n-1).
        Returns the number of elements filled
        """
        loc = self._resolve_locator(target)
        try:
            loc.first.wait_for(state="attached", timeout=timeout)
        except PlaywrightTimeoutError:
            raise Exception(f"No elements present @ `{target}` within {timeout/1000}s")

        count = loc.count()
        if count == 0:
            self.logger.warning(f"No elements found for `{target}` to fill.")
            return 0

        self.logger.info(f"Filling {count} element(s) @ `{target}` with text: {text!r}")
        filled = 0
        for i in range(count):
            nth = loc.nth(i)
            try:
                # if is_scroll:
                #     try:
                #         self.scroll_into_view(nth, timeout=timeout)
                #     except Exception:
                #         pass
                nth.fill(text, timeout=timeout)
                self.logger.info(f"[fill_all] index={i} OK")
                filled += 1
            except PlaywrightTimeoutError:
                self.logger.error(f"[fill_all] Timeout filling index={i} @ `{target}`")
            except Exception as e:
                self.logger.error(f"[fill_all] Failed filling index={i} @ `{target}` -> {e}")

        if filled == 0:
            self.logger.warning(f"No element filled for `{target}`.")
        return filled