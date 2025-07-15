#!/bin/bash
# GitHub Actions workflow trigger validator
# File: /home/jjesse/github/baseball_stats/scripts/test_workflow_dispatch.sh

echo "===================================================="
echo "GitHub Actions Workflow Dispatch Validator"
echo "===================================================="

# GitHub username and repository
# NOTE: Replace these with your actual GitHub username and repository name
GITHUB_USERNAME="jjesse"
REPO_NAME="baseball_stats"

# List all workflow files
WORKFLOW_DIR="/home/jjesse/github/baseball_stats/.github/workflows"
WORKFLOW_FILES=$(ls -1 "$WORKFLOW_DIR"/*.yml | grep -v README)

echo "Found $(echo "$WORKFLOW_FILES" | wc -l) workflow files to check"
echo "----------------------------------------------------"

# Check each workflow file for workflow_dispatch trigger
for file in $WORKFLOW_FILES; do
    filename=$(basename "$file")
    echo "Checking $filename..."
    
    # Check if workflow_dispatch is present
    if grep -q "workflow_dispatch" "$file"; then
        echo "  ✅ Found workflow_dispatch trigger text"
        
        # Get the line with workflow_dispatch
        dispatch_line=$(grep -n "workflow_dispatch" "$file" | head -1 | cut -d: -f1)
        
        # Get the surrounding context (3 lines before and after)
        start_line=$((dispatch_line - 3))
        if [ $start_line -lt 1 ]; then start_line=1; fi
        end_line=$((dispatch_line + 3))
        
        echo "  📋 Context around workflow_dispatch (lines $start_line-$end_line):"
        sed -n "${start_line},${end_line}p" "$file" | sed 's/^/    /'
        
        # Check the formatting of the workflow_dispatch trigger
        if grep -q "workflow_dispatch: *{}" "$file"; then
            echo "  ✅ Using minimalist syntax 'workflow_dispatch: {}'"
        elif grep -q "workflow_dispatch: *$" "$file"; then
            echo "  ✅ Using empty syntax 'workflow_dispatch:'"
        else
            # Check if it has inputs or other configurations
            if grep -A5 "workflow_dispatch:" "$file" | grep -q "inputs:"; then
                echo "  ✅ Using extended syntax with inputs"
            else
                echo "  ⚠️ Using non-standard workflow_dispatch syntax"
            fi
        fi
    else
        echo "  ❌ No workflow_dispatch trigger found!"
    fi
    
    # Check indentation and structure
    echo "  🔍 Checking YAML structure..."
    
    # If yamllint is available, use it for validation
    if command -v yamllint &> /dev/null; then
        if yamllint -d "{extends: relaxed, rules: {line-length: disable}}" "$file" > /dev/null 2>&1; then
            echo "  ✅ YAML structure is valid"
        else
            echo "  ❌ YAML structure has issues:"
            yamllint -d "{extends: relaxed, rules: {line-length: disable}}" "$file" | head -5 | sed 's/^/    /'
            if [ $(yamllint -d "{extends: relaxed, rules: {line-length: disable}}" "$file" | wc -l) -gt 5 ]; then
                echo "    ... (more issues omitted)"
            fi
        fi
    else
        echo "  ⚠️ yamllint not available, skipping detailed YAML validation"
    fi
    
    echo "----------------------------------------------------"
done

echo "===================================================="
echo "Summary of workflow files:"
echo "===================================================="

for file in $WORKFLOW_FILES; do
    filename=$(basename "$file")
    
    # Get scheduled timing if any
    if grep -q "cron:" "$file"; then
        cron_expression=$(grep -A1 "cron:" "$file" | tail -1 | sed 's/.*cron: *//;s/["\047]//g;s/ *#.*//;s/ *$//')
        echo "📅 $filename - Schedule: $cron_expression"
    else
        echo "🔘 $filename - No schedule (manual trigger only)"
    fi
done

echo "===================================================="
echo "Testing workflow_dispatch via GitHub API"
echo "===================================================="
echo "To test workflows via the GitHub API, you need a Personal Access Token."
echo "This requires manually running the following commands in your terminal:"
echo ""
echo "# Example curl command to trigger a workflow:"
echo "curl -X POST \\"
echo "  -H \"Authorization: token YOUR_GITHUB_TOKEN\" \\"
echo "  -H \"Accept: application/vnd.github.v3+json\" \\"
echo "  https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/actions/workflows/update-batting.yml/dispatches \\"
echo "  -d '{\"ref\":\"main\"}'"
echo ""
echo "===================================================="
echo "Validation complete!"