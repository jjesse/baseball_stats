#!/bin/bash
# Script to validate GitHub Actions workflow files
# File: /home/jjesse/github/baseball_stats/scripts/validate_workflows.sh

echo "Validating GitHub Actions workflow files..."
echo "--------------------------------------------"

# Directory containing workflow files
WORKFLOW_DIR="/home/jjesse/github/baseball_stats/.github/workflows"

# Ensure the workflow directory exists
if [ ! -d "$WORKFLOW_DIR" ]; then
    echo "Error: Workflow directory not found at $WORKFLOW_DIR"
    exit 1
fi

# Check for workflow_dispatch trigger in all YAML files
for file in "$WORKFLOW_DIR"/*.yml; do
    filename=$(basename "$file")
    echo "Checking $filename..."
    
    # Create a clean copy to validate
    temp_file=$(mktemp)
    cp "$file" "$temp_file"
    
    # Remove any potential BOM or special characters
    sed -i 's/\r$//' "$temp_file"  # Remove Windows line endings
    
    # Check if workflow_dispatch is present in the file
    if grep -q "workflow_dispatch:" "$temp_file"; then
        echo "✓ Found workflow_dispatch trigger in $filename"
        
        # Try to validate the YAML structure
        if command -v yamllint &> /dev/null; then
            if yamllint -d "{extends: relaxed, rules: {line-length: disable}}" "$temp_file" &> /dev/null; then
                echo "✓ YAML syntax is valid in $filename"
            else
                echo "✗ YAML syntax errors found in $filename"
                yamllint -d "{extends: relaxed, rules: {line-length: disable}}" "$temp_file"
            fi
        else
            echo "! yamllint not available, skipping syntax validation"
        fi
        
        # Extract the 'on' section to check trigger structure
        on_section=$(sed -n '/^on:/,/^[a-z]/{/^[a-z]/!p}' "$temp_file")
        if echo "$on_section" | grep -q "workflow_dispatch:"; then
            echo "✓ workflow_dispatch is properly under 'on' section"
        else
            echo "✗ workflow_dispatch may not be properly structured under 'on' section"
            echo "--- on section content ---"
            echo "$on_section"
            echo "-----------------------"
        fi
    else
        echo "✗ No workflow_dispatch trigger found in $filename"
    fi
    
    # Clean up temp file
    rm "$temp_file"
    echo "--------------------------------------------"
done

# Create a new version of update-batting.yml with guaranteed workflow_dispatch trigger
echo "Creating a new version of update-batting.yml with guaranteed workflow_dispatch trigger..."
cat > "$WORKFLOW_DIR/update-batting-fixed.yml" << 'EOF'
name: Update Batting Stats (Fixed)

on:
  workflow_dispatch: {}  # Minimalist workflow_dispatch trigger
  schedule:
    - cron: '0 12 * * *'  # Runs daily at 12:00 UTC (main branch only)

jobs:
  update-batting:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    # Skip scheduled runs on preview branch
    if: github.event_name == 'workflow_dispatch' || github.ref == 'refs/heads/main'

    steps:
    - name: Checkout repo
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pybaseball matplotlib seaborn pandas
      timeout-minutes: 5

    - name: Run batting chart script
      run: |
        # Set output path based on branch
        if [ "${{ github.ref }}" = "refs/heads/preview" ]; then
          export OUTPUT_PATH="docs/preview"
          mkdir -p docs/preview
        else
          export OUTPUT_PATH="docs"
        fi
        python batting_chart.py || exit 1
      timeout-minutes: 5

    - name: Archive current batting stats
      run: |
        mkdir -p archive
        if [ "${{ github.ref }}" = "refs/heads/preview" ]; then
          if [ -f "docs/preview/batting_stats.csv" ]; then
            cp docs/preview/batting_stats.csv archive/batting_$(date +%F).csv
          fi
        else
          if [ -f "docs/batting_stats.csv" ]; then
            cp docs/batting_stats.csv archive/batting_$(date +%F).csv
          fi
        fi
      timeout-minutes: 2

    - name: Run batting trend chart script
      run: |
        # Set output path based on branch
        if [ "${{ github.ref }}" = "refs/heads/preview" ]; then
          export OUTPUT_PATH="docs/preview"
          mkdir -p docs/preview
        else
          export OUTPUT_PATH="docs"
        fi
        python trend_batting.py || {
          echo "Warning: trend_batting.py failed, creating fallback files"
          mkdir -p "${OUTPUT_PATH}"
          echo "Trend analysis failed - $(date)" > "${OUTPUT_PATH}/trend_batting_error.txt"
          for stat in AVG HR RBI; do
            touch "${OUTPUT_PATH}/trend_batting_${stat,,}.png"
          done
        }
      timeout-minutes: 5
      continue-on-error: true

    - name: Commit and push changes
      run: |
        if [[ -n $(git status --porcelain) ]]; then
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          
          # Set output path based on branch
          if [ "${{ github.ref }}" = "refs/heads/preview" ]; then
            export OUTPUT_PATH="docs/preview"
            mkdir -p docs/preview
            COMMIT_MSG="Update batting stats and trends (preview) [skip ci]"
            FILE_PATTERN="docs/preview/batting_*.png docs/preview/batting_*.html docs/preview/last_updated_batting.txt archive/batting_*.csv"
          else
            export OUTPUT_PATH="docs"
            COMMIT_MSG="Update batting stats and trends [skip ci]"
            FILE_PATTERN="docs/batting_*.png docs/batting_*.html docs/last_updated_batting.txt archive/batting_*.csv"
          fi
          
          git add $FILE_PATTERN
          git commit -m "$COMMIT_MSG"
          git push origin ${{ github.ref_name }}
        else
          echo "No changes to commit"
        fi
      timeout-minutes: 5
EOF

echo "Created /home/jjesse/github/baseball_stats/.github/workflows/update-batting-fixed.yml"
echo "--------------------------------------------"

echo "Validation complete. Check the output for any issues."