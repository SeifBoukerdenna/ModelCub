"""Logging configuration for ModelCub."""
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import yaml


def setup_logging(config_path: Optional[Path] = None, force_level: Optional[str] = None):
    """
    Setup logging from config file.

    Priority:
    1. force_level (environment variable)
    2. Per-project config (if config_path provided)
    3. Global config (~/.modelcub/config.yaml)
    4. Default (INFO level, console only)
    """
    config = None

    # Try per-project config
    if config_path and config_path.exists():
        try:
            config = yaml.safe_load(config_path.read_text())
        except Exception:
            pass

    # Try global config
    if not config:
        global_config = Path.home() / ".modelcub" / "config.yaml"
        if global_config.exists():
            try:
                config = yaml.safe_load(global_config.read_text())
            except Exception:
                pass

    # Extract logging config
    log_config = config.get("logging", {}) if config else {}

    # Level
    level_str = force_level or log_config.get("level", "INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)

    # Format
    format_str = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(format_str)

    # Root logger
    root_logger = logging.getLogger("modelcub")
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    handlers_config = log_config.get("handlers", {})

    # Console handler
    if isinstance(handlers_config, dict):
        console_config = handlers_config.get("console", {"enabled": True})
        if console_config.get("enabled", True):
            console_handler = logging.StreamHandler()
            console_level = console_config.get("level", "INFO")
            console_handler.setLevel(getattr(logging, console_level.upper(), logging.INFO))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

    # File handler
    if isinstance(handlers_config, dict):
        file_config = handlers_config.get("file", {})
        if file_config.get("enabled", False):
            log_path = Path(file_config.get("path", "~/.modelcub/logs/modelcub.log")).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=file_config.get("max_bytes", 10485760),
                backupCount=file_config.get("backup_count", 5)
            )
            file_level = file_config.get("level", "DEBUG")
            file_handler.setLevel(getattr(logging, file_level.upper(), logging.DEBUG))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

    # Only log setup message if not default
    if config or force_level:
        root_logger.info(f"Logging configured: level={level_str}")


# Auto-setup on import
try:
    from .paths import project_root
    config_path = project_root() / ".modelcub" / "config.yaml"
    setup_logging(config_path)
except Exception:
    setup_logging()