import logging
from pathlib import Path

MAP_LEVELS = {
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}

def setup_global_logging(log_file: str | Path, level: str = 'INFO', is_date: bool = True, to_console: bool = False):
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(MAP_LEVELS[level.upper()])

    # Clear old handlers (tránh log trùng)
    for h in list(root.handlers):
        root.removeHandler(h)

    fmt = '%(asctime)s %(name)-16s %(levelname)-8s %(message)s' if is_date else '%(name)-16s %(levelname)-8s %(message)s'
    formatter = logging.Formatter(fmt=fmt)

    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setLevel(MAP_LEVELS[level.upper()])
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    if to_console:
        console = logging.StreamHandler()
        console.setLevel(MAP_LEVELS[level.upper()])
        console.setFormatter(formatter)
        root.addHandler(console)

class Logger:
    def __init__(self, prefix: str = "webimporter", log_level: str = 'INFO'):
        self._logger = logging.getLogger(prefix)
        self._logger.setLevel(MAP_LEVELS[log_level.upper()])
        # Không gắn handler ở đây -> dùng chung handlers của root

    def error(self, msg): self._logger.error(msg)
    def warning(self, msg): self._logger.warning(msg)
    def info(self, msg): self._logger.info(msg)
    def debug(self, msg): self._logger.debug(msg)