#!/usr/bin/env python3
"""
Enhanced post-processing script for final investment reports.
Transforms complex technical reports into simplified, accessible format for general investors.
Uses XML template to ensure consistent structure and LLM for intelligent simplification.
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from tradingagents.default_config import DEFAULT_CONFIG


class ReportTemplate:
    """Handles loading and parsing of XML template for report structure."""
    
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


class ReportPostProcessor:
    """Main class for post-processing investment reports."""
    
    def __init__(self, template_path: Path):
        self.template = ReportTemplate(template_path)
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
    
    def simplify_report(self, original_content: str, ticker: str, decision: str) -> str:
        """Transform complex report into simplified format using template guidelines."""
        
        # Build comprehensive system prompt based on template
        system_prompt = self._build_system_prompt(ticker, decision)
        
        # Process the content
        simplified = self._invoke_llm(system_prompt, original_content)
        
        return simplified
    
    def _build_system_prompt(self, ticker: str, decision: str) -> str:
        """Build detailed system prompt based on XML template."""
        
        sections = self.template.get_sections()
        guidelines = self.template.get_formatting_guidelines()
        rules = self.template.get_content_rules()
        
        prompt_parts = [
            "You are an expert financial writer specializing in making investment analysis accessible to general investors.",
            f"Transform the following complex investment report for {ticker} into a simplified, easy-to-understand format.",
            "",
            "REQUIRED STRUCTURE:",
        ]
        
        # Add section requirements
        for section in sections:
            if section['required']:
                prompt_parts.append(f"• {section['name'].replace('_', ' ').title()}: {section['description']}")
                if section.get('max_length'):
                    prompt_parts.append(f"  (Maximum {section['max_length']} characters)")
        
        prompt_parts.extend([
            "",
            "LANGUAGE GUIDELINES:",
            f"• Reading level: {guidelines.get('language', {}).get('reading_level', 'high school')}",
            f"• Style: {guidelines.get('language', {}).get('style', 'conversational')}",
            "• Avoid technical jargon - use simple, everyday language",
            "• Use analogies when they help explain complex concepts",
            f"• Maximum total length: {guidelines.get('length', {}).get('total_max_words', 800)} words",
            "",
            "CONTENT TRANSFORMATION RULES:",
        ])
        
        # Add simplification rules
        if 'simplification' in rules and 'replace_technical_terms' in rules['simplification']:
            prompt_parts.append("• Replace technical terms with simple explanations:")
            terms = rules['simplification']['replace_technical_terms']
            if isinstance(terms.get('term'), list):
                for term in terms['term']:
                    if isinstance(term, dict):
                        prompt_parts.append(f"  - '{term.get('original')}' → '{term.get('simple')}'")
        
        prompt_parts.extend([
            "",
            "REMOVE COMPLEX CONTENT:",
            "• Advanced options strategies and complex derivatives",
            "• Detailed financial modeling and academic theories", 
            "• Technical analysis details beyond basic trends",
            "• Regulatory minutiae and complex risk management",
            "",
            "FOCUS ON ESSENTIALS:",
            "• What the company does (in simple terms)",
            "• Why the stock might go up or down",
            "• What could change the outlook",
            "• How much risk is involved",
            "• Practical next steps for investors",
            "",
            f"The original report recommends: {decision}",
            "",
            "Format your response as clear, readable text with appropriate headings.",
            "Write as if explaining to a friend who invests but isn't a financial expert.",
            "Be confident but humble - acknowledge uncertainty where appropriate.",
            "Avoid hype and overly promotional language.",
        ])
        
        return "\n".join(prompt_parts)
    
    def process_file(self, file_path: Path, output_path: Optional[Path] = None) -> bool:
        """Process a single report file."""
        try:
            # Read original content
            original_content = file_path.read_text(encoding='utf-8')
            
            # Extract ticker and decision from file path and content
            ticker = self._extract_ticker_from_path(file_path)
            decision = self._extract_decision_from_content(original_content)
            
            # Simplify the report
            simplified_content = self.simplify_report(original_content, ticker, decision)
            
            # Determine output path
            if output_path is None:
                output_path = file_path.parent / f"simplified_{file_path.name}"
            
            # Save simplified version
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(simplified_content, encoding='utf-8')
            
            print(f"✓ Processed: {file_path} → {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            return False
    
    def _extract_ticker_from_path(self, file_path: Path) -> str:
        """Extract ticker symbol from file path."""
        # Path structure: .../TICKER/LOCALE/filename.md
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part in ['BUY', 'HOLD', 'SELL'] and i + 1 < len(parts):
                return parts[i + 1]
        return "UNKNOWN"
    
    def _extract_decision_from_content(self, content: str) -> str:
        """Extract investment decision from content."""
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        for line in lines[:5]:  # Check first few lines
            upper_line = line.upper()
            if 'DECISION:' in upper_line:
                if 'BUY' in upper_line:
                    return 'BUY'
                elif 'SELL' in upper_line:
                    return 'SELL'
                elif 'HOLD' in upper_line:
                    return 'HOLD'
        
        # Fallback to path-based detection
        for decision in ['BUY', 'SELL', 'HOLD']:
            if decision.lower() in content.lower()[:500]:
                return decision
        
        return 'HOLD'


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).resolve().parent


def discover_final_decision_files(reports_root: Path, trade_date: str) -> List[Path]:
    """Find all final_trade_decision.md files for a given date."""
    base = reports_root / trade_date
    if not base.exists():
        return []
    
    return list(base.glob("**/final_trade_decision.md"))


def main():
    """Main entry point for the post-processing script."""
    parser = argparse.ArgumentParser(
        description="Post-process investment reports to make them accessible to general investors"
    )
    parser.add_argument(
        "--date", 
        required=True, 
        help="Target date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to XML template file (default: report_template.xml in project root)"
    )
    parser.add_argument(
        "--output-suffix",
        default="simplified_",
        help="Prefix for output files (default: simplified_)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what files would be processed without actually processing them"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is required")
        sys.exit(1)
    
    # Set up paths
    project_root = get_project_root()
    template_path = Path(args.template) if args.template else project_root / "report_template.xml"
    reports_root = project_root / "reports"
    
    if not template_path.exists():
        print(f"ERROR: Template file not found: {template_path}")
        sys.exit(1)
    
    # Find files to process
    final_decision_files = discover_final_decision_files(reports_root, args.date)
    
    if not final_decision_files:
        print(f"No final_trade_decision.md files found for date {args.date}")
        return
    
    print(f"Found {len(final_decision_files)} files to process for date {args.date}")
    
    if args.dry_run:
        print("\nDRY RUN - Files that would be processed:")
        for file_path in final_decision_files:
            output_path = file_path.parent / f"{args.output_suffix}{file_path.name}"
            print(f"  {file_path} → {output_path}")
        return
    
    # Initialize processor
    try:
        processor = ReportPostProcessor(template_path)
    except Exception as e:
        print(f"ERROR: Failed to initialize processor: {e}")
        sys.exit(1)
    
    # Process files
    success_count = 0
    total_count = len(final_decision_files)
    
    print(f"\nProcessing {total_count} files...")
    
    for file_path in final_decision_files:
        output_path = file_path.parent / f"{args.output_suffix}{file_path.name}"
        
        if processor.process_file(file_path, output_path):
            success_count += 1
    
    print(f"\nCompleted: {success_count}/{total_count} files processed successfully")
    
    if success_count < total_count:
        print(f"Warning: {total_count - success_count} files failed to process")
        sys.exit(1)


if __name__ == "__main__":
    main()