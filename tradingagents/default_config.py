import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "data")),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": os.getenv("TRADING_LLM_PROVIDER", "openai"),
    "deep_think_llm": os.getenv("TRADING_DEEP_LLM", "gpt-5-nano"),
    "quick_think_llm": os.getenv("TRADING_QUICK_LLM", "gpt-5-nano"),
    "backend_url": os.getenv("TRADING_BACKEND_URL", "https://api.openai.com/v1"),
    # Ollama settings
    "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2"),
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": False,
}
