#!/usr/bin/env python3
"""
Generate HTML for the demo showcase section on the home page.
This script finds representative demo GIFs from each environment group.
"""

from pathlib import Path
import random

def find_demo_gifs():
    """Find one demo GIF from each environment group."""
    demo_dir = Path('markdowns/assets/demo_gifs')
    
    if not demo_dir.exists():
        print("Demo GIFs directory not found!")
        return []
    
    # Get all subdirectories (one per environment variant)
    env_dirs = [d for d in demo_dir.iterdir() if d.is_dir()]
    
    # Group by base environment name (remove variant suffix)
    from collections import defaultdict
    import re
    
    groups = defaultdict(list)
    for env_dir in env_dirs:
        # Extract base name (e.g., "ClutteredRetrieval2D" from "ClutteredRetrieval2D-o1")
        base_name = re.sub(r'-[a-z]\d+$', '', env_dir.name)
        groups[base_name].append(env_dir)
    
    # Select one GIF from each group
    showcase_gifs = []
    for base_name, dirs in sorted(groups.items()):
        # Pick the first directory (usually the simplest variant)
        demo_dir_path = dirs[0]
        
        # Find GIFs in this directory
        gifs = list(demo_dir_path.glob('*.gif'))
        
        if gifs:
            # Pick the first GIF (or random if you prefer)
            selected_gif = gifs[0]
            relative_path = str(selected_gif.relative_to(Path('.')))
            
            showcase_gifs.append({
                'path': relative_path,
                'name': base_name,
                'full_name': demo_dir_path.name
            })
    
    return showcase_gifs

def generate_showcase_html(max_gifs=9):
    """Generate HTML for the showcase section."""
    gifs = find_demo_gifs()
    
    # Limit to max_gifs for visual appeal
    if len(gifs) > max_gifs:
        # You can choose which ones to show, or sample randomly
        # For now, let's take the first max_gifs
        gifs = gifs[:max_gifs]
    
    print(f"\nGenerating showcase with {len(gifs)} environment groups:\n")
    
    html = '''                <div class="demo-showcase">
                    <div class="demo-gif-grid">
'''
    
    for gif in gifs:
        print(f"  • {gif['name']} ({gif['full_name']})")
        html += f'''                        <div class="demo-gif-item">
                            <img src="{gif['path']}" alt="{gif['name']} Demo">
                            <span class="demo-label">{gif['name']}</span>
                        </div>
'''
    
    html += '''                    </div>
                </div>
'''
    
    print(f"\n{'='*60}")
    print("Copy the HTML below and paste it into index.html")
    print("inside the #hero section (after the <p> tag):")
    print('='*60 + '\n')
    print(html)
    
    return html

if __name__ == '__main__':
    print("="*60)
    print("PRBench Showcase Generator")
    print("="*60)
    generate_showcase_html(max_gifs=9)

