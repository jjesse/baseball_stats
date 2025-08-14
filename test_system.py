#!/usr/bin/env python3
"""
Test runner to validate the MLB Stats Dashboard functionality
"""
import os
import sys
import subprocess
import json
from pathlib import Path


def test_file_exists(filepath, description):
    """Test if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False


def test_directory_structure():
    """Test that all required directories and files exist"""
    print("\n🔍 Testing Directory Structure...")

    required_files = [
        ("docs/index.html", "Homepage"),
        ("docs/pitching.html", "Pitching Dashboard"),
        ("docs/batting.html", "Batting Dashboard"),
        ("docs/standings.html", "Standings Dashboard"),
        ("docs/mvp-cy-young.html", "MVP & Cy Young Dashboard"),
        ("mvp_cy_young_calculator.py", "Award Calculator Script"),
        ("create_award_charts.py", "Chart Generator Script"),
        ("pitching_chart.py", "Pitching Script"),
        ("batting_chart.py", "Batting Script"),
        ("standings_chart.py", "Standings Script"),
        ("requirements.txt", "Dependencies File"),
        (".github/workflows/update-mvp-cy-young.yml", "MVP/Cy Young Workflow"),
        (".github/workflows/update-all.yml", "Master Workflow"),
        ("README.md", "Documentation"),
    ]

    results = []
    for filepath, description in required_files:
        results.append(test_file_exists(filepath, description))

    return all(results)


def test_navigation_consistency():
    """Test that all HTML files have consistent navigation"""
    print("\n🧭 Testing Navigation Consistency...")

    html_files = [
        "docs/index.html",
        "docs/pitching.html",
        "docs/batting.html",
        "docs/standings.html",
        "docs/mvp-cy-young.html",
    ]

    expected_nav_links = [
        'href="index.html"',
        'href="pitching.html"',
        'href="batting.html"',
        'href="standings.html"',
        'href="mvp-cy-young.html"',
    ]

    all_good = True
    for html_file in html_files:
        if os.path.exists(html_file):
            with open(html_file, "r") as f:
                content = f.read()

            missing_links = []
            for link in expected_nav_links:
                if link not in content:
                    missing_links.append(link)

            if missing_links:
                print(f"❌ {html_file} missing: {missing_links}")
                all_good = False
            else:
                print(f"✅ {html_file} has complete navigation")
        else:
            print(f"❌ {html_file} not found")
            all_good = False

    return all_good


def test_script_syntax():
    """Test that Python scripts have valid syntax"""
    print("\n🐍 Testing Python Script Syntax...")

    python_scripts = [
        "mvp_cy_young_calculator.py",
        "create_award_charts.py",
        "pitching_chart.py",
        "batting_chart.py",
        "standings_chart.py",
    ]

    all_good = True
    for script in python_scripts:
        if os.path.exists(script):
            try:
                # Test syntax by compiling
                with open(script, "r") as f:
                    compile(f.read(), script, "exec")
                print(f"✅ {script} - Syntax OK")
            except SyntaxError as e:
                print(f"❌ {script} - Syntax Error: {e}")
                all_good = False
        else:
            print(f"❌ {script} - File not found")
            all_good = False

    return all_good


def test_award_calculator():
    """Test the MVP/Cy Young calculator with fallback data"""
    print("\n🏆 Testing Award Prediction Calculator...")

    try:
        # Try importing the module
        sys.path.append(".")

        # Test if we can run the fallback functionality
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                """
import sys
sys.path.append(".")
try:
    from mvp_cy_young_calculator import generate_award_predictions
    result = generate_award_predictions()
    print("SUCCESS: Award calculator ran successfully")
    if "al_mvp" in result and "nl_mvp" in result:
        print("SUCCESS: Generated AL and NL MVP predictions")
    if "al_cy_young" in result and "nl_cy_young" in result:
        print("SUCCESS: Generated AL and NL Cy Young predictions")
    # Check if we have actual data vs fallback
    if result.get("al_mvp") and len(result["al_mvp"]) > 0:
        first_player = result["al_mvp"][0]
        if "WAR" in first_player:
            print("SUCCESS: Using advanced statistical analysis")
        else:
            print("INFO: Using fallback predictions (no real data available)")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
            """,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ Award calculator works!")
            print(result.stdout)
            return True
        else:
            print(f"❌ Award calculator failed:")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            return False

    except Exception as e:
        print(f"❌ Error testing award calculator: {e}")
        return False


def test_workflows():
    """Test that GitHub Actions workflows are valid YAML"""
    print("\n⚙️ Testing GitHub Actions Workflows...")

    workflows = [
        ".github/workflows/update-mvp-cy-young.yml",
        ".github/workflows/update-all.yml",
        ".github/workflows/update-batting.yml",
        ".github/workflows/update-pitching.yml",
        ".github/workflows/update-standings.yml",
    ]

    all_good = True
    for workflow in workflows:
        if os.path.exists(workflow):
            try:
                import yaml

                with open(workflow, "r") as f:
                    yaml.safe_load(f)
                print(f"✅ {workflow} - Valid YAML")
            except ImportError:
                print(f"⚠️ {workflow} - Cannot validate (PyYAML not installed)")
            except Exception as e:
                print(f"❌ {workflow} - Invalid YAML: {e}")
                all_good = False
        else:
            print(f"❌ {workflow} - File not found")
            all_good = False

    return all_good


def generate_test_data():
    """Generate test data files to simulate a working system"""
    print("\n📊 Generating Test Data...")

    os.makedirs("docs", exist_ok=True)

    # Create test award predictions JSON - updated to match new format
    test_predictions = {
        "al_mvp": [
            {
                "Name": "Aaron Judge",
                "Team": "NYY",
                "MVP_Probability": 85.2,
                "Key_Stats": "58HR/144RBI/.322AVG",
                "WAR": 10.6,
                "OPS": 1.111
            },
            {
                "Name": "Shohei Ohtani",
                "Team": "LAA",
                "MVP_Probability": 72.8,
                "Key_Stats": "44HR/95RBI/.304AVG",
                "WAR": 9.6,
                "OPS": 1.021
            },
        ],
        "nl_mvp": [
            {
                "Name": "Ronald Acuña Jr.",
                "Team": "ATL",
                "MVP_Probability": 89.3,
                "Key_Stats": "40HR/104RBI/.337AVG",
                "WAR": 8.3,
                "OPS": 1.012
            },
            {
                "Name": "Mookie Betts",
                "Team": "LAD",
                "MVP_Probability": 71.5,
                "Key_Stats": "35HR/107RBI/.307AVG",
                "WAR": 8.3,
                "OPS": .903
            },
        ],
        "al_cy_young": [
            {
                "Name": "Gerrit Cole",
                "Team": "NYY",
                "CyYoung_Probability": 78.4,
                "Key_Stats": "15-4/2.63ERA/222K",
                "WAR": 6.1,
                "ERA": 2.63,
                "WHIP": 1.02
            },
            {
                "Name": "Shane Bieber",
                "Team": "CLE",
                "CyYoung_Probability": 71.2,
                "Key_Stats": "12-8/2.88ERA/198K",
                "WAR": 5.9,
                "ERA": 2.88,
                "WHIP": 1.11
            },
        ],
        "nl_cy_young": [
            {
                "Name": "Spencer Strider",
                "Team": "ATL",
                "CyYoung_Probability": 92.1,
                "Key_Stats": "20-5/2.67ERA/281K",
                "WAR": 8.8,
                "ERA": 2.67,
                "WHIP": 0.99
            },
            {
                "Name": "Zac Gallen",
                "Team": "ARI",
                "CyYoung_Probability": 76.8,
                "Key_Stats": "17-9/3.47ERA/220K",
                "WAR": 5.6,
                "ERA": 3.47,
                "WHIP": 1.13
            },
        ],
        "last_updated": "2025-01-17 14:30:00",
        "al_mvp_leader": "Aaron Judge",
        "nl_mvp_leader": "Ronald Acuña Jr.",
        "al_cy_young_leader": "Gerrit Cole",
        "nl_cy_young_leader": "Spencer Strider"
    }

    with open("docs/award_predictions.json", "w") as f:
        json.dump(test_predictions, f, indent=2)

    print("✅ Generated test award predictions data")

    # Create test timestamp files
    timestamp_files = [
        "docs/last_updated_batting.txt",
        "docs/last_updated_pitching.txt",
        "docs/last_updated_standings.txt",
    ]

    for file in timestamp_files:
        with open(file, "w") as f:
            f.write("Last updated: 2025-01-17 14:30:00")
        print(f"✅ Generated {file}")


def main():
    """Run all tests"""
    print("🏟️ MLB Stats Dashboard - System Validation Test")
    print("=" * 50)

    tests = [
        ("Directory Structure", test_directory_structure),
        ("Navigation Consistency", test_navigation_consistency),
        ("Python Script Syntax", test_script_syntax),
        ("GitHub Actions Workflows", test_workflows),
        ("Award Calculator", test_award_calculator),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Test failed with error: {e}")
            results.append((test_name, False))

    # Generate test data
    generate_test_data()

    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL SYSTEMS GO! Your MLB Stats Dashboard is ready!")
        print("\n📝 Next Steps:")
        print(
            "1. Run 'python mvp_cy_young_calculator.py' to generate award predictions"
        )
        print("2. Open 'docs/index.html' in a browser to test the dashboard")
        print("3. Test the MVP & Cy Young page navigation")
        print("4. Trigger the GitHub Actions workflow to test automation")
    else:
        print(f"\n⚠️ {total - passed} issues found. Please fix before proceeding.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
