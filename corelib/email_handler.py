
from __future__ import annotations
import imaplib
import email
from email.parser import BytesParser
from email.policy import default
from email.message import Message
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re
import time
from pathlib import Path
from corelib import logger as _logger

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None  # Bạn cần cài: pip install beautifulsoup4

logger = _logger.Logger(prefix="email", log_level="INFO")

# ======================================================================
# Helpers thời gian
# ======================================================================
def mark_now_utc() -> datetime:
    """
    Lấy mốc thời gian UTC ngay trước khi click Download.
    """
    now = datetime.now(timezone.utc)
    logger.info(f"[mark_now_utc] anchor={now.isoformat()}")
    return now

# ======================================================================
# Kết nối & tìm email
# ======================================================================
def _open_imap(server: str, port: int, username: str, password: str):
    """
    Kết nối IMAP SSL.
    """
    logger.info(f"[IMAP] connect {server}:{port} as {username}")
    m = imaplib.IMAP4_SSL(server, port)
    m.login(username, password)
    return m

def _imap_search(imap_conn: imaplib.IMAP4_SSL, criteria: str) -> List[bytes]:
    """
    Thực hiện search và trả về danh sách ID (bytes).
    """
    status, data = imap_conn.search(None, criteria)
    if status != "OK":
        return []
    if not data or not data[0]:
        return []
    return data[0].split()

def _parse_msg_date(msg: Message) -> Optional[datetime]:
    """
    Parse header 'Date' thành datetime UTC.
    """
    raw = msg.get("date")
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None

# ======================================================================
# Trích xuất body & link
# ======================================================================
def _extract_body(msg: Message) -> tuple[str, str]:
    """
    Trả về (plain_text, html_text).
    """
    plain, html = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = (part.get_content_type() or "").lower()
            disp = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disp:
                continue
            try:
                payload = part.get_payload(decode=True) or b""
                text = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
            except Exception:
                text = ""
            if ctype == "text/plain" and not plain:
                plain = text
            elif ctype == "text/html" and not html:
                html = text
    else:
        ctype = (msg.get_content_type() or "").lower()
        payload = msg.get_payload(decode=True) or b""
        text = payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
        if ctype == "text/html":
            html = text
        else:
            plain = text
    return plain, html

def _extract_all_links(text: str) -> List[str]:
    if not text:
        return []
    pattern = re.compile(r"https?://[^\s\"'<>()]+", re.IGNORECASE)
    return pattern.findall(text)

# ======================================================================
# Parse nội dung email Excel
# ======================================================================
def parse_excel_email_details(subject: str, sender: str, html_body: str, plain_body: str) -> Dict[str, Any]:
    """
    Parse các trường Make / Function Name / Version / Enum version / DB Link trong email Excel.
    Ưu tiên HTML; fallback text.
    """
    source = html_body or plain_body
    details = {
        "subject": subject,
        "from": sender,
        "make": None,
        "function_name": None,
        "version": None,
        "enum_version": None,
        "download_url": None,
        "raw_links": [],
        "raw_html": html_body[:4000] if html_body else "",
        "raw_text": plain_body[:4000] if plain_body else ""
    }

    # Lấy link “Download Excel File” (ưu tiên anchor chứa text “Download Excel”)
    if html_body and BeautifulSoup:
        try:
            soup = BeautifulSoup(html_body, "html.parser")
            # Anchor theo text
            a_tag = soup.find("a", string=re.compile(r"Download\s+Excel", re.IGNORECASE))
            if a_tag and a_tag.get("href"):
                details["download_url"] = a_tag.get("href").strip()
            # Nếu chưa thấy, lấy anchor đầu có .zip
            if not details["download_url"]:
                z = soup.find("a", href=re.compile(r"\.zip($|\?)", re.IGNORECASE))
                if z and z.get("href"):
                    details["download_url"] = z.get("href").strip()
        except Exception:
            pass

    if not details["download_url"]:
        # fallback tìm link .zip bằng regex
        zip_links = [l for l in _extract_all_links(source) if l.lower().endswith(".zip") or ".zip?" in l.lower()]
        if zip_links:
            details["download_url"] = zip_links[0]

    # Lấy danh sách tất cả links (debug / cần thiết)
    details["raw_links"] = _extract_all_links(source)

    # Regex các trường bên trong list <li> (HTML) hoặc dòng text
    patterns = {
        "make": r"[Mm]ake:\s*</?strong>?\s*([^<\n\r]+)",
        "function_name": r"[Ff]unction\s*Name:\s*</?strong>?\s*([^<\n\r]+)",
        "version": r"[Vv]ersion:\s*</?strong>?\s*([^<\n\r]+)",
        "enum_version": r"[Ee]num\s*[Vv]ersion:\s*</?strong>?\s*([^<\n\r]+)",
    }

    for key, pat in patterns.items():
        m = re.search(pat, source, re.IGNORECASE)
        if m:
            details[key] = m.group(1).strip()

    # Làm sạch giá trị 'null'
    if details["enum_version"] and details["enum_version"].lower() == "null":
        details["enum_version"] = None

    return details

# def parse_excel_email_details(subject: str, sender: str, html_body: str, plain_body: str) -> Dict[str, Any]:
    """
    Parse email cho cả 2 loại:
      - Download: Action: Download the Excel File ...
      - Import:   Action: Import the Excel File ...
    Trả về dict thống nhất.

    Trường trả về:
      subject, from, action (IMPORT|DOWNLOAD|UNKNOWN),
      make, function_name,
      version (download case),
      from_version, new_version (import case),
      enum_version,
      start_import_local (chuỗi gốc), start_import_utc (ISO) – chỉ với IMPORT,
      download_url (nếu có),
      raw_links, raw_html, raw_text
    """
    source = html_body or plain_body or ""
    action = "UNKNOWN"
    if re.search(r"Action:\s*Import the Excel File", source, re.IGNORECASE):
        action = "IMPORT"
    elif re.search(r"Action:\s*Download the Excel File", source, re.IGNORECASE):
        action = "DOWNLOAD"

    details: Dict[str, Any] = {
        "subject": subject,
        "from": sender,
        "action": action,
        "make": None,
        "function_name": None,
        "version": None,         # dùng cho email download
        "from_version": None,    # dùng cho email import
        "new_version": None,     # dùng cho email import
        "enum_version": None,
        "start_import_local": None,
        "start_import_utc": None,
        "download_url": None,
        "raw_links": [],
        "raw_html": html_body[:6000] if html_body else "",
        "raw_text": plain_body[:6000] if plain_body else "",
    }

    # 1. Tìm download_url (chỉ có ở email download)
    if html_body and BeautifulSoup:
        try:
            soup = BeautifulSoup(html_body, "html.parser")
            # Anchor có chữ Download Excel
            a_tag = soup.find("a", string=re.compile(r"Download\s+Excel", re.IGNORECASE))
            if a_tag and a_tag.get("href"):
                details["download_url"] = a_tag.get("href").strip()
            if not details["download_url"]:
                z = soup.find("a", href=re.compile(r"\.zip($|\?)", re.IGNORECASE))
                if z and z.get("href"):
                    details["download_url"] = z.get("href").strip()
        except Exception:
            pass

    if not details["download_url"]:
        # fallback tìm link .zip
        zip_links = [l for l in _extract_all_links(source) if ".zip" in l.lower()]
        if zip_links:
            details["download_url"] = zip_links[0]

    # 2. Links thô để debug
    details["raw_links"] = _extract_all_links(source)

    # 3. Regex chung cho cả HTML / Plain text (chấp nhận dạng bullet “• ” hoặc không)
    def r(label):
        # Cho phép: "•  Make:" hoặc "Make:" hoặc "<li><strong>Make:</strong>"
        return rf"(?:•\s*)?{label}:\s*</?strong>?\s*([^<\r\n]+)"

    patterns = {
        "make": r("Make"),
        "function_name": r("Function\s*Name"),
        "version": r("Version"),          # (download) – trong import có From/New Version nên version sẽ không xuất hiện
        "from_version": r("From\s*Version"),
        "new_version": r("New\s*Version"),
        "enum_version": r("Enum\s*Version"),
    }

    for key, pat in patterns.items():
        m = re.search(pat, source, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            details[key] = val if val else None

    # 4. Làm sạch enum_version 'null'
    if details["enum_version"] and details["enum_version"].lower() == "null":
        details["enum_version"] = None

    # 5. Parse thời gian bắt đầu import (chỉ email import)
    #    Ví dụ: Start importing at: 14:41:59 17/09/2025 GMT+7
    if action == "IMPORT":
        m_time = re.search(
            r"Start importing at:\s*([0-9]{2}):([0-9]{2}):([0-9]{2})\s+([0-9]{2})/([0-9]{2})/([0-9]{4})\s+GMT([+\-][0-9]{1,2})",
            source,
            re.IGNORECASE,
        )
        if m_time:
            hh, mm, ss, dd, MM, yyyy, tz_off = m_time.groups()
            details["start_import_local"] = f"{hh}:{mm}:{ss} {dd}/{MM}/{yyyy} GMT{tz_off}"
            try:
                # Tạo datetime với offset giờ
                offset_hours = int(tz_off)
                dt_local = datetime(
                    int(yyyy), int(MM), int(dd),
                    int(hh), int(mm), int(ss),
                    tzinfo=timezone.utc
                ) + (offset_hours * 3600 - 0) * 0  # placeholder để tránh cảnh báo
                # Cách chuẩn: tạo tzinfo bằng timezone(timedelta(hours=offset_hours))
                from datetime import timedelta
                dt_with_tz = datetime(
                    int(yyyy), int(MM), int(dd),
                    int(hh), int(mm), int(ss),
                    tzinfo=timezone(timedelta(hours=offset_hours))
                )
                details["start_import_utc"] = dt_with_tz.astimezone(timezone.utc).isoformat()
            except Exception:
                pass

    # 6. Điều chỉnh: nếu action=IMPORT thì 'version' (download) không dùng; nếu action=DOWNLOAD không có from/new_version.
    if action == "IMPORT":
        details["version"] = None  # đảm bảo không gây nhầm lẫn

    return details

# ======================================================================
# Hàm chính: lấy email Excel mới nhất sau cutoff
# ======================================================================
# def fetch_latest_excel_email(
#     imap_server: str,
#     imap_port: int,
#     username: str,
#     password: str,
#     sender_filter: str,
#     cutoff_dt_utc: Optional[datetime],
#     subject_keyword: str = "Excel",
#     delivery_wait: int = 5,
#     max_search_days: int = 7,
#     download_first_match: bool = True
# ) -> Optional[Dict[str, Any]]:
#     """
#     Lấy email Excel mới nhất thỏa:
#       - Từ sender_filter
#       - Subject chứa subject_keyword (case-insensitive)
#       - Ngày/giờ >= cutoff_dt_utc (nếu truyền)
#     delivery_wait: sleep (giây) sau khi trigger để mail kịp về.
#     max_search_days: an toàn nếu cutoff ở giữa ngày (IMAP SINCE chỉ theo ngày).
#     download_first_match: trả về match đầu tiên (mới nhất).
#     """
#     if cutoff_dt_utc and cutoff_dt_utc.tzinfo is None:
#         raise ValueError("cutoff_dt_utc phải timezone-aware (UTC).")

#     logger.info(f"[ExcelMail] WAIT {delivery_wait}s for email delivery...")
#     time.sleep(delivery_wait)

#     # IMAP SINCE chỉ theo ngày -> dùng ngày nhỏ nhất giữa cutoff và (cutoff - max_search_days)
#     if cutoff_dt_utc:
#         since_date = cutoff_dt_utc.date()
#         # Có thể lùi thêm vài ngày để chắc chắn không bỏ sót nếu timezone chênh
#         since_date_str = since_date.strftime("%d-%b-%Y")
#     else:
#         since_date_str = datetime.now(timezone.utc).strftime("%d-%b-%Y")

#     criteria = f'(FROM "{sender_filter}" SINCE {since_date_str})'
#     logger.info(f"[ExcelMail] search criteria: {criteria}")

#     imap_conn = None
#     try:
#         imap_conn = _open_imap(imap_server, imap_port, username, password)
#         imap_conn.select("INBOX")

#         ids = _imap_search(imap_conn, criteria)
#         if not ids:
#             logger.info("[ExcelMail] no email IDs found.")
#             return None

#         logger.info(f"[ExcelMail] total matched by search (date-only) = {len(ids)}")

#         # Duyệt mới nhất trước
#         for eid in reversed(ids):
#             status, data = imap_conn.fetch(eid, "(RFC822)")
#             if status != "OK" or not data:
#                 continue

#             msg = BytesParser(policy=default).parsebytes(data[0][1])
#             subject = msg.get("subject") or ""
#             sender = msg.get("from") or ""
#             received_dt = _parse_msg_date(msg)

#             logger.info(f"  • [{received_dt}] {subject} - From: {sender}")

#             # Lọc thời gian chính xác
#             if cutoff_dt_utc and received_dt and received_dt < cutoff_dt_utc:
#                 logger.info("    ↳ Skip (older than cutoff)")
#                 continue

#             # Lọc subject
#             if subject_keyword.lower() not in subject.lower():
#                 logger.info(f"    ↳ Skip (subject lacks '{subject_keyword}')")
#                 continue

#             # Lọc đúng sender (phòng trường hợp FROM search match alias)
#             if sender_filter.lower() not in sender.lower():
#                 logger.info("    ↳ Skip (sender mismatch)")
#                 continue

#             logger.info("   ✅ MATCH: subject contains keyword & time >= cutoff")

#             plain_body, html_body = _extract_body(msg)
#             details = parse_excel_email_details(subject, sender, html_body, plain_body)
#             details["received_at"] = received_dt.isoformat() if received_dt else None
#             details["message_id"] = eid.decode()

#             return details

#         logger.info("[ExcelMail] no matching Excel email after cutoff.")
#         return None
#     finally:
#         try:
#             if imap_conn:
#                 imap_conn.logout()
#         except Exception:
#             pass

def fetch_latest_email(
    imap_server: str,
    imap_port: int,
    username: str,
    password: str,
    sender_filter: str,
    cutoff_dt_utc: Optional[datetime],
    subject_keyword: str ,  
    delivery_wait: int = 5,
    max_search_days: int = 7,
    download_first_match: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Lấy email mới nhất thỏa:
      - Từ sender_filter
      - Subject chứa subject_keyword (case-insensitive)
      - Ngày/giờ >= cutoff_dt_utc (nếu truyền)
    """
    if cutoff_dt_utc and cutoff_dt_utc.tzinfo is None:
        raise ValueError("cutoff_dt_utc phải timezone-aware (UTC).")

    logger.info(f"[ExcelMail] WAIT {delivery_wait}s for email delivery...")
    time.sleep(delivery_wait)

    if cutoff_dt_utc:
        since_date = cutoff_dt_utc.date()
        since_date_str = since_date.strftime("%d-%b-%Y")
    else:
        since_date_str = datetime.now(timezone.utc).strftime("%d-%b-%Y")

    criteria = f'(FROM "{sender_filter}" SINCE {since_date_str})'
    logger.info(f"[ExcelMail] search criteria: {criteria}")

    imap_conn = None
    try:
        imap_conn = _open_imap(imap_server, imap_port, username, password)
        imap_conn.select("INBOX")

        ids = _imap_search(imap_conn, criteria)
        if not ids:
            logger.info("[ExcelMail] no email IDs found.")
            return None

        logger.info(f"[ExcelMail] total matched by search (date-only) = {len(ids)}")

        # Duyệt mới nhất trước
        for eid in reversed(ids):
            status, data = imap_conn.fetch(eid, "(RFC822)")
            if status != "OK" or not data:
                continue

            msg = BytesParser(policy=default).parsebytes(data[0][1])
            subject = msg.get("subject") or ""
            sender = msg.get("from") or ""
            received_dt = _parse_msg_date(msg)

            logger.info(f"  • [{received_dt}] {subject} - From: {sender}")

            # Lọc thời gian
            if cutoff_dt_utc and received_dt and received_dt < cutoff_dt_utc:
                logger.info("    ↳ Skip (older than cutoff)")
                continue

            # Lọc subject
            if subject_keyword.lower() not in subject.lower():
                logger.info(f"    ↳ Skip (subject lacks '{subject_keyword}')")
                continue

            # Lọc sender
            if sender_filter.lower() not in sender.lower():
                logger.info("    ↳ Skip (sender mismatch)")
                continue

            logger.info("   ✅ MATCH: subject contains keyword & time >= cutoff")

            # Chỉ parse Excel nếu keyword là "Excel"
            if subject_keyword.lower() == "excel":
                plain_body, html_body = _extract_body(msg)
                details = parse_excel_email_details(subject, sender, html_body, plain_body)
            else:
                # Chỉ trả về subject & sender cho các loại email khác
                details = {
                    "subject": subject,
                    "from": sender,
                    "received_at": received_dt.isoformat() if received_dt else None,
                    "message_id": eid.decode()
                }

            return details

        logger.info("[ExcelMail] no matching email after cutoff.")
        return None
    finally:
        try:
            if imap_conn:
                imap_conn.logout()
        except Exception:
            pass


# ======================================================================
# Hàm wrapper chờ (poll) đến khi có email Excel
# ======================================================================
def wait_for_excel_email(
    imap_server: str,
    imap_port: int,
    username: str,
    password: str,
    sender_filter: str,
    cutoff_dt_utc: datetime,
    subject_keyword: str,
    delivery_wait: int = 5,
    timeout: int = 180,
    interval: int = 8,
) -> Dict[str, Any]:
    """
    Poll cho đến khi tìm được email Excel sau cutoff.
    """
    start = time.time()
    attempt = 0
    logger.info(f"[ExcelMail] START wait | cutoff={cutoff_dt_utc.isoformat()} | timeout={timeout}s | interval={interval}s")
    while time.time() - start < timeout:
        attempt += 1
        remain = timeout - int(time.time() - start)
        logger.info(f"[ExcelMail] attempt={attempt} remain={remain}s")

        result = fetch_latest_email(
            imap_server=imap_server,
            imap_port=imap_port,
            username=username,
            password=password,
            sender_filter=sender_filter,
            cutoff_dt_utc=cutoff_dt_utc,
            subject_keyword=subject_keyword,
            delivery_wait=delivery_wait if attempt == 1 else 0,  # chỉ sleep ở vòng đầu
        )
        if result:
            logger.info(f"[ExcelMail] FOUND Excel email: {result.get('subject')}")
            return result

        logger.info("[ExcelMail] not found yet, sleep...")
        time.sleep(interval)

    raise TimeoutError("Không tìm thấy email Excel trong thời gian chờ.")

# ======================================================================
# Tiện ích lưu file (tùy chọn)
# ======================================================================

