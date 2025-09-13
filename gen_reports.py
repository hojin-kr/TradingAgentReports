import argparse
import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from tradingagents.default_config import DEFAULT_CONFIG


def _normalize_decision_token(token: str) -> Optional[str]:
    """Map various decision words/phrases (EN/KR and common analyst terms) to BUY/SELL/HOLD."""
    if not token:
        return None
    t = token.strip().upper()
    mapping = {
        # BUY
        "BUY": "BUY",
        "STRONG BUY": "BUY",
        "OUTPERFORM": "BUY",
        "OVERWEIGHT": "BUY",
        "ACCUMULATE": "BUY",
        "LONG": "BUY",
        "매수": "BUY",
        # SELL
        "SELL": "SELL",
        "STRONG SELL": "SELL",
        "UNDERPERFORM": "SELL",
        "UNDERWEIGHT": "SELL",
        "REDUCE": "SELL",
        "SHORT": "SELL",
        "매도": "SELL",
        # HOLD
        "HOLD": "HOLD",
        "NEUTRAL": "HOLD",
        "EQUAL WEIGHT": "HOLD",
        "MARKET PERFORM": "HOLD",
        "보유": "HOLD",
        "중립": "HOLD",
    }
    return mapping.get(t)


def _extract_explicit_decision_line(lines: List[str]) -> Optional[str]:
    """Return the explicit 'Decision: ...' line if present near the top."""
    decision_regex = re.compile(r"^\s*decision\s*:\s*(.+)$", re.IGNORECASE)
    for ln in lines[:10]:
        m = decision_regex.match(ln)
        if m:
            return ln.strip()
    return None


def _classify_from_text_window(text: str) -> Optional[str]:
    """Classify using bounded window with robust word boundaries and synonym mapping.

    Avoid false positives (e.g., BUYBACK). Exclude negations like 'not a buy'.
    """
    if not text:
        return None
    window = text[:600]
    # Candidate tokens with synonyms; order gives priority when multiple found
    candidates = [
        (r"\bstrong\s+sell\b", "SELL"),
        (r"\bstrong\s+buy\b", "BUY"),
        (r"\bund(er)?perform\b", "SELL"),
        (r"\bunderweight\b", "SELL"),
        (r"\breduce\b", "SELL"),
        (r"\boverweight\b", "BUY"),
        (r"\boutperform\b", "BUY"),
        (r"\bequal\s+weight\b", "HOLD"),
        (r"\bmarket\s+perform\b", "HOLD"),
        (r"\bneutral\b", "HOLD"),
        (r"\bbuy\b", "BUY"),
        (r"\bsell\b", "SELL"),
        (r"\bhold\b", "HOLD"),
        (r"매수", "BUY"),
        (r"매도", "SELL"),
        (r"보유", "HOLD"),
        (r"중립", "HOLD"),
    ]

    negations = re.compile(r"(?i)\b(not|no|avoid|never)\b.*\b(buy|sell|매수|매도)\b")
    if negations.search(window):
        # If there is a clear negation, bias to HOLD unless an explicit line exists elsewhere
        return "HOLD"

    lower_window = window.lower()
    earliest_idx = None
    chosen = None
    for pattern, label in candidates:
        m = re.search(pattern, lower_window)
        if not m:
            continue
        idx = m.start()
        if earliest_idx is None or idx < earliest_idx:
            earliest_idx = idx
            chosen = label
    return chosen


def decision_info_from_text_beginning(raw_text: str) -> Tuple[str, str, float]:
    """Extract decision with source and confidence.

    Returns (decision, source, confidence 0-1).
    Source is one of: explicit_line, head_window, tail_legacy, default.
    """
    if not raw_text:
        return ("HOLD", "default", 0.3)
    try:
        lines = [ln.strip() for ln in raw_text.strip().splitlines() if ln.strip()]
        if not lines:
            return ("HOLD", "default", 0.3)

        # 1) Explicit Decision: line
        explicit = _extract_explicit_decision_line(lines)
        if explicit:
            upper = explicit.upper()
            # Capture the right-hand side and normalize
            m = re.match(r"^\s*DECISION\s*:\s*(.+)$", explicit, re.IGNORECASE)
            if m:
                rhs = m.group(1).strip()
                # Try direct normalization first, otherwise scan rhs tokens
                normalized = _normalize_decision_token(rhs)
                if not normalized:
                    normalized = _classify_from_text_window(rhs) or "HOLD"
                return (normalized, "explicit_line", 0.95)

        # 2) Head window scan (first lines and first N chars)
        head_blob = ("\n".join(lines[:8]) + "\n" + raw_text[:600])
        classified = _classify_from_text_window(head_blob)
        if classified:
            return (classified, "head_window", 0.8)

        # 3) Legacy tail scan
        last = lines[-1].rstrip(" .!?)]")
        tail_blob = (last + "\n" + raw_text[-300:])
        classified_tail = _classify_from_text_window(tail_blob)
        if classified_tail:
            return (classified_tail, "tail_legacy", 0.55)
    except Exception:
        pass
    return ("HOLD", "default", 0.3)


def decision_from_text_beginning(raw_text: str) -> str:
    """Backward-compatible wrapper returning only the decision label."""
    return decision_info_from_text_beginning(raw_text)[0]


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


def _atomic_write(file_path: Path, text: str) -> None:
    """Write text atomically to avoid partial files on crash."""
    tmp_fd, tmp_path = tempfile.mkstemp(dir=str(file_path.parent), suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(text if text else "")
        os.replace(tmp_path, file_path)
    except Exception:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        finally:
            raise


def write_markdown_file(target_dir: Path, filename: str, title: str, content: str) -> Path:
    ensure_dir(target_dir)
    file_path = target_dir / filename
    _atomic_write(file_path, content or "")
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


def _extract_existing_decision_line(text: str) -> Optional[str]:
    """Search the first few lines for an existing 'Decision:' line and return it if found."""
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines()]
    for ln in lines[:10]:
        up = ln.upper()
        if up.startswith("DECISION:"):
            return ln.strip()
    return None


def _build_short_summary(text: str, max_len: int = 140) -> str:
    """Heuristically build a <=140-char summary from the start of the text.

    Preference order:
    - First non-empty line that is not a 'Decision:' line
    - Otherwise the first sentence from the text
    - Fallback to the first max_len characters
    """
    if not text:
        return ""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    for ln in lines[:10]:
        if not ln.lower().startswith("decision:"):
            summary = ln
            if len(summary) <= max_len:
                return summary
            # Try to cut at a sentence boundary within limit
            cut = summary[:max_len]
            dot = cut.rfind(".")
            if dot >= 40:  # avoid ultra-short chop
                return cut[:dot+1].strip()
            return cut.strip()

    # Fallback to first sentence from full text
    text_clean = " ".join(text.strip().split())
    for sep in [". ", "! ", "? "]:
        idx = text_clean.find(sep)
        if idx != -1 and idx + 1 <= max_len:
            return text_clean[: idx + 1]
    return text_clean[:max_len].strip()


def postprocess_final_trade_decision(text: str) -> str:
    """Ensure final_trade_decision starts with a top 'Decision:' line only.

    - Do not add any summary line.
    - Prepend a 'Decision: ...' line. If one exists, reuse it; otherwise build from extracted BUY/SELL/HOLD.
    - Avoid duplicating existing leading 'Decision:' lines.
    """
    if not text:
        return text

    # Decide label
    decision = decision_from_text_beginning(text)
    existing_decision = _extract_existing_decision_line(text)
    decision_line = existing_decision or f"Decision: {decision}"

    # Remove leading decision lines to avoid duplication near the top
    lines = text.splitlines()
    while lines and lines[0].strip().lower().startswith("decision:"):
        lines.pop(0)
    new_body = "\n".join(lines).lstrip("\n")

    return f"{decision_line}\n\n{new_body}".strip()


def save_reports(
    final_state: Dict,
    ticker: str,
    trade_date: str,
    locales: List[str],
    reports_root: Path,
    translator: Optional[object],
    translate: bool,
) -> List[Path]:
    """Persist reports, routing all files by final_trade_decision (BUY/HOLD/SELL)."""
    saved_files: List[Path] = []

    for raw_locale in locales:
        locale = raw_locale.strip().upper()

        # Individual report files (route all files by final_trade_decision)
        reports_map = {
            "market_report.md": ("Market Report", final_state.get("market_report", "")),
            "sentiment_report.md": ("Sentiment Report", final_state.get("sentiment_report", "")),
            "news_report.md": ("News Report", final_state.get("news_report", "")),
            "fundamentals_report.md": ("Fundamentals Report", final_state.get("fundamentals_report", "")),
            "investment_plan.md": ("Investment Plan", final_state.get("investment_plan", "")),
            "trader_investment_plan.md": ("Trader Investment Plan", get_trader_plan(final_state)),
            "final_trade_decision.md": ("Final Trade Decision", final_state.get("final_trade_decision", "")),
        }

        # Resolve decision once per locale from the original final decision text
        final_decision_text = final_state.get("final_trade_decision", "")
        decision_label, decision_source, decision_conf = decision_info_from_text_beginning(final_decision_text)
        decision_dir = decision_label
        base_dir = reports_root / trade_date / decision_dir / ticker.upper() / locale
        ensure_dir(base_dir)

        # Persist decision metadata for auditability
        meta = {
            "ticker": ticker.upper(),
            "date": trade_date,
            "locale": locale,
            "decision": decision_label,
            "source": decision_source,
            "confidence": round(decision_conf, 2),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
        meta_path = base_dir / "_decision.json"
        _atomic_write(meta_path, json.dumps(meta, ensure_ascii=False, indent=2))

        for filename, (title, content) in reports_map.items():
            localized_content = maybe_translate(content, locale, translator, translate)
            # Apply post-processing only to final_trade_decision.md
            if filename == "final_trade_decision.md":
                text_for_routing = localized_content or content
                final_text = postprocess_final_trade_decision(text_for_routing)
            else:
                final_text = localized_content

            saved_files.append(
                write_markdown_file(base_dir, filename, title, final_text)
            )

        # Skip creating combined complete.md; save only the raw agent outputs above

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

    # Derive decision prioritizing the beginning of the final decision text
    decision_label = decision_from_text_beginning(final_state.get("final_trade_decision", ""))

    # Reports root under repository
    reports_root = get_project_root() / "reports"
    ensure_dir(reports_root)

    saved_files = save_reports(
        final_state=final_state,
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
