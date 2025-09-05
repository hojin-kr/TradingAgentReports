import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


# Reuse decision extraction logic to ensure consistency
from gen_reports import decision_from_text_beginning


REPORTS_DECISIONS = ("BUY", "HOLD", "SELL")
PREFERRED_EN_LOCALES = ("EN", "EN-US", "EN-GB")


@dataclass
class TickerLocation:
    date_dir: Path
    decision_dir: str
    ticker_dir: Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parent


def iter_date_dirs(reports_root: Path) -> Iterable[Path]:
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for child in sorted(reports_root.iterdir()):
        if child.is_dir() and date_pattern.match(child.name):
            yield child


def discover_ticker_locations_for_date(date_dir: Path) -> Dict[str, List[TickerLocation]]:
    ticker_to_locations: Dict[str, List[TickerLocation]] = {}
    for decision in REPORTS_DECISIONS:
        ddir = date_dir / decision
        if not ddir.exists() or not ddir.is_dir():
            continue
        for ticker_dir in sorted(ddir.iterdir()):
            if not ticker_dir.is_dir():
                continue
            ticker = ticker_dir.name
            ticker_to_locations.setdefault(ticker, []).append(
                TickerLocation(date_dir=date_dir, decision_dir=decision, ticker_dir=ticker_dir)
            )
    return ticker_to_locations


def _read_first_existing(paths: List[Path]) -> Optional[str]:
    for p in paths:
        try:
            if p.exists() and p.is_file():
                return p.read_text(encoding="utf-8")
        except Exception:
            continue
    return None


def _find_candidate_files(ticker_dir: Path) -> List[Path]:
    candidates: List[Path] = []
    # Prefer EN family
    for loc in PREFERRED_EN_LOCALES:
        candidates.append(ticker_dir / loc / "final_trade_decision.md")
    for loc in PREFERRED_EN_LOCALES:
        candidates.append(ticker_dir / loc / "complete.md")
    # Fallback to any locale present (alphabetical for determinism)
    for locale_dir in sorted([p for p in ticker_dir.iterdir() if p.is_dir()]):
        candidates.append(locale_dir / "final_trade_decision.md")
    for locale_dir in sorted([p for p in ticker_dir.iterdir() if p.is_dir()]):
        candidates.append(locale_dir / "complete.md")
    # Last-resort: other section files which may contain BUY/SELL/HOLD
    for locale_dir in sorted([p for p in ticker_dir.iterdir() if p.is_dir()]):
        for fname in (
            "trader_investment_plan.md",
            "investment_plan.md",
            "market_report.md",
            "sentiment_report.md",
            "fundamentals_report.md",
            "news_report.md",
        ):
            candidates.append(locale_dir / fname)
    return candidates


def determine_decision_for_ticker(locations: List[TickerLocation]) -> str:
    # Search all locations, but prefer those already under a decision dir with authoritative files
    candidate_texts: List[Tuple[str, str]] = []  # (decision_extracted, source_path)
    for loc in locations:
        for file_path in _find_candidate_files(loc.ticker_dir):
            text = _read_first_existing([file_path])
            if not text:
                continue
            decision = decision_from_text_beginning(text)
            if decision in REPORTS_DECISIONS:
                candidate_texts.append((decision, str(file_path)))
                # Prefer immediate return if the file is final_trade_decision.md in EN* locale
                if file_path.name == "final_trade_decision.md" and file_path.parent.name in PREFERRED_EN_LOCALES:
                    return decision
    # If we didn't early return, choose the first consistent one if any
    for d in REPORTS_DECISIONS:
        if any(cand_dec == d for cand_dec, _ in candidate_texts):
            return d
    return "HOLD"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _merge_move(src: Path, dst: Path) -> None:
    """Move directory tree src into dst, merging by locales/files if needed."""
    ensure_dir(dst)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            _merge_move(item, target)
        else:
            ensure_dir(target.parent)
            if target.exists():
                # Overwrite with source version for determinism
                target.unlink()
            shutil.move(str(item), str(target))


def _prune_empty_dirs(path: Path) -> None:
    """Delete empty directories bottom-up under path."""
    if not path.exists():
        return
    # Walk bottom-up
    for sub in sorted(path.rglob("*"), key=lambda p: len(str(p)), reverse=True):
        if sub.is_dir():
            try:
                next(sub.iterdir())
            except StopIteration:
                try:
                    sub.rmdir()
                except Exception:
                    pass


def reorganize_date(date_dir: Path, dry_run: bool = False) -> List[str]:
    actions: List[str] = []
    ticker_map = discover_ticker_locations_for_date(date_dir)
    for ticker, locations in ticker_map.items():
        desired_decision = determine_decision_for_ticker(locations)
        target_dir = date_dir / desired_decision / ticker
        # Create target dir if needed
        if not dry_run:
            ensure_dir(target_dir)
        for loc in locations:
            if loc.ticker_dir.resolve() == target_dir.resolve():
                continue
            # Move/merge this ticker_dir into target_dir
            actions.append(f"MOVE {loc.ticker_dir} -> {target_dir}")
            if not dry_run:
                _merge_move(loc.ticker_dir, target_dir)
                # Remove the now-empty source ticker dir
                try:
                    loc.ticker_dir.rmdir()
                except Exception:
                    pass
        # After moves, prune empty decision dirs under this date
        if not dry_run:
            for decision in REPORTS_DECISIONS:
                _prune_empty_dirs(date_dir / decision)
    return actions


def reorganize_all(reports_root: Path, only_date: Optional[str], dry_run: bool) -> None:
    dates: List[Path]
    if only_date:
        date_dir = reports_root / only_date
        if not date_dir.exists():
            print(f"No such date directory: {date_dir}")
            return
        dates = [date_dir]
    else:
        dates = list(iter_date_dirs(reports_root))

    for date_dir in dates:
        print(f"[Reorg] Processing {date_dir}")
        actions = reorganize_date(date_dir, dry_run=dry_run)
        if dry_run:
            for act in actions:
                print("  ", act)


def main():
    parser = argparse.ArgumentParser(description="Reorganize report directories based on final_trade_decision.")
    parser.add_argument("--date", help="Target date in YYYY-MM-DD. If omitted, process all dates.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned moves without changing files")
    args = parser.parse_args()

    reports_root = get_project_root() / "reports"
    reorganize_all(reports_root, only_date=args.date, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

