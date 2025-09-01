import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from tradingagents.default_config import DEFAULT_CONFIG


def decision_from_text_end(raw_text: str) -> str:
    """Extract BUY/SELL/HOLD by scanning the last non-empty line of text.

    Rules:
    - Look at the last non-empty line; try to match a trailing BUY/SELL/HOLD.
    - If not found, scan the last 200 characters as a fallback.
    - Default to HOLD if nothing decisive is found.
    """
    if not raw_text:
        return "HOLD"
    try:
        lines = [ln.strip() for ln in raw_text.strip().splitlines() if ln.strip()]
        if not lines:
            return "HOLD"
        last = lines[-1].upper().rstrip(" .!?)]")
        for token in ("BUY", "SELL", "HOLD"):
            if last.endswith(token) or last == token:
                return token
        tail = raw_text[-200:].upper()
        for token in ("BUY", "SELL", "HOLD"):
            if token in tail:
                return token
    except Exception:
        pass
    return "HOLD"


def get_project_root() -> Path:
    """Return repository root based on this file location."""
    return Path(__file__).resolve().parent


def load_state_from_log(ticker: str, trade_date: str) -> Dict:
    """Load a saved state from eval_results file if available."""
    log_path = (
        get_project_root()
        / "eval_results"
        / ticker
        / "TradingAgentsStrategy_logs"
        / f"full_states_log_{trade_date}.json"
    )
    if not log_path.exists():
        raise FileNotFoundError(f"No saved log found at: {log_path}")
    with open(log_path, "r") as f:
        data = json.load(f)
    if trade_date not in data:
        # pick the last available entry as fallback
        latest_key = sorted(data.keys())[-1]
        return data[latest_key]
    return data[trade_date]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def get_trader_plan(final_state: Dict) -> str:
    """Return trader plan text with fallback for log key naming."""
    return final_state.get("trader_investment_plan") or final_state.get("trader_investment_decision") or ""


def write_markdown_file(target_dir: Path, filename: str, title: str, content: str) -> Path:
    ensure_dir(target_dir)
    file_path = target_dir / filename
    with open(file_path, "w") as f:
        f.write(f"# {title}\n\n")
        f.write(content if content else "")
        f.write("\n")
    return file_path


def build_complete_markdown(final_state: Dict) -> str:
    """Combine all reports into a single markdown content."""
    sections: List[Tuple[str, str]] = [
        ("Final Trade Decision", final_state.get("final_trade_decision", "")),
        ("Trader Investment Plan", get_trader_plan(final_state)),
        ("Investment Plan", final_state.get("investment_plan", "")),
        ("Market Report", final_state.get("market_report", "")),
        ("Sentiment Report", final_state.get("sentiment_report", "")),
        ("News Report", final_state.get("news_report", "")),
        ("Fundamentals Report", final_state.get("fundamentals_report", "")),
    ]
    buf: List[str] = []
    for heading, body in sections:
        if not body:
            continue
        buf.append(f"## {heading}\n\n{body}\n")
    return "\n".join(buf).strip()


def maybe_translate(text: str, locale: str, translator: Optional[object], enable_translation: bool) -> str:
    """Translate text to target locale using provided translator (must have .invoke)."""
    if not text or not enable_translation or translator is None:
        return text
    if locale.upper() in ["EN", "EN-US", "EN-GB"]:
        return text

    prompt = (
        "You are a precise translator. Translate the following financial analysis into "
        f"{locale.upper()} while preserving technical terminology and formatting. "
        "Do not add explanations."
    )
    messages = [("system", prompt), ("human", text)]
    try:
        return translator.invoke(messages).content
    except Exception:
        return text


def save_reports(
    final_state: Dict,
    decision_label: str,
    ticker: str,
    trade_date: str,
    locales: List[str],
    reports_root: Path,
    translator: Optional[object],
    translate: bool,
) -> List[Path]:
    """Persist reports in the required directory structure per locale."""
    saved_files: List[Path] = []

    # Normalize decision directory
    decision_dir = decision_from_text_end(decision_label)

    for raw_locale in locales:
        locale = raw_locale.strip().upper()
        base_dir = reports_root / trade_date / decision_dir / ticker.upper() / locale
        ensure_dir(base_dir)

        # Individual report files
        reports_map = {
            "market_report.md": ("Market Report", final_state.get("market_report", "")),
            "sentiment_report.md": ("Sentiment Report", final_state.get("sentiment_report", "")),
            "news_report.md": ("News Report", final_state.get("news_report", "")),
            "fundamentals_report.md": ("Fundamentals Report", final_state.get("fundamentals_report", "")),
            "investment_plan.md": ("Investment Plan", final_state.get("investment_plan", "")),
            "trader_investment_plan.md": ("Trader Investment Plan", get_trader_plan(final_state)),
            "final_trade_decision.md": ("Final Trade Decision", final_state.get("final_trade_decision", "")),
        }

        for filename, (title, content) in reports_map.items():
            localized_content = maybe_translate(content, locale, translator, translate)
            saved_files.append(
                write_markdown_file(base_dir, filename, title, localized_content)
            )

        # Complete combined report
        combined = build_complete_markdown(final_state)
        combined_localized = maybe_translate(combined, locale, translator, translate)
        saved_files.append(
            write_markdown_file(base_dir, "complete.md", f"{ticker.upper()} Report ({trade_date})", combined_localized)
        )

    return saved_files


def main():
    parser = argparse.ArgumentParser(description="Generate Markdown reports from TradingAgents outputs.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g., NVDA")
    parser.add_argument("--date", required=True, help="Analysis date in YYYY-MM-DD")
    parser.add_argument(
        "--locales",
        default="EN",
        help="Comma-separated locales to output, e.g., EN,KO",
    )
    parser.add_argument(
        "--from-log",
        action="store_true",
        help="Load from eval_results state log instead of re-running the graph",
    )
    parser.add_argument(
        "--translate",
        action="store_true",
        help="Translate non-EN locales using the configured LLM",
    )
    args = parser.parse_args()

    ticker = args.ticker.strip().upper()
    trade_date = args.date.strip()
    locales = [l.strip() for l in args.locales.split(",") if l.strip()]

    # Determine if we need translation or to run the graph
    need_translation = args.translate and any(l.upper() not in ["EN", "EN-US", "EN-GB"] for l in locales)
    run_graph = not args.from_log

    translator = None
    final_state: Dict

    if args.from_log:
        final_state = load_state_from_log(ticker, trade_date)
    else:
        # Lazy import to avoid heavy dependencies when not needed
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        config = DEFAULT_CONFIG.copy()
        graph = TradingAgentsGraph(debug=False, config=config)
        final_state, _ = graph.propagate(ticker, trade_date)
        if need_translation:
            translator = graph.quick_thinking_llm

    if args.from_log and need_translation:
        # We only need a translator, not the full run
        try:
            from tradingagents.graph.trading_graph import TradingAgentsGraph
            config = DEFAULT_CONFIG.copy()
            graph = TradingAgentsGraph(debug=False, config=config)
            translator = graph.quick_thinking_llm
        except Exception:
            translator = None

    # Derive decision from the end of the final decision text
    decision_label = decision_from_text_end(final_state.get("final_trade_decision", ""))

    # Reports root under repository
    reports_root = get_project_root() / "reports"
    ensure_dir(reports_root)

    saved_files = save_reports(
        final_state=final_state,
        decision_label=decision_label,
        ticker=ticker,
        trade_date=trade_date,
        locales=locales,
        reports_root=reports_root,
        translator=translator,
        translate=args.translate,
    )

    # Print saved paths for quick reference
    for p in saved_files:
        print(str(p))


if __name__ == "__main__":
    main()
