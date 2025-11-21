#!/usr/bin/env python3
"""
Test script to preview how environments will be categorized.
"""

from pathlib import Path
import sys

# Import categorization function
sys.path.insert(0, '.')
from generate_pages import categorize_environment, parse_env_name_from_markdown

def main():
    markdown_dir = Path('markdowns')
    
    if not markdown_dir.exists():
        print("markdowns/ directory not found!")
        return
    
    md_files = sorted(markdown_dir.glob('*.md'))
    
    # Group by category
    categories = {
        'Geometric 2D': [],
        'Geometric 3D': [],
        'Dynamic 2D': [],
        'Dynamic 3D': []
    }
    
    for md_file in md_files:
        with open(md_file, 'r') as f:
            content = f.read()
        
        env_name = parse_env_name_from_markdown(content)
        category = categorize_environment(env_name)
        categories[category].append(env_name)
    
    # Display results
    print("="*70)
    print("ENVIRONMENT CATEGORIZATION PREVIEW")
    print("="*70)
    
    for cat_name, envs in categories.items():
        print(f"\n{cat_name} ({len(envs)} environments):")
        print("-" * 70)
        for env in sorted(envs):
            print(f"  • {env}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {sum(len(envs) for envs in categories.values())} environments")
    print("="*70)

if __name__ == '__main__':
    main()

