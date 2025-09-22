from __future__ import annotations
from typing import Callable, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import Page, Response
from corelib import logger

class ApiClient:
    def __init__(self, page: Page, base_api: Optional[str] = None, log_level: str = "INFO"):
        self.page = page
        self.base_api = (base_api or "").rstrip("/")
        self.logger = logger.Logger(prefix="API", log_level=log_level)

    # determine which response is the one the test is waiting for
    def _match_predicate(
        self,
        method: Optional[str],
        path_or_url: str,
        query: Optional[Dict[str, Any]],
        allow_subset: bool = True,
        base_api_override: Optional[str] = None,
    ):
        base = (base_api_override or self.base_api or "").rstrip("/")
        full = path_or_url if path_or_url.startswith("http") else f"{base}{path_or_url}"

        def _norm(v: Any) -> str:
            return str(v)

        def _pred(resp: Response) -> bool:
            try:
                if method and resp.request.method.upper() != method.upper():
                    return False
                if not resp.url.startswith(full):
                    return False
                if query:
                    qs = parse_qs(urlparse(resp.url).query)
                    # so khớp subset: mọi key trong query phải khớp (lấy phần tử đầu)
                    for k, v in query.items():
                        if k not in qs:
                            return False
                        if _norm(qs[k][0]) != _norm(v):
                            return False
                return True
            except Exception:
                return False

        return _pred

    def run_and_wait_response(
        self,
        trigger: Callable[[], Any],
        path_or_url: str,
        method: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        timeout: float = 30000,
        base_api: Optional[str] = None,  # override theo call
    ) -> Tuple[Response, Any]:
        pred = self._match_predicate(method=method, path_or_url=path_or_url, query=query, base_api_override=base_api)
        self.logger.info(f"Waiting API: {method or '*'} {path_or_url} query={query or {}} base={base_api or self.base_api}")
        with self.page.expect_response(pred, timeout=timeout) as resp_info:
            result = trigger()
        resp = resp_info.value
        self.logger.info(f"API status: {resp.status} {resp.url}")
        return resp, result

    def run_and_wait_json(
        self,
        trigger: Callable[[], Any],
        path_or_url: str,
        method: Optional[str] = None,
        query: Optional[Dict[str, Any]] = None,
        expected_status: Optional[int] = 200,
        timeout: float = 30000,
        base_api: Optional[str] = None,  # override theo call
    ) -> Tuple[Response, Any, Any]:
        resp, result = self.run_and_wait_response(
            trigger, path_or_url, method=method, query=query, timeout=timeout, base_api=base_api
        )
        if expected_status is not None:
            assert resp.status == expected_status, f"Expected {expected_status}, got {resp.status} for {resp.url}"
        try:
            data = resp.json()
        except Exception:
            data = None
        return resp, data, result