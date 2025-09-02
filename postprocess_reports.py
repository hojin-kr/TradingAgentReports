import argparse
from pathlib import Path
from typing import List

from tradingagents.default_config import DEFAULT_CONFIG


def get_project_root() -> Path:
    return Path(__file__).resolve().parent


def discover_markdown_files_for_date(reports_root: Path, trade_date: str) -> List[Path]:
    base = reports_root / trade_date
    if not base.exists():
        return []
    return list(base.glob("**/*.md"))


def create_llm():
    # Always use OpenAI per requirement; fall back to DEFAULT_CONFIG models
    from langchain_openai import ChatOpenAI

    model = DEFAULT_CONFIG.get("quick_think_llm", "gpt-4o-mini")
    base_url = DEFAULT_CONFIG.get("backend_url", "https://api.openai.com/v1")
    return ChatOpenAI(model=model, base_url=base_url)


def improve_text(llm, text: str, locale: str) -> str:
    system_prompt = (
        "You are an expert financial editor. Improve clarity, grammar, spelling, and coherence, "
        "and enrich with concise, factual connective phrasing without fabricating data. "
        "Preserve the document's structure, headings, bullet points, numbers, tickers, and dates. "
        "Keep the original language unchanged (locale="
        f"{locale.upper()}"
        "). Do not add disclaimers or metadata. Return only the revised markdown content."
    )
    messages = [("system", system_prompt), ("human", text)]
    result = llm.invoke(messages)
    return getattr(result, "content", str(result))


def translate_en_to_ko(llm, text: str) -> str:
    system_prompt = (
        "You are a precise translator for financial documents. Translate the following markdown "
        "from English to Korean. Preserve meaning, technical terminology, numeric values, tickers, "
        "and markdown structure (headings, lists). Do not add explanations."
    )
    messages = [("system", system_prompt), ("human", text)]
    result = llm.invoke(messages)
    return getattr(result, "content", str(result))


def save_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content.rstrip() + "\n")


def process_reports_for_date(trade_date: str) -> None:
    reports_root = get_project_root() / "reports"
    md_files = discover_markdown_files_for_date(reports_root, trade_date)
    if not md_files:
        print(f"No markdown files found for date {trade_date} under {reports_root}")
        return

    llm = create_llm()

    for path in md_files:
        locale = path.parent.name.upper()
        try:
            original = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Improve the document in-place (for both EN and KO and any other locales)
        improved = improve_text(llm, original, locale)
        save_text(path, improved)

        # If this is an EN file, also create/update the KO translation
        if locale in ("EN", "EN-US", "EN-GB"):
            ko_path = path.parent.parent / "KO" / path.name
            translated = translate_en_to_ko(llm, improved)
            # Optionally run an extra pass to polish the Korean output
            polished_ko = improve_text(llm, translated, "KO")
            save_text(ko_path, polished_ko)


def main():
    parser = argparse.ArgumentParser(description="Post-process TradingAgents reports for a given date.")
    parser.add_argument("--date", required=True, help="Target date in YYYY-MM-DD")
    args = parser.parse_args()

    process_reports_for_date(args.date)


if __name__ == "__main__":
    main()


