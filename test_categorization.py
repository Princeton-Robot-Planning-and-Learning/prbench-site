#!/usr/bin/env python3
"""
Test script to preview how environments will be categorized and grouped.
"""

from pathlib import Path
import sys
from collections import defaultdict

# Import categorization function
sys.path.insert(0, '.')
from generate_pages import categorize_environment, parse_env_name_from_markdown, extract_base_environment_name

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
        base_name = extract_base_environment_name(env_name)
        categories[category].append({'name': env_name, 'base': base_name})
    
    # Display results
    print("="*70)
    print("ENVIRONMENT CATEGORIZATION & GROUPING PREVIEW")
    print("="*70)
    
    for cat_name, envs in categories.items():
        print(f"\n{cat_name} ({len(envs)} environments):")
        print("-" * 70)
        
        # Group by base name
        groups = defaultdict(list)
        for env in envs:
            groups[env['base']].append(env['name'])
        
        for base_name in sorted(groups.keys()):
            variants = sorted(groups[base_name])
            if len(variants) == 1:
                print(f"  • {base_name}")
                print(f"      └─ {variants[0]}")
            else:
                print(f"  • {base_name} ({len(variants)} variants)")
                for variant in variants:
                    variant_suffix = variant.replace(base_name, '').lstrip('-')
                    if variant_suffix:
                        print(f"      └─ {variant_suffix}")
                    else:
                        print(f"      └─ {variant}")
    
    print("\n" + "="*70)
    print(f"TOTAL: {sum(len(envs) for envs in categories.values())} environments")
    print("="*70)

if __name__ == '__main__':
    main()

