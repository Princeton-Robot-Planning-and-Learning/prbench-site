#!/usr/bin/env python3
"""
Generate environment HTML pages from markdown files.
Usage: python generate_pages.py
"""

import os
import re
from pathlib import Path
import markdown

# HTML template for environment pages
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | PRBench</title>
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="environment.css">
</head>
<body>
    <header>
        <nav>
            <div class="container">
                <h1><a href="../index.html" style="color: white; text-decoration: none;">PRBench</a></h1>
                <ul class="nav-links">
                    <li><a href="../index.html#about">About</a></li>
                    <li><a href="../index.html#benchmark">Benchmark</a></li>
                    <li><a href="../index.html#results">Results</a></li>
                    <li><a href="../index.html#contact">Contact</a></li>
                </ul>
            </div>
        </nav>
    </header>

    <main>
        <section class="environment-detail">
            <div class="container">
                <div class="breadcrumb">
                    <a href="../index.html#benchmark">Benchmark</a> / 
                    <span>{category}</span> / 
                    <span>{env_name}</span>
                </div>

                <div class="environment-content">
                    {content}
                </div>

                <div class="back-link">
                    <a href="../index.html#benchmark">← Back to Benchmark</a>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2025 PRBench. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""

def parse_env_name_from_markdown(content):
    """Extract environment name from the first heading."""
    lines = content.strip().split('\n')
    for line in lines:
        if line.startswith('# '):
            # Extract the part after 'prbench/'
            full_name = line[2:].strip()
            if '/' in full_name:
                return full_name.split('/', 1)[1]
            return full_name
    return "Unknown Environment"

def categorize_environment(env_name):
    """Determine category based on environment name."""
    name_lower = env_name.lower()
    
    # Check for 2D vs 3D
    is_2d = '2d' in name_lower
    is_3d = '3d' in name_lower
    
    # For 2D: Only environments starting with "Dyn" are Dynamic 2D
    # For 3D: TidyBot environments are Dynamic 3D, others are Geometric 3D
    if is_2d:
        # Check if the environment name starts with "Dyn" (case insensitive)
        is_dynamic = env_name.lower().startswith('dyn')
        return "Dynamic 2D" if is_dynamic else "Geometric 2D"
    elif is_3d:
        # For 3D: TidyBot environments are dynamic, others are geometric
        is_dynamic = 'tidybot' in name_lower
        return "Dynamic 3D" if is_dynamic else "Geometric 3D"
    else:
        # Default to Geometric 2D if not specified
        return "Geometric 2D"

def generate_html_filename(env_name, category):
    """Generate a clean filename for the HTML page."""
    # Create a clean filename from environment name
    clean_name = re.sub(r'[^\w\s-]', '', env_name.lower())
    clean_name = re.sub(r'[-\s]+', '-', clean_name)
    return f"{clean_name}.html"

def convert_markdown_to_html(md_file_path):
    """Convert a markdown file to an HTML environment page."""
    # Read the markdown file
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Parse environment name
    env_name = parse_env_name_from_markdown(md_content)
    
    # Determine category
    category = categorize_environment(env_name)
    
    # Fix asset paths: change 'assets/' to '../markdowns/assets/'
    md_content = md_content.replace('](assets/', '](../markdowns/assets/')
    md_content = md_content.replace('="assets/', '="../markdowns/assets/')
    
    # Preprocess markdown to ensure tables are properly formatted
    # Tables need blank lines before and after them
    lines = md_content.split('\n')
    processed_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        # Check if this line starts a table (has pipe characters and looks like a table row)
        is_table_line = line.strip().startswith('|') and line.strip().endswith('|')
        
        if is_table_line and not in_table:
            # Starting a table - ensure blank line before
            if processed_lines and processed_lines[-1].strip():
                processed_lines.append('')
            in_table = True
        elif not is_table_line and in_table:
            # Ending a table - ensure blank line after
            in_table = False
            processed_lines.append(line)
            if line.strip() and i + 1 < len(lines):
                processed_lines.append('')
            continue
        
        processed_lines.append(line)
    
    md_content = '\n'.join(processed_lines)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    html_content = md.convert(md_content)
    
    # Generate HTML page
    html_output = HTML_TEMPLATE.format(
        title=env_name,
        category=category,
        env_name=env_name,
        content=html_content
    )
    
    # Generate output filename
    html_filename = generate_html_filename(env_name, category)
    output_path = Path('environments') / html_filename
    
    # Ensure environments directory exists
    Path('environments').mkdir(exist_ok=True)
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"Generated: {output_path} (Category: {category})")
    
    return {
        'name': env_name,
        'category': category,
        'filename': html_filename,
        'html_path': str(output_path)
    }

def scan_and_generate():
    """Scan for markdown files and generate HTML pages."""
    markdown_dir = Path('markdowns')
    
    if not markdown_dir.exists():
        print(f"Error: {markdown_dir} directory not found!")
        return []
    
    md_files = list(markdown_dir.glob('*.md'))
    
    # Filter out README.md
    md_files = [f for f in md_files if f.name.lower() != 'readme.md']
    
    if not md_files:
        print("No markdown files found in markdowns/ directory!")
        return []
    
    print(f"Found {len(md_files)} markdown file(s)")
    
    environments = []
    for md_file in md_files:
        print(f"\nProcessing: {md_file}")
        env_info = convert_markdown_to_html(md_file)
        environments.append(env_info)
    
    return environments

def generate_category_html(category_name, environments):
    """Generate HTML for a category section."""
    # Sort environments by name
    environments = sorted(environments, key=lambda x: x['name'])
    
    category_descriptions = {
        'Geometric 2D': '2D environments focused on geometric reasoning and spatial relationships.',
        'Geometric 3D': '3D environments for testing spatial reasoning in three dimensions.',
        'Dynamic 2D': '2D environments involving dynamic physical interactions and motion.',
        'Dynamic 3D': '3D environments with complex dynamics and physical interactions.'
    }
    
    html = f'''
                <div class="category">
                    <h3>{category_name}</h3>
                    <p class="category-description">{category_descriptions.get(category_name, '')}</p>
                    <div class="environment-grid">
'''
    
    for env in environments:
        html += f'''                        <a href="environments/{env['filename']}" class="environment-card">
                            <h4>{env['name']}</h4>
                            <p>Click to view details</p>
                        </a>
'''
    
    html += '''                    </div>
                </div>
'''
    
    return html

def update_index_html(environments):
    """Update index.html with the discovered environments."""
    # Group environments by category
    categories = {
        'Geometric 2D': [],
        'Geometric 3D': [],
        'Dynamic 2D': [],
        'Dynamic 3D': []
    }
    
    for env in environments:
        if env['category'] in categories:
            categories[env['category']].append(env)
    
    print("\n" + "="*60)
    print("Environment Distribution:")
    for cat, envs in categories.items():
        print(f"  {cat}: {len(envs)} environments")
    print("="*60)
    
    # Read current index.html
    index_path = Path('index.html')
    if not index_path.exists():
        print("\nWarning: index.html not found!")
        return
    
    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # Generate new benchmark section content
    benchmark_html = '''        <section id="benchmark">
            <div class="container">
                <h2>Benchmark</h2>
                <p>Our benchmark is organized into four categories of physical reasoning environments:</p>
'''
    
    # Add each category
    for category_name in ['Geometric 2D', 'Geometric 3D', 'Dynamic 2D', 'Dynamic 3D']:
        if categories[category_name]:
            benchmark_html += generate_category_html(category_name, categories[category_name])
    
    benchmark_html += '''            </div>
        </section>'''
    
    # Replace the benchmark section
    import re
    pattern = r'<section id="benchmark">.*?</section>'
    new_content = re.sub(pattern, benchmark_html, index_content, flags=re.DOTALL)
    
    # Write back to index.html
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("\n✓ Updated index.html with all environments!")

if __name__ == '__main__':
    print("PRBench Environment Page Generator")
    print("="*60)
    
    environments = scan_and_generate()
    
    if environments:
        update_index_html(environments)
        print(f"\n✓ Successfully generated {len(environments)} environment page(s)!")
    else:
        print("\n✗ No environments were generated.")

