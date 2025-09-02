import argparse
import os
import sys
from pathlib import Path
from typing import List

from tradingagents.default_config import DEFAULT_CONFIG
from tenacity import retry, stop_after_attempt, wait_exponential


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


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _invoke_llm(llm, system_prompt: str, text: str) -> str:
    messages = [("system", system_prompt), ("human", text)]
    result = llm.invoke(messages)
    return getattr(result, "content", str(result))


def improve_text(llm, text: str, locale: str) -> str:
    system_prompt = (
        "You are an expert financial editor. Improve clarity, grammar, spelling, and coherence, "
        "and enrich with concise, factual connective phrasing without fabricating data. "
        "Preserve the document's structure, headings, bullet points, numbers, tickers, and dates. "
        "Keep the original language unchanged (locale="
        f"{locale.upper()}"
        "). Do not add disclaimers or metadata. Return only the revised markdown content."
    )
    return _invoke_llm(llm, system_prompt, text)


def translate_en_to_ko(llm, text: str) -> str:
    system_prompt = (
        "You are a precise translator for financial documents. Translate the following markdown "
        "from English to Korean. Preserve meaning, technical terminology, numeric values, tickers, "
        "and markdown structure (headings, lists). Do not add explanations."
    )
    return _invoke_llm(llm, system_prompt, text)


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

    # Check OpenAI key presence early for clearer logs
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY is not set; postprocess will likely be skipped due to auth errors.")

    try:
        llm = create_llm()
    except Exception as e:
        print(f"Failed to initialize LLM: {e}")
        return

    for path in md_files:
        locale = path.parent.name.upper()
        try:
            original = path.read_text(encoding="utf-8")
        except Exception:
            continue

        # Improve the document in-place (for both EN and KO and any other locales)
        try:
            improved = improve_text(llm, original, locale)
            if improved:
                save_text(path, improved)
        except Exception as e:
            print(f"Improve step failed for {path}: {e}")
            # Continue to next file
            continue

        # If this is an EN file, also create/update the KO translation
        if locale in ("EN", "EN-US", "EN-GB"):
            ko_path = path.parent.parent / "KO" / path.name
            try:
                translated = translate_en_to_ko(llm, improved)
                # Optionally run an extra pass to polish the Korean output
                polished_ko = improve_text(llm, translated, "KO")
                if polished_ko:
                    save_text(ko_path, polished_ko)
            except Exception as e:
                print(f"Translate step failed for {path} -> {ko_path}: {e}")
                # Continue processing other files
                continue


def main():
    parser = argparse.ArgumentParser(description="Post-process TradingAgents reports for a given date.")
    parser.add_argument("--date", required=True, help="Target date in YYYY-MM-DD")
    args = parser.parse_args()

    try:
        process_reports_for_date(args.date)
    except Exception as e:
        print(f"Postprocess failed with an unexpected error: {e}")
        # Exit 0 to avoid breaking CI if partial work is done
        sys.exit(0)


if __name__ == "__main__":
    main()


