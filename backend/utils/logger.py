import logging
import sys
from utils.config import load_config


def setup_logger(name: str = "agent_app") -> logging.Logger:
    """配置并返回 logger 实例。"""
    cfg = load_config()
    log_cfg = cfg.get("logging", {})

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_cfg.get("level", "INFO"), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        fmt = log_cfg.get("format", "%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)

    return logger
