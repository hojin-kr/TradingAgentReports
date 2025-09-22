#!/usr/bin/env python3
"""
News report post-processing script for structured daily market intelligence.
Transforms comprehensive trading-focused news reports into standardized format using XML template.
"""

import argparse
import json
import re
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from tradingagents.default_config import DEFAULT_CONFIG


class NewsReportTemplate:
    """Handles loading and parsing of XML template for news report structure."""
    
    def __init__(self, template_path: Path):
        self.template_path = template_path
        self.template = self._load_template()
    
    def _load_template(self) -> ET.Element:
        """Load and parse XML template."""
        try:
            tree = ET.parse(self.template_path)
            return tree.getroot()
        except Exception as e:
            raise ValueError(f"Failed to load template from {self.template_path}: {e}")
    
    def get_sections(self) -> List[Dict]:
        """Extract section definitions from template."""
        sections = []
        structure = self.template.find('structure')
        if structure is not None:
            for section in structure.findall('section'):
                section_data = {
                    'name': section.get('name'),
                    'required': section.get('required', 'false').lower() == 'true',
                    'description': section.find('description').text if section.find('description') is not None else '',
                    'max_length': int(section.find('max_length').text) if section.find('max_length') is not None else None,
                    'max_items': int(section.find('max_items').text) if section.find('max_items') is not None else None,
                    'tone': section.find('tone').text if section.find('tone') is not None else '',
                }
                sections.append(section_data)
        return sections
    
    def get_formatting_guidelines(self) -> Dict:
        """Extract formatting guidelines from template."""
        guidelines = {}
        formatting = self.template.find('formatting_guidelines')
        if formatting is not None:
            for child in formatting:
                guidelines[child.tag] = self._parse_element_to_dict(child)
        return guidelines
    
    def get_content_rules(self) -> Dict:
        """Extract content transformation rules from template."""
        rules = {}
        content_rules = self.template.find('content_rules')
        if content_rules is not None:
            for child in content_rules:
                rules[child.tag] = self._parse_element_to_dict(child)
        return rules
    
    def get_output_format(self) -> Dict:
        """Extract output format specifications from template."""
        output_format = {}
        format_node = self.template.find('output_format')
        if format_node is not None:
            output_format = self._parse_element_to_dict(format_node)
        return output_format
    
    def _parse_element_to_dict(self, element: ET.Element) -> Dict:
        """Recursively parse XML element to dictionary."""
        result = {}
        
        # Add text content if present
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # Add attributes
        result.update(element.attrib)
        
        # Add child elements
        for child in element:
            if child.tag in result:
                # Handle multiple children with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(self._parse_element_to_dict(child))
            else:
                result[child.tag] = self._parse_element_to_dict(child)
        
        return result


class NewsReportPostProcessor:
    """Main class for post-processing news reports into structured format."""
    
    def __init__(self, template_path: Path):
        self.template = NewsReportTemplate(template_path)
        self.llm = self._create_llm()
        
    def _create_llm(self) -> ChatOpenAI:
        """Initialize LLM using existing OpenAI API key."""
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        model = DEFAULT_CONFIG.get("quick_think_llm", "gpt-4o-mini")
        base_url = DEFAULT_CONFIG.get("backend_url", "https://api.openai.com/v1")
        return ChatOpenAI(model=model, base_url=base_url, temperature=0.1)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _invoke_llm(self, system_prompt: str, user_content: str) -> str:
        """Invoke LLM with retry logic."""
        messages = [("system", system_prompt), ("human", user_content)]
        result = self.llm.invoke(messages)
        return getattr(result, "content", str(result))
    
    def structure_news_report(self, original_content: str, ticker: str, trade_date: str) -> str:
        """Transform comprehensive news report into structured format using template."""
        
        # Build comprehensive system prompt based on template
        system_prompt = self._build_system_prompt(ticker, trade_date)
        
        # Process the content
        structured = self._invoke_llm(system_prompt, original_content)
        
        return structured
    
    def _build_system_prompt(self, ticker: str, trade_date: str) -> str:
        """Build detailed system prompt based on XML template."""
        
        sections = self.template.get_sections()
        guidelines = self.template.get_formatting_guidelines()
        rules = self.template.get_content_rules()
        output_format = self.template.get_output_format()
        
        prompt_parts = [
            "You are an expert financial analyst specializing in creating structured daily market intelligence reports.",
            f"Transform the following comprehensive news analysis for {ticker} into a standardized, structured format.",
            f"Report Date: {trade_date}",
            "",
            "REQUIRED STRUCTURE AND SECTIONS:",
        ]
        
        # Add section requirements
        for section in sections:
            section_name = section['name'].replace('_', ' ').title()
            prompt_parts.append(f"## {section_name}")
            prompt_parts.append(f"- {section['description']}")
            if section.get('max_length'):
                prompt_parts.append(f"- Maximum length: {section['max_length']} characters")
            if section.get('max_items'):
                prompt_parts.append(f"- Maximum items: {section['max_items']}")
            if section['required']:
                prompt_parts.append("- **REQUIRED SECTION**")
            else:
                prompt_parts.append("- Optional section (include if relevant content available)")
            prompt_parts.append("")
        
        formatting_rules = [
            "FORMATTING GUIDELINES:",
            "• Style: professional, direct, action-oriented",
            "• Reading level: professional trader/investor",
            "• Maximum total length: 2000 words",
            "• Use bullet points for key insights and price levels",
            "• Bold critical price levels and key insights",
            "• Include specific, actionable price levels and targets",
            "",
            "CONTENT TRANSFORMATION RULES:",
            "• Extract and organize all actionable price levels (support/resistance)",
            "• Identify specific catalysts and their market impact",
            "• Provide clear risk/reward scenarios with price targets",
            "• Include position management and risk guidance",
            "• Focus on immediate trading implications",
            "",
            "OUTPUT FORMAT:",
            f"# Daily Trading Intelligence: {ticker} - {trade_date}",
            "",
        ]
        
        template_sections = [
            "## Executive Snapshot",
            "## Macro and Market Backdrop", 
            "## Company-Specific Catalysts and News",
            "## Price Action and Technical Levels",
            "## Trading Scenarios and Outlook",
            "## Key Data Points Summary (if applicable)",
            "",
            "STRUCTURE REQUIREMENTS:",
            "• Use bullet points for catalysts and key developments",
            "• Include specific price levels and targets where available",
            "• Organize trading scenarios as Base Case, Bull Case, Bear Case",
            "• End with summary table if multiple key points need organization",
            "• Focus on actionable intelligence for traders",
            "• Maintain professional, analytical tone",
        ]
        
        prompt_parts.extend(formatting_rules)
        prompt_parts.extend(template_sections)
        
        return "\n".join(prompt_parts)
    
    def process_file(self, file_path: Path, output_path: Optional[Path] = None, force: bool = False) -> bool:
        """Process a single news report file."""
        try:
            # Determine output path
            if output_path is None:
                output_path = file_path.parent / f"structured_{file_path.name}"
            
            # Check if output already exists and is newer than input (unless force=True)
            if not force and self._should_skip_processing(file_path, output_path):
                print(f"⏭ Skipped (already exists): {output_path}")
                return True
            
            # Read original content
            original_content = file_path.read_text(encoding='utf-8')
            
            # Extract ticker and trade date from file path
            ticker = self._extract_ticker_from_path(file_path)
            trade_date = self._extract_date_from_path(file_path)
            
            # Structure the news report
            structured_content = self.structure_news_report(original_content, ticker, trade_date)
            
            # Save structured version
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(structured_content, encoding='utf-8')
            
            print(f"✓ Processed: {file_path} → {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            return False
    
    def _should_skip_processing(self, input_path: Path, output_path: Path) -> bool:
        """Check if processing should be skipped based on file existence and modification times."""
        if not output_path.exists():
            return False
        
        try:
            # Check if the output file looks valid (not empty and has reasonable content)
            if output_path.stat().st_size < 200:  # Less than 200 bytes is probably invalid
                return False
            
            # Quick validation - check if it has expected structure
            content = output_path.read_text(encoding='utf-8')
            if not any(marker in content for marker in ['# Daily Trading Intelligence', '## Executive Snapshot', '## Macro and Market']):
                return False
            
            # Get modification times
            input_mtime = input_path.stat().st_mtime
            output_mtime = output_path.stat().st_mtime
            
            # Skip if output is newer than or equal to input (allowing for small time differences)
            time_diff = output_mtime - input_mtime
            if time_diff >= -1:  # Allow 1 second tolerance for filesystem timing
                return True
            
            # If input is significantly newer, we should reprocess
            return False
            
        except Exception:
            # If we can't check properly, process anyway
            return False
    
    def _extract_ticker_from_path(self, file_path: Path) -> str:
        """Extract ticker symbol from file path."""
        # Path structure: .../TICKER/LOCALE/filename.md
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part in ['BUY', 'HOLD', 'SELL'] and i + 1 < len(parts):
                return parts[i + 1]
        return "UNKNOWN"
    
    def _extract_date_from_path(self, file_path: Path) -> str:
        """Extract trade date from file path."""
        # Path structure: .../YYYY-MM-DD/...
        parts = file_path.parts
        for part in parts:
            if re.match(r'\d{4}-\d{2}-\d{2}', part):
                return part
        return datetime.now().strftime('%Y-%m-%d')


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).resolve().parent


def discover_news_report_files(reports_root: Path, trade_date: str) -> List[Path]:
    """Find all news_report.md files for a given date."""
    base = reports_root / trade_date
    if not base.exists():
        return []
    
    return list(base.glob("**/news_report.md"))


def main():
    """Main entry point for the news report post-processing script."""
    parser = argparse.ArgumentParser(
        description="Post-process news reports into structured daily market intelligence format"
    )
    parser.add_argument(
        "--date", 
        required=True, 
        help="Target date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to XML template file (default: news_report_template.xml in project root)"
    )
    parser.add_argument(
        "--output-suffix",
        default="structured_",
        help="Prefix for output files (default: structured_)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what files would be processed without actually processing them"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force processing even if structured files already exist"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    
    # Set up paths
    project_root = get_project_root()
    template_path = Path(args.template) if args.template else project_root / "news_report_template_simple.xml"
    reports_root = project_root / "reports"
    
    if not template_path.exists():
        print(f"ERROR: Template file not found: {template_path}")
        sys.exit(1)
    
    # Find files to process
    news_report_files = discover_news_report_files(reports_root, args.date)
    
    if not news_report_files:
        print(f"No news_report.md files found for date {args.date}")
        return
    
    print(f"Found {len(news_report_files)} news report files to process for date {args.date}")
    
    if args.dry_run:
        print("\nDRY RUN - Processing analysis:")
        
        # Initialize a mock processor to check skip logic
        try:
            mock_processor = NewsReportPostProcessor(template_path)
        except Exception as e:
            print(f"ERROR: Failed to initialize processor for dry run: {e}")
            return
        
        process_count = 0
        skip_count = 0
        
        for file_path in news_report_files:
            output_path = file_path.parent / f"{args.output_suffix}{file_path.name}"
            
            if not args.force and mock_processor._should_skip_processing(file_path, output_path):
                print(f"  ⏭ SKIP: {file_path} → {output_path} (already exists)")
                skip_count += 1
            else:
                print(f"  ✓ PROCESS: {file_path} → {output_path}")
                process_count += 1
        
        print(f"\nSummary: {process_count} files to process, {skip_count} files to skip")
        return
    
    # Initialize processor
    try:
        processor = NewsReportPostProcessor(template_path)
    except Exception as e:
        print(f"ERROR: Failed to initialize processor: {e}")
        sys.exit(1)
    
    # Process files
    success_count = 0
    skip_count = 0
    total_count = len(news_report_files)
    
    print(f"\nProcessing {total_count} files...")
    
    for file_path in news_report_files:
        output_path = file_path.parent / f"{args.output_suffix}{file_path.name}"
        
        # Check if we should skip (unless force is enabled)
        if not args.force and processor._should_skip_processing(file_path, output_path):
            print(f"⏭ Skipped (already exists): {output_path}")
            skip_count += 1
            success_count += 1  # Count as success since file exists
        elif processor.process_file(file_path, output_path, force=args.force):
            success_count += 1
    
    processed_count = success_count - skip_count
    print(f"\nCompleted: {success_count}/{total_count} files handled successfully")
    if skip_count > 0:
        print(f"  - {processed_count} files processed")
        print(f"  - {skip_count} files skipped (already exist)")
    
    if success_count < total_count:
        print(f"Warning: {total_count - success_count} files failed to process")
        sys.exit(1)


if __name__ == "__main__":
    main()