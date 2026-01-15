#!/usr/bin/env python3
"""
Programmatic runner for MBTI Research Colab Notebook
Extracts code cells and executes them, handling Colab-specific features
"""

import json
import os
import sys
from pathlib import Path

def extract_code_cells(notebook_path):
    """Extract code cells from notebook"""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    code_cells = []
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            source = ''.join(cell['source'])
            # Skip cells with Colab-specific features or interactive input for now
            if 'google.colab' in source:
                print(f"⏭️  Skipping cell {i}: Colab-specific feature")
                continue
            if 'getpass' in source or ('input(' in source and 'getpass' not in source):
                print(f"⏭️  Skipping cell {i}: Interactive input")
                continue
            code_cells.append((i, source))
    
    return code_cells

def execute_code_cells(code_cells, notebook_dir):
    """Execute code cells in sequence"""
    original_dir = os.getcwd()
    os.chdir(notebook_dir)
    
    try:
        for cell_idx, code in code_cells:
            print(f"\n{'='*60}")
            print(f"Executing cell {cell_idx}")
            print(f"{'='*60}")
            
            # Handle magic commands
            if code.strip().startswith('%pip'):
                print(f"⚠️  Magic command detected: {code.split(chr(10))[0]}")
                print("   Please run manually: pip install ...")
                continue
            
            # Execute code
            try:
                exec(code, {'__name__': '__main__', '__file__': notebook_dir})
                print(f"✅ Cell {cell_idx} executed successfully")
            except Exception as e:
                print(f"❌ Error in cell {cell_idx}: {e}")
                import traceback
                traceback.print_exc()
    finally:
        os.chdir(original_dir)

def main():
    notebook_path = Path(__file__).parent / 'MBTI_Research_Colab.ipynb'
    
    if not notebook_path.exists():
        print(f"❌ Notebook not found: {notebook_path}")
        sys.exit(1)
    
    print(f"📓 Loading notebook: {notebook_path}")
    code_cells = extract_code_cells(notebook_path)
    print(f"✅ Extracted {len(code_cells)} code cells")
    
    print("\n⚠️  Note: This runner has limitations:")
    print("   - Skips Colab-specific features (google.colab.files)")
    print("   - Skips interactive inputs (getpass, input)")
    print("   - Requires API keys as environment variables")
    print("\n💡 For full functionality, use Google Colab\n")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted")
        return
    
    execute_code_cells(code_cells, notebook_path.parent)

if __name__ == '__main__':
    main()
