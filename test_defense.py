#!/usr/bin/env python3
"""
Quick script to generate initial defensive stats data for testing
"""
import subprocess
import sys
import os

def main():
    print("Generating defensive statistics data...")
    
    # Change to the correct directory
    os.chdir('/home/jjesse/github/baseball_stats')
    
    try:
        # Run the defense chart generator
        result = subprocess.run([sys.executable, 'defense_chart.py'], 
                              capture_output=True, text=True, timeout=300)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✓ Defense charts generated successfully!")
        else:
            print(f"❌ Script failed with return code: {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("❌ Script timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error running script: {e}")

if __name__ == "__main__":
    main()