import os
from typing import Dict, Optional

from cointradingagents import default_config

_CONFIG: Optional[Dict] = None


def _ensure_config():
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = default_config.DEFAULT_CONFIG.copy()
        # Ensure directories exist
        os.makedirs(_CONFIG["coin_reports_dir"], exist_ok=True)
        os.makedirs(_CONFIG["coin_eval_results_dir"], exist_ok=True)


def set_config(config: Dict):
    """Override default configuration with runtime values."""
    _ensure_config()
    _CONFIG.update(config)


def get_config() -> Dict:
    _ensure_config()
    return _CONFIG.copy()

