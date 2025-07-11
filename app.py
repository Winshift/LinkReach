#!/usr/bin/env python3
"""Simple test app for Hugging Face Spaces"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

try:
    print("\nTrying to import backend package...")
    import backend
    print("✓ backend package imported successfully")
    
    print("\nTrying to import backend.models...")
    import backend.models
    print("✓ backend.models imported successfully")
    
    print("\nTrying to import backend.models.schemas...")
    from backend.models.schemas import FilterRequest
    print("✓ backend.models.schemas imported successfully")
    
    print("\nTrying to import backend.services...")
    import backend.services
    print("✓ backend.services imported successfully")
    
    print("\nTrying to import backend.api...")
    import backend.api
    print("✓ backend.api imported successfully")
    
    print("\nTrying to import main...")
    import main
    print("✓ main imported successfully")
    
    print("\n✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Other error: {e}")
    import traceback
    traceback.print_exc()

import pandas as pd
from prompt_to_filter import generate_filter_code
import re

def main():
    # path = input("📂 Enter CSV file path (e.g., connections.csv): ").strip()
    prompt = input("💬 Enter your filtering prompt: ").strip()

    with open('connections.csv', encoding='utf-8') as f:
        for i in range(5):
            print(f.readline().strip())

    try:
        df = pd.read_csv('connections.csv')
    except Exception as e:
        print("❌ Error loading CSV:", e)
        return

    print(f"\n🔍 Previewing your data...\n{df.head(5)}\n")

    sample_df = df.head(5).to_string(index=False)

    print("🤖 Generating filtering code from prompt...\n")
    filter_code = generate_filter_code(prompt, sample_df)
    print("🧠 GPT-generated code:\n", filter_code)

    # Clean GPT output
    clean_code = re.sub(r"```(?:python)?|```", "", filter_code).strip()

    print("🧠 Cleaned Filter Code:\n", clean_code)

    try:
        local_vars = {'df': df}
        exec(filter_code, {}, local_vars)
        filtered_df = local_vars['df']
    except Exception as e:
        print("❌ Error executing filter:", e)
        return

    output_file = "filtered_results.csv"
    filtered_df.to_csv(output_file, index=False)
    print(f"\n✅ Done! Filtered {len(filtered_df)} results saved to: {output_file}")

    show = input("👀 Show results in terminal? (y/n): ").lower()
    if show == 'y':
        print(filtered_df)

if __name__ == "__main__":
    main()
