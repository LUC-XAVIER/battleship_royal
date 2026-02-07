import sys
import os
from datetime import datetime
from enum import IntEnum
from colorama import Fore, Style

COLOR_ENABLED = True

class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40


class Logger:
    def __init__(self, level: LogLevel = LogLevel.DEBUG, stream=sys.stdout):
        self.level = level
        self.stream = stream

    # ---------- formatting helpers ----------

    def _ts(self) -> str:
        ts = datetime.now().strftime("%H:%M:%S")
        return f"{Style.DIM}{ts}{Style.RESET_ALL}" if COLOR_ENABLED else ts

    def _level(self, level: LogLevel) -> str:
        if not COLOR_ENABLED:
            return level.name

        return {
            LogLevel.DEBUG: Fore.CYAN + "DEBUG",
            LogLevel.INFO: Fore.LIGHTGREEN_EX + "INFO",
            LogLevel.WARN: Fore.YELLOW + "WARN",
            LogLevel.ERROR: Fore.LIGHTRED_EX + "ERROR",
        }[level] + Style.RESET_ALL

    def _caller(self) -> str:
        frame = sys._getframe(3)

        file = os.path.basename(frame.f_code.co_filename)
        line = frame.f_lineno
        func = frame.f_code.co_name

        self_obj = frame.f_locals.get("self")
        cls = self_obj.__class__.__name__ if self_obj else None

        if not COLOR_ENABLED:
            return f"{file}:{line} {cls + '.' if cls else ''}{func}"

        file_c = Fore.BLUE + file + Style.RESET_ALL
        line_c = Style.DIM + str(line) + Style.RESET_ALL
        func_c = Fore.CYAN + func + Style.RESET_ALL
        cls_c = Fore.MAGENTA + cls + Style.RESET_ALL if cls else ""

        if cls:
            return f"{file_c}:{line_c} {cls_c}.{func_c}"
        return f"{file_c}:{line_c} {func_c}"

    # ---------- core logger ----------

    def _log(self, level: LogLevel, *values: object, sep=' ', end='\n'):
        if level < self.level:
            return

        prefix = f"[{self._ts()} {self._level(level)} {self._caller()}]"
        print(prefix, *values, sep=sep, end=end, file=self.stream, flush=True)

    # ---------- public API ----------

    def debug(self, *values: object, **kwargs):
        self._log(LogLevel.DEBUG, *values, **kwargs)

    def info(self, *values: object, **kwargs):
        self._log(LogLevel.INFO, *values, **kwargs)

    def warn(self, *values: object, **kwargs):
        self._log(LogLevel.WARN, *values, **kwargs)

    def error(self, *values: object, **kwargs):
        self._log(LogLevel.ERROR, *values, **kwargs)

if __name__ == "__main__":
    log = Logger(LogLevel.DEBUG)
    log.debug("debug message")
    log.info("info message")
    log.warn("warn message")
    log.error("error message")