#!/bin/bash

# Test script for GitHub Actions workflows
# This script helps test the workflows locally before pushing

set -e

echo "🧪 Testing GitHub Actions Workflows"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if required files exist
echo ""
echo "📁 Checking required files..."

files_to_check=(
    "news_report_template_simple.xml"
    "report_template.xml" 
    "postprocess_news_reports.py"
    "postprocess_final_reports.py"
    ".github/workflows/postprocess-news-reports.yml"
    ".github/workflows/postprocess-reports.yml"
    ".github/workflows/postprocess-all-reports.yml"
    ".github/workflows/postprocess-sequential.yml"
)

missing_files=0
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "$file exists"
    else
        print_status 1 "$file is missing"
        missing_files=$((missing_files + 1))
    fi
done

if [ $missing_files -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ $missing_files required files are missing. Please create them before running workflows.${NC}"
    exit 1
fi

# Check Python dependencies
echo ""
echo "🐍 Checking Python dependencies..."

python3 -c "import xml.etree.ElementTree as ET; print('✅ xml.etree.ElementTree available')" 2>/dev/null || {
    print_status 1 "xml.etree.ElementTree not available"
    exit 1
}

python3 -c "import pathlib; print('✅ pathlib available')" 2>/dev/null || {
    print_status 1 "pathlib not available"  
    exit 1
}

# Check if langchain-openai is available (optional for testing)
python3 -c "import langchain_openai; print('✅ langchain-openai available')" 2>/dev/null || {
    print_warning "langchain-openai not available (install with: pip install langchain-openai)"
}

python3 -c "import tenacity; print('✅ tenacity available')" 2>/dev/null || {
    print_warning "tenacity not available (install with: pip install tenacity)"
}

# Test XML template parsing
echo ""
echo "📋 Testing XML template parsing..."

python3 << 'EOF'
import xml.etree.ElementTree as ET
import sys

def test_xml_file(filename):
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        print(f"✅ {filename} is valid XML")
        
        # Check for required elements
        if filename == "news_report_template_simple.xml":
            structure = root.find('structure')
            if structure is not None:
                sections = structure.findall('section')
                print(f"   Found {len(sections)} sections")
                required_sections = ['executive_snapshot', 'macro_backdrop', 'company_specific_catalysts']
                for req in required_sections:
                    found = any(s.get('name') == req for s in sections)
                    if found:
                        print(f"   ✅ Required section '{req}' found")
                    else:
                        print(f"   ❌ Required section '{req}' missing")
                        return False
        return True
    except ET.ParseError as e:
        print(f"❌ {filename} has XML syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ {filename} not found")
        return False
    except Exception as e:
        print(f"❌ Error parsing {filename}: {e}")
        return False

success = True
for template in ["news_report_template_simple.xml", "report_template.xml"]:
    if not test_xml_file(template):
        success = False

sys.exit(0 if success else 1)
EOF

print_status $? "XML template validation"

# Test Python script syntax
echo ""
echo "🔍 Testing Python script syntax..."

python3 -m py_compile postprocess_news_reports.py 2>/dev/null
print_status $? "postprocess_news_reports.py syntax"

python3 -m py_compile postprocess_final_reports.py 2>/dev/null  
print_status $? "postprocess_final_reports.py syntax"

# Check for sample data (optional)
echo ""
echo "📊 Checking for sample data..."

if [ -d "reports" ]; then
    latest_date=$(find reports -maxdepth 1 -type d -name "20*" | sort | tail -1 | xargs basename 2>/dev/null || echo "")
    if [ -n "$latest_date" ]; then
        news_count=$(find "reports/$latest_date" -name "news_report.md" 2>/dev/null | wc -l)
        final_count=$(find "reports/$latest_date" -name "final_trade_decision.md" 2>/dev/null | wc -l)
        
        print_info "Latest report date: $latest_date"
        print_info "News reports found: $news_count"
        print_info "Final decision reports found: $final_count"
        
        if [ $news_count -gt 0 ] || [ $final_count -gt 0 ]; then
            print_status 0 "Sample data available for testing"
        else
            print_warning "No sample reports found in $latest_date"
        fi
    else
        print_warning "No dated report directories found"
    fi
else
    print_warning "No reports directory found"
fi

# Test dry run if OPENAI_API_KEY is available (optional)
echo ""
echo "🔑 Testing with API key (if available)..."

if [ -n "$OPENAI_API_KEY" ]; then
    print_info "OPENAI_API_KEY is set"
    
    if [ -n "$latest_date" ] && [ $news_count -gt 0 ]; then
        print_info "Testing news report processing (dry run)..."
        python3 postprocess_news_reports.py --date "$latest_date" --dry-run >/dev/null 2>&1
        print_status $? "News report dry run test"
    fi
    
    if [ -n "$latest_date" ] && [ $final_count -gt 0 ]; then
        print_info "Testing final report processing (dry run)..."  
        python3 postprocess_final_reports.py --date "$latest_date" --dry-run >/dev/null 2>&1
        print_status $? "Final report dry run test"
    fi
else
    print_warning "OPENAI_API_KEY not set - skipping API tests"
fi

# Check GitHub Actions workflow syntax (basic)
echo ""
echo "⚙️  Checking workflow files..."

for workflow in .github/workflows/postprocess-*.yml; do
    if [ -f "$workflow" ]; then
        # Basic YAML syntax check
        python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null
        print_status $? "$(basename $workflow) YAML syntax"
    fi
done

echo ""
echo "🎉 Testing complete!"
echo ""
echo "📝 Next steps:"
echo "1. Ensure OPENAI_API_KEY is set in GitHub repository secrets"
echo "2. Push changes to trigger workflows" 
echo "3. Monitor workflow runs in GitHub Actions tab"
echo "4. Test with manual workflow dispatch first"

echo ""
echo "💡 Quick test commands:"
echo "   # Test sequential processing (RECOMMENDED):"
echo "   gh workflow run postprocess-sequential.yml -f date=YYYY-MM-DD -f dry_run=true"
echo ""
echo "   # Test news reports only:"
echo "   gh workflow run postprocess-news-reports.yml -f date=YYYY-MM-DD -f dry_run=true"
echo ""
echo "   # Test all reports in parallel:"  
echo "   gh workflow run postprocess-all-reports.yml -f date=YYYY-MM-DD -f dry_run=true"