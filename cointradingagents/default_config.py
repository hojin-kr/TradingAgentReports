import os

_PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DEFAULT_CONFIG = {
    "project_dir": _PROJECT_DIR,
    "coin_reports_dir": os.getenv("COINTRADINGAGENTS_REPORTS_DIR", "./coin_reports"),
    "coin_eval_results_dir": os.getenv(
        "COINTRADINGAGENTS_EVAL_DIR", "./coin_eval_results"
    ),
    "data_cache_dir": os.getenv(
        "COINTRADINGAGENTS_CACHE_DIR", os.path.join(_PROJECT_DIR, "data_cache")
    ),
    "binance_base_url": os.getenv("BINANCE_API_URL", "https://api.binance.com"),
    # LLM settings
    "llm_provider": os.getenv("COIN_LLM_PROVIDER", "openai"),
    "deep_think_llm": os.getenv("COIN_DEEP_LLM", "gpt-5-nano"),
    "quick_think_llm": os.getenv("COIN_QUICK_LLM", "gpt-5-nano"),
    "backend_url": os.getenv("COIN_BACKEND_URL", "https://api.openai.com/v1"),
    # Ollama settings
    "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "ollama_model": os.getenv("OLLAMA_MODEL", "gemma3:4b"),
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
}
