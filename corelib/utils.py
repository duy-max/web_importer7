try:
    import time
    import hmac
    import hashlib
    import yaml
    import platform
    import json
    from corelib import logger
    from yaml.scanner import ScannerError
    from json.decoder import JSONDecodeError
    from pathlib import Path
    import re
    import requests


except ImportError as imp_err:
    print('There was an error importing files - From %s' % __file__)
    print('\n---{{{ Failed - ' + format(imp_err) + ' }}}---\n')
    raise

logger = logger.Logger(prefix="utils", log_level="INFO")


def convert_value_type(value: str):
    # Trim whitespace
    value = value.strip()

    # Remove quotes if present
    if (value.startswith("'") and value.endswith("'")) or \
       (value.startswith('"') and value.endswith('"')):
        return value[1:-1]

    # Convert boolean
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False

    # Convert number
    if value.replace(".", "", 1).isdigit():
        # support both int and float
        return int(value) if value.isdigit() else float(value)

    # Return as string
    return value


def handle_role_locator(rest: str):
    # Ví dụ: rest = "button|name=Login"
    parts = rest.split("|")
    role_name = parts[0]  # "button"
    option_strings = parts[1:]  # ["name=Login"]

    options = {}

    for option_string in option_strings:
        if "=" in option_string:
            key, value = option_string.split("=", 1)
            options[key] = convert_value_type(value)

    return {"method": "role", "args": [role_name, options]}


def extract_locator_to_element(locator: str):
    # Bước 1: Tách method và phần còn lại
    colon_index = locator.find(":")
    if colon_index == -1:
        raise ValueError(f"Invalid locator format: {locator}")

    method = locator[:colon_index]
    rest = locator[colon_index + 1:]

    # Bước 2: Xử lý riêng cho role
    if method == "role":
        return handle_role_locator(rest)
    
    if method == "id":
        if not rest.startswith("#"):
            rest = f"#{rest}"
        return {"method" :"id", "args":[rest]}


    # Bước 3: Các trường hợp khác
    return {"method": method, "args": [rest]}


# --- Ví dụ sử dụng ---
# print(extract_locator_to_element("placeholder:Username"))
# → {'method': 'placeholder', 'args': ['Username']}
#
# print(extract_locator_to_element("role:button|name=Login"))
# → {'method': 'role', 'args': ['button', {'name': 'Login'}]}
#
# print(extract_locator_to_element("role:button|name='Login'"))
# → {'method': 'role', 'args': ['button', {'name': 'Login'}]}
#
# print(extract_locator_to_element("role:input|disabled=true"))
# → {'method': 'role', 'args': ['input', {'disabled': True}]}
#
# print(extract_locator_to_element("role:button|tabIndex=5"))
# → {'method': 'role', 'args': ['button', {'tabIndex': 5}]}



def read_config_file(file):
    """
    Read config file, supporting config files:
    - yaml
    - json
    :param file: (str) file path
    :return: python-format of the file content
    """
    with open(file, 'r') as f:
        try:
            return yaml.load(f, Loader=yaml.UnsafeLoader)
        except ScannerError:
            try:
                return json.load(f)
            except JSONDecodeError:
                raise Exception('The config file type is not supported or the config syntax got errors.')
            
def soft_format(text, format_func):
    try:
        return format_func(text)
    except (ValueError, TypeError):
        return text

# def group_tabular_data(header: list | tuple, contents: list| tuple, row=None):
#     """
#     Group a tabular data
#     :param header: (list/tuple)
#     :param contents: (list/tuple)
#     :param row:
#     :return:
#     """
#     if not contents:
#         return {} if row else []
#     logger.info(f'Header keys length: {len(header)}')
#     logger.info(f'Contents length: {len(contents)}')
#     if len(contents) % len(header) != 0:
#         logger.info('Unable to parse data.')
#         return {}
#         # raise Exception('Unable to parse data.')
#     data_partition = [contents[i:i + len(header)] for i in range(0, len(contents), len(header))]
#     if row is None:
#         return [{field: line_data[i] for i, field in enumerate(header)} for line_data in data_partition]
#     if row <= len(data_partition):
#         return {field: data_partition[row - 1][i] for i, field in enumerate(header)}
#     logger.warning(f'Total rows: {len(data_partition)}, no data at row #{row}')

def group_tabular_data(header: list | tuple, contents: list | tuple, row=None):
    """
    Group a tabular data
    :param header: (list/tuple)
    :param contents: (list/tuple)
    :param row: (1-based index)
    :return:
    """
    if not contents:
        logger.info("No contents available")
        return {} if row else []

    logger.info(f"[DEBUG] Header keys ({len(header)}): {header}")
    logger.info(f"[DEBUG] Contents length={len(contents)} | values={contents}")

    if len(contents) % len(header) != 0:
        logger.info(f"[DEBUG] Contents ({len(contents)}) is not divisible by header length ({len(header)}).")
        return {}
        # raise Exception('Unable to parse data.')

    data_partition = [
        contents[i:i + len(header)] for i in range(0, len(contents), len(header))
    ]
    logger.info(f"[DEBUG] Partitioned data into {len(data_partition)} rows")
    for idx, row_data in enumerate(data_partition, start=1):
        logger.info(f"[DEBUG] Row {idx}: {row_data}")

    # Nếu không truyền row → return toàn bộ rows
    if row is None:
        logger.info("[DEBUG] Returning all rows as list of dicts")
        return [{field: line_data[i] for i, field in enumerate(header)} for line_data in data_partition]

    # Nếu có row
    logger.info(f"[DEBUG] Requested row={row} (1-based)")
    if row <= len(data_partition):
        result = {field: data_partition[row - 1][i] for i, field in enumerate(header)}
        logger.info(f"[DEBUG] Returning row {row}: {result}")
        return result

    logger.warning(f"[DEBUG] Total rows={len(data_partition)}, no data at row #{row}")
    return {}


def parse_fields_to_dict(fields: list[str]) -> dict:
    """
    """
    result = {}
    for line in fields:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized_key = key.strip().lower().replace(" ", "_").replace(":", "")
        result[normalized_key] = value.strip()
    return result


def find_import_file(make_name: str, function_name: str, test_case: str = "", folder: str = "test_data") -> Path:
    """
    Tìm file .zip trong test_data theo dạng tên ghép: {make_name}_{function_name}_{test_case}.zip 
    (không phân biệt hoa/thường, bỏ ký tự đặc biệt).
    - Ưu tiên khớp "exact" theo stem (tên file không tính .zip).
    - Fallback: stem chứa cả make, function và test_case.
    - Quét đệ quy mọi thư mục con của test_data.
    Trả về: Path file mới nhất nếu có nhiều kết quả.
    """
    proj_root = Path(__file__).resolve().parents[1]
    data_dir = proj_root / folder
    if not data_dir.exists():
        raise FileNotFoundError(f"Test data folder not found: {data_dir}")

    def norm(s: str) -> str:
        return re.sub(r"\W+", "", (s or "")).lower()

    mk = norm(make_name)
    fn = norm(function_name)
    tc = norm(test_case)
    expected_stem = norm(f"{make_name}_{function_name}" + (f"_{test_case}" if test_case else ""))

    exact: list[Path] = []
    loose: list[Path] = []
    scanned: list[str] = []

    for p in data_dir.rglob("*.zip"):
        stem_norm = norm(p.stem)
        scanned.append(str(p))
        # exact match tất cả
        if stem_norm == expected_stem:
            exact.append(p)
        # loose match: ít nhất make + function, test_case nếu có thì cũng match
        elif mk in stem_norm and fn in stem_norm and (not tc or tc in stem_norm):
            loose.append(p)

    def pick(cands: list[Path]) -> Path | None:
        if not cands:
            return None
        cands.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return cands[0]

    chosen = pick(exact) or pick(loose)
    if not chosen:
        raise FileNotFoundError(
            f"No .zip matched file '{make_name}_{function_name}_{test_case}.zip' in {data_dir}\n"
            f"Scanned zips:\n- " + "\n- ".join(scanned)
        )

    logger.info(f"[import_excel] chosen file: {chosen}")
    return chosen


# def find_import_file(make_name: str, function_name: str, test_case: str , folder: str = "test_data") -> Path:
#     """
#     Tìm file .zip trong test_data theo dạng tên ghép: {make_name}_{function_name}.zip (không phân biệt hoa/thường, bỏ ký tự đặc biệt).
#     - Ưu tiên khớp "exact" theo stem (tên file không tính .zip).
#     - Fallback: stem chứa cả make và function.
#     - Quét đệ quy mọi thư mục con của test_data.
#     Trả về: Path file mới nhất nếu có nhiều kết quả.
#     """
#     proj_root = Path(__file__).resolve().parents[1]  # d:\webimporter
#     data_dir = proj_root / folder
#     if not data_dir.exists():
#         raise FileNotFoundError(f"Test data folder not found: {data_dir}")

#     def norm(s: str) -> str:
#         return re.sub(r"\W+", "", (s or "")).lower()

#     mk = norm(make_name)
#     fn = norm(function_name)
#     expected_stem = norm(f"{make_name}_{function_name}")  # ví dụ: mitsubishi_networkscan -> mitsubishinetworkscan

#     exact: list[Path] = []
#     loose: list[Path] = []
#     scanned: list[str] = []

#     for p in data_dir.rglob("*.zip"):
#         stem_norm = norm(p.stem)            # tên file không tính .zip
#         scanned.append(str(p))
#         if stem_norm == expected_stem:
#             exact.append(p)
#         elif mk in stem_norm and fn in stem_norm:
#             loose.append(p)

#     def pick(cands: list[Path]) -> Path | None:
#         if not cands:
#             return None
#         cands.sort(key=lambda x: x.stat().st_mtime, reverse=True)
#         return cands[0]

#     chosen = pick(exact) or pick(loose)
#     if not chosen:
#         raise FileNotFoundError(
#             f"No .zip matched file '{make_name}_{function_name}.zip' in {data_dir}\n"
#             f"Scanned zips:\n- " + "\n- ".join(scanned)
#         )

#     logger.info(f"[import_excel] chosen file: {chosen}")
#     return chosen

def download_file(url: str, file_name: str | Path, out_dir: str | Path = "downloads"):
    """
    Tải file (dùng cho URL .zip). Yêu cầu requests.
    """
    proj_root = Path(__file__).resolve().parents[1]  # d:\webimporter
    down_dir = proj_root / out_dir
    down_dir.mkdir(parents=True, exist_ok=True)
    file_path = down_dir / Path(file_name).name
    logger.info(f"[download] GET {url}")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info(f"[download] saved -> {file_path.resolve()}")
    return file_path