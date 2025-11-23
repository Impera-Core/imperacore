import logging
import sys
import os

# ANSI Reset
RESET = "\033[0m"

# Neonfarben
NEON_COLORS = {
    "DEBUG": "\033[38;2;21;255;255m",
    "INFO": "\033[38;2;57;255;20m",
    "WARNING": "\033[38;2;255;140;0m",
    "ERROR": "\033[38;2;255;50;40m",
    "CRITICAL": "\033[38;2;255;0;0m",
    "SUCCESS": "\033[38;2;0;255;100m",
    "CREATE": "\033[38;2;0;200;255m",
    "INSTALL": "\033[38;2;180;0;255m",
    "ADDED": "\033[38;2;0;255;255m",
    "COPY": "\033[38;2;255;255;0m",
    "REMOVE": "\033[38;2;255;0;50m",
    "PATCH": "\033[38;2;255;140;0m",
    "LOADING": "\033[38;2;255;0;255m",
    "BUILD": "\033[38;2;0;255;200m",
    "FLASH": "\033[38;2;200;255;0m",
    "TEST": "\033[38;2;80;0;255m",
    "RUNNING": "\033[38;2;0;255;200m"
}

ICONS = {
    "DEBUG": "🐞",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "💀",
    "SUCCESS": "✔️",
    "CREATE": "🛠️",
    "INSTALL": "📥",
    "ADDED": "➕",
    "COPY": "📄",
    "REMOVE": "🗑️",
    "PATCH": "🩹",
    "LOADING": "⏳",
    "BUILD": "🏗️",
    "FLASH": "⚡",
    "TEST": "🧪",
    "RUNNING": "⏱️"
}

# Formatter
class IconFormatter(logging.Formatter):
    def format(self, record):
        level = record.levelname
        icon = ICONS.get(level, "ℹ️")
        color = NEON_COLORS.get(level, NEON_COLORS["INFO"])
        return f"{color}{icon} [{level.lower()}]{RESET} | {record.getMessage()}"

# Logger Setup
logger = logging.getLogger("nexuzcore")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(IconFormatter())

file_handler = logging.FileHandler(os.path.join(os.getcwd(), "nexuzcore-build.log"), encoding='utf-8')
file_handler.setFormatter(logging.Formatter("[%(levelname)s] | %(message)s"))

logger.handlers = [console_handler, file_handler]
logger.propagate = False

# Eigene Levels
SUCCESS_LEVEL = 25
CREATE_LEVEL = 26
RUNNING_LEVEL = 27

logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.addLevelName(CREATE_LEVEL, "CREATE")
logging.addLevelName(RUNNING_LEVEL, "RUNNING")

# Helper Funktionen
def debug(msg, *args, **kwargs): logger.debug(msg, *args, **kwargs)
def info(msg, *args, **kwargs): logger.info(msg, *args, **kwargs)
def warning(msg, *args, **kwargs): logger.warning(msg, *args, **kwargs)
def error(msg, *args, **kwargs): logger.error(msg, *args, **kwargs)
def critical(msg, *args, **kwargs): logger.critical(msg, *args, **kwargs)
def success(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, msg, *args, **kwargs)
def create(msg, *args, **kwargs): logger.log(CREATE_LEVEL, f"🛠️ {msg}", *args, **kwargs)
def running(msg, *args, **kwargs): logger.log(RUNNING_LEVEL, f"⏱️ {msg}", *args, **kwargs)
def install(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"📥 {msg}", *args, **kwargs)
def added(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"➕ {msg}", *args, **kwargs)
def copy(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"📄 {msg}", *args, **kwargs)
def remove(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"🗑️ {msg}", *args, **kwargs)
def patch(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"🩹 {msg}", *args, **kwargs)
def loading(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"⏳ {msg}", *args, **kwargs)
def build(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"🏗️ {msg}", *args, **kwargs)
def flash(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"⚡ {msg}", *args, **kwargs)
def test(msg, *args, **kwargs): logger.log(SUCCESS_LEVEL, f"🧪 {msg}", *args, **kwargs)

# Direkter Zugriff
log = logger
