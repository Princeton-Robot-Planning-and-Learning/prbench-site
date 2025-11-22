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
                    <li><a href="../index.html#usage">Usage</a></li>
                    <li><a href="../index.html#benchmark">Environments</a></li>
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
                    <a href="{category_link}">{category}</a> / 
                    {group_breadcrumb}
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

# HTML template for category pages
CATEGORY_TEMPLATE = """<!DOCTYPE html>
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
                    <li><a href="../index.html#usage">Usage</a></li>
                    <li><a href="../index.html#benchmark">Environments</a></li>
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
                    <span>{category_name}</span>
                </div>

                <h1>{category_name}</h1>
                
                <div class="environment-content">
                    <p class="category-page-description">{category_description}</p>
                    
                    <h2>Environment Families</h2>
                    
                    <div class="env-families-list">
{families_html}
                    </div>
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

# HTML template for environment group pages
GROUP_TEMPLATE = """<!DOCTYPE html>
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
                    <li><a href="../index.html#usage">Usage</a></li>
                    <li><a href="../index.html#benchmark">Environments</a></li>
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
                    <a href="{category_link}">{category}</a> / 
                    <span>{group_name}</span>
                </div>

                <h1>{group_name}</h1>
                
                <div class="environment-content">
                    <div class="gifs-grid">
{gifs_html}
                    </div>

                    <h2>Description</h2>
                    {description_html}

                    <h2>Variants</h2>
                    <p>This environment has {num_variants} standard variant(s). Each variant has a constant number of objects. See the variant pages for detailed descriptions of observation spaces, action spaces, and rewards.</p>
                    
                    <div class="variant-list">
{variants_html}
                    </div>

                    <h2>References</h2>
                    {references_html}
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
    # For 3D: TidyBot and RBY1A environments are Dynamic 3D, others are Geometric 3D
    if is_2d:
        # Check if the environment name starts with "Dyn" (case insensitive)
        is_dynamic = env_name.lower().startswith('dyn')
        return "Dynamic 2D" if is_dynamic else "Geometric 2D"
    elif is_3d:
        # For 3D: TidyBot and RBY1A environments are dynamic, others are geometric
        is_dynamic = 'tidybot' in name_lower or 'rby1a' in name_lower
        return "Dynamic 3D" if is_dynamic else "Geometric 3D"
    else:
        # Default to Geometric 2D if not specified
        return "Geometric 2D"

def extract_base_environment_name(env_name):
    """Extract the base environment name without variant suffixes.
    
    Examples:
        ClutteredRetrieval2D-o1-v0 -> ClutteredRetrieval2D
        Motion2D-p3-v0 -> Motion2D
        TidyBot3D-ground-o3-v0 -> TidyBot3D-ground
        TidyBot3D-base_motion-o1-v0 -> TidyBot3D-base_motion
        RBY1A3D-cupboard-o8-v0 -> RBY1A3D-cupboard
        DynPushT-t1-v0 -> DynPushT
    """
    # Remove -v0, -v1, etc. version suffixes
    name = re.sub(r'-v\d+$', '', env_name)
    
    # Special handling for TidyBot environments (keep the scene type)
    if name.startswith('TidyBot3D'):
        # Pattern: TidyBot3D-{scene_type}-{variant}
        # Handles: ground, table, cupboard, base_motion, etc.
        parts = name.split('-')
        if len(parts) >= 3:
            # Keep everything except the last part if it's a variant
            last_part = parts[-1]
            if re.match(r'^[a-z]\d+$', last_part) or re.match(r'^o\d+$', last_part):
                return '-'.join(parts[:-1])  # TidyBot3D-ground, TidyBot3D-base_motion, etc.
    
    # Special handling for RBY1A3D environments (keep the scene type)
    if name.startswith('RBY1A3D'):
        # Pattern: RBY1A3D-{scene_type}-{variant}
        parts = name.split('-')
        if len(parts) >= 3:
            last_part = parts[-1]
            if re.match(r'^[a-z]\d+$', last_part) or re.match(r'^o\d+$', last_part):
                return '-'.join(parts[:-1])  # RBY1A3D-cupboard, etc.
    
    # For other environments, remove the last variant part (usually -o1, -p3, -b5, -t1, etc.)
    parts = name.split('-')
    if len(parts) >= 2:
        # Check if the last part is a variant (starts with letter followed by numbers)
        last_part = parts[-1]
        if re.match(r'^[a-z]\d+$', last_part):
            return '-'.join(parts[:-1])
    
    return name

def generate_html_filename(env_name, category):
    """Generate a clean filename for the HTML page."""
    # Create a clean filename from environment name
    clean_name = re.sub(r'[^\w\s-]', '', env_name.lower())
    clean_name = re.sub(r'[-\s]+', '-', clean_name)
    return f"{clean_name}.html"

def generate_group_filename(base_name):
    """Generate a clean filename for the group page."""
    clean_name = re.sub(r'[^\w\s-]', '', base_name.lower())
    clean_name = re.sub(r'[-\s]+', '-', clean_name)
    return f"{clean_name}-group.html"

def generate_category_filename(category_name):
    """Generate a clean filename for the category page."""
    clean_name = re.sub(r'[^\w\s-]', '', category_name.lower())
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
    
    # Extract the three GIFs before processing
    gif_pattern = r'!\[(.*?)\]\((assets/.*?\.gif)\)'
    gif_matches = re.findall(gif_pattern, md_content)
    
    # Store GIF info: [(alt_text, path), ...]
    gifs_info = []
    for alt_text, gif_path in gif_matches[:3]:  # Only take first 3 GIFs
        fixed_path = gif_path.replace('assets/', '../markdowns/assets/')
        gifs_info.append((alt_text, fixed_path))
    
    # Check if Example Demonstration is available
    has_demo_gif = False
    demo_gif_pattern = r'### Example Demonstration\s*\n!\[.*?\]\(assets/.*?\.gif\)'
    if re.search(demo_gif_pattern, md_content):
        has_demo_gif = True
    
    # Remove the GIF sections from markdown to avoid duplication
    # Remove the random action GIF line and Initial State Distribution/Example Demonstration sections
    md_content_lines = md_content.split('\n')
    filtered_lines = []
    skip_until_next_section = False
    
    for i, line in enumerate(md_content_lines):
        # Skip the first GIF (random action GIF) right after title
        if i > 0 and line.strip().startswith('![') and 'random_action_gifs' in line:
            continue
        # Skip Initial State Distribution section header and GIF
        elif line.strip() == '### Initial State Distribution':
            skip_until_next_section = True
            continue
        # Skip Example Demonstration section header and GIF (or text)
        elif line.strip() == '### Example Demonstration':
            skip_until_next_section = True
            continue
        # Stop skipping when we hit the next section
        elif skip_until_next_section and line.strip().startswith('###') and 'Initial State Distribution' not in line and 'Example Demonstration' not in line:
            skip_until_next_section = False
            filtered_lines.append(line)
        # Skip lines while in skip mode
        elif skip_until_next_section:
            continue
        else:
            filtered_lines.append(line)
    
    md_content = '\n'.join(filtered_lines)
    
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
    
    # Extract the h1 title from html_content
    title_match = re.search(r'<h1>(.*?)</h1>', html_content)
    title_html = ''
    if title_match:
        title_html = f'<h1>{title_match.group(1)}</h1>\n'
        # Remove the h1 from html_content
        html_content = re.sub(r'<h1>.*?</h1>\n?', '', html_content, count=1)
    
    # Create GIF grid HTML (similar to group pages)
    gifs_html = ''
    if gifs_info or has_demo_gif is False:
        gifs_html = '<div class="gifs-grid">\n'
        gif_labels = ['Random Actions', 'Initial State Distribution', 'Example Demonstration']
        
        # Add the GIFs we found
        for i, (alt_text, gif_path) in enumerate(gifs_info):
            label = gif_labels[i] if i < len(gif_labels) else alt_text or f'GIF {i+1}'
            gifs_html += f'''                        <div class="gif-container">
                            <h3>{label}</h3>
                            <img src="{gif_path}" alt="{label}">
                        </div>
'''
        
        # If we only have 2 GIFs and no demo GIF, add placeholder for demo
        if len(gifs_info) == 2 and not has_demo_gif:
            gifs_html += f'''                        <div class="gif-container">
                            <h3>Example Demonstration</h3>
                            <p style="padding: 60px 20px; text-align: center; color: #666;">No demonstration GIFs available</p>
                        </div>
'''
        
        gifs_html += '                    </div>\n\n'
    
    # Combine title, GIFs grid, and the rest of the content
    final_content = title_html + gifs_html + html_content
    
    # Get base name for breadcrumb
    base_name = extract_base_environment_name(env_name)
    group_filename = generate_group_filename(base_name)
    category_filename = generate_category_filename(category)
    
    # Check if this environment has a group (will be determined later, so we'll use a placeholder)
    # For now, we'll add the group link if base_name != env_name
    if base_name != env_name:
        group_breadcrumb = f'<a href="{group_filename}">{base_name}</a> / '
    else:
        group_breadcrumb = ''
    
    # Generate HTML page
    html_output = HTML_TEMPLATE.format(
        title=env_name,
        category=category,
        category_link=category_filename,
        env_name=env_name,
        group_breadcrumb=group_breadcrumb,
        content=final_content
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
        'html_path': str(output_path),
        'md_file_path': str(md_file_path)
    }

def extract_variant_description(md_file_path):
    """Extract the variant description from a markdown file."""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract variant description section
    variant_description_match = re.search(r'### Variant Description\s*\n(.*?)(?=\n### |\n##|\Z)', content, re.DOTALL)
    if variant_description_match:
        variant_description = variant_description_match.group(1).strip()
        # Remove markdown formatting and convert to plain text
        # Remove any leading/trailing whitespace and newlines
        variant_description = ' '.join(variant_description.split())
        return variant_description
    return 'View details →'

def extract_group_content(md_file_path):
    """Extract description, group description, references, and GIFs from a markdown file."""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the three GIFs
    gif_pattern = r'!\[.*?\]\((assets/.*?\.gif)\)'
    gifs = re.findall(gif_pattern, content)
    
    # Fix paths for the group page
    gifs = [gif.replace('assets/', '../markdowns/assets/') for gif in gifs]
    
    # Extract environment group description section (prioritize this for group pages)
    group_description_match = re.search(r'### Environment Group Description\s*\n(.*?)(?=\n### |\n##|\Z)', content, re.DOTALL)
    group_description = group_description_match.group(1).strip() if group_description_match else ''
    
    # Extract description section (fallback if no group description)
    description_match = re.search(r'### Description\s*\n(.*?)(?=\n### |\n##|\Z)', content, re.DOTALL)
    description = description_match.group(1).strip() if description_match else ''
    
    # Extract references section
    references_match = re.search(r'### References\s*\n(.*?)(?=\n### |\n##|\Z)', content, re.DOTALL)
    references = references_match.group(1).strip() if references_match else ''
    
    # Convert markdown to HTML
    md = markdown.Markdown()
    
    # Use group description if available, otherwise fall back to description
    if group_description:
        description_html = md.convert(group_description)
    elif description:
        description_html = md.convert(description)
    else:
        description_html = '<p>No description available.</p>'
    
    md.reset()
    references_html = md.convert(references) if references else '<p>No references available.</p>'
    
    return {
        'gifs': gifs,
        'description_html': description_html,
        'references_html': references_html
    }

def extract_object_count(variant_name):
    """Extract the number of objects from a variant name.
    
    Examples:
        ClutteredRetrieval2D-o1-v0 -> 1
        ClutteredRetrieval2D-o10-v0 -> 10
        Motion2D-p3-v0 -> 3
        ClutteredStorage2D-b15-v0 -> 15
    """
    # Look for patterns like -o1, -p3, -b15, -t1, etc.
    match = re.search(r'-([a-z])(\d+)-v\d+$', variant_name)
    if match:
        return int(match.group(2))
    return 0

def has_demonstration_gif(md_file_path):
    """Check if a markdown file has a demonstration GIF."""
    if not md_file_path or not Path(md_file_path).exists():
        return False
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if there's a demo GIF (not just the text "No demonstration GIFs available")
    demo_gif_pattern = r'### Example Demonstration\s*\n!\[.*?\]\(assets/.*?\.gif\)'
    return bool(re.search(demo_gif_pattern, content))

def select_best_variant_for_gifs(variants):
    """Select the variant with the most objects that has a demo GIF.
    
    If no variant has a demo GIF, select the one with the most objects.
    """
    # Separate variants with and without demo GIFs
    variants_with_demo = []
    variants_without_demo = []
    
    for variant in variants:
        md_path = variant.get('md_file_path')
        object_count = extract_object_count(variant['name'])
        variant_info = (variant, object_count)
        
        if has_demonstration_gif(md_path):
            variants_with_demo.append(variant_info)
        else:
            variants_without_demo.append(variant_info)
    
    # Prefer variants with demo GIFs, sorted by object count (descending)
    if variants_with_demo:
        # Sort by object count descending, return the variant with most objects
        variants_with_demo.sort(key=lambda x: x[1], reverse=True)
        return variants_with_demo[0][0]
    
    # If no demos available, use the variant with most objects
    if variants_without_demo:
        variants_without_demo.sort(key=lambda x: x[1], reverse=True)
        return variants_without_demo[0][0]
    
    # Fallback to first variant
    return variants[0] if variants else None

def create_group_page(base_name, category, variants):
    """Create an HTML page for an environment group."""
    group_filename = generate_group_filename(base_name)
    category_filename = generate_category_filename(category)
    output_path = Path('environments') / group_filename
    
    # Sort variants by name
    variants = sorted(variants, key=lambda x: x['name'])
    
    # Select the best variant for displaying GIFs (most objects with demo, or most objects without)
    best_variant = select_best_variant_for_gifs(variants)
    md_file_path = best_variant.get('md_file_path') if best_variant else None
    
    group_content = {'gifs': [], 'description_html': '', 'references_html': ''}
    if md_file_path and Path(md_file_path).exists():
        group_content = extract_group_content(md_file_path)
    
    # Generate GIF HTML
    gifs_html = ''
    gif_labels = ['Random Actions', 'Initial State Distribution', 'Example Demonstration']
    for i, gif in enumerate(group_content['gifs'][:3]):  # Only use first 3 GIFs
        label = gif_labels[i] if i < len(gif_labels) else f'GIF {i+1}'
        gifs_html += f'''                        <div class="gif-container">
                            <h3>{label}</h3>
                            <img src="{gif}" alt="{label}">
                        </div>
'''
    
    # Generate HTML for variants list
    variants_html = ''
    for variant in variants:
        variant_suffix = variant['name'].replace(base_name, '').lstrip('-')
        if not variant_suffix:
            variant_suffix = variant['name']
        
        # Extract variant description from the markdown file
        variant_md_path = variant.get('md_file_path')
        variant_desc = 'View details →'
        if variant_md_path and Path(variant_md_path).exists():
            variant_desc = extract_variant_description(variant_md_path)
        
        variants_html += f'''                        <div class="variant-card">
                            <a href="{variant['filename']}" class="variant-link">
                                <h3>{variant['name']}</h3>
                                <p class="variant-description">{variant_desc}</p>
                            </a>
                        </div>
'''
    
    # Generate the HTML
    html_output = GROUP_TEMPLATE.format(
        title=base_name,
        category=category,
        category_link=category_filename,
        group_name=base_name,
        num_variants=len(variants),
        gifs_html=gifs_html,
        description_html=group_content['description_html'],
        references_html=group_content['references_html'],
        variants_html=variants_html
    )
    
    # Write the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"  Generated group page: {output_path}")
    
    return {
        'base_name': base_name,
        'filename': group_filename,
        'category': category,
        'num_variants': len(variants)
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
    
    # Group environments by base name and create group pages
    print("\n" + "="*60)
    print("Creating environment group pages...")
    print("="*60)
    
    from collections import defaultdict
    groups = defaultdict(list)
    
    for env in environments:
        base_name = extract_base_environment_name(env['name'])
        env['base_name'] = base_name
        groups[base_name].append(env)
    
    group_pages = []
    for base_name, variants in sorted(groups.items()):
        # Create group pages for all environments (even single variants)
        num_variants = len(variants)
        variant_text = "variant" if num_variants == 1 else "variants"
        print(f"\nCreating group page for: {base_name} ({num_variants} {variant_text})")
        group_info = create_group_page(base_name, variants[0]['category'], variants)
        group_pages.append(group_info)
    
    print(f"\n✓ Created {len(group_pages)} group page(s)")
    
    # Create category pages
    print("\n" + "="*60)
    print("Creating category pages...")
    print("="*60)
    
    category_pages = create_category_pages(groups)
    
    print(f"\n✓ Created {len(category_pages)} category page(s)")
    
    return environments

def generate_category_html(category_name, environments):
    """Generate HTML for a category section with environment groups."""
    # Group environments by base name
    from collections import defaultdict
    env_groups = defaultdict(list)
    
    for env in environments:
        base_name = extract_base_environment_name(env['name'])
        env['base_name'] = base_name
        env_groups[base_name].append(env)
    
    # Sort groups by base name, and within each group sort by full name
    sorted_groups = sorted(env_groups.items())
    for base_name, group in sorted_groups:
        group.sort(key=lambda x: x['name'])
    
    category_descriptions = {
        'Geometric 2D': '2D environments focused on geometric reasoning and spatial relationships.',
        'Geometric 3D': '3D environments for testing spatial reasoning in three dimensions.',
        'Dynamic 2D': '2D environments involving dynamic physical interactions and motion.',
        'Dynamic 3D': '3D environments with complex dynamics and physical interactions.'
    }
    
    category_filename = generate_category_filename(category_name)
    
    html = f'''
                <div class="category">
                    <h3><a href="environments/{category_filename}" class="category-title-link">{category_name}</a></h3>
                    <p class="category-description">{category_descriptions.get(category_name, '')}</p>
'''
    
    # Generate HTML for each environment group
    for base_name, group in sorted_groups:
        if len(group) == 1:
            # Single environment - display as a card linking directly to it
            env = group[0]
            html += f'''                    <div class="env-group">
                        <h4 class="env-group-title">{base_name}</h4>
                        <div class="environment-grid">
                            <a href="environments/{env['filename']}" class="environment-card">
                                <h5>{env['name']}</h5>
                                <p>Click to view details</p>
                            </a>
                        </div>
                    </div>
'''
        else:
            # Multiple variants - display group title linking to group page, then show variants
            group_filename = generate_group_filename(base_name)
            html += f'''                    <div class="env-group">
                        <h4 class="env-group-title">
                            <a href="environments/{group_filename}" class="group-title-link">{base_name}</a>
                            <span class="variant-count">({len(group)} variants)</span>
                        </h4>
                        <div class="environment-grid">
'''
            for env in group:
                # Extract the variant part for display
                variant = env['name'].replace(base_name, '').lstrip('-') if base_name in env['name'] else env['name']
                if not variant:
                    variant = env['name']
                
                html += f'''                            <a href="environments/{env['filename']}" class="environment-card">
                                <h5>{variant}</h5>
                                <p>Click to view details</p>
                            </a>
'''
            html += '''                        </div>
                    </div>
'''
    
    html += '''                </div>
'''
    
    return html

def create_category_pages(groups):
    """Create pages for each category listing all environment families."""
    category_descriptions = {
        'Geometric 2D': '2D environments focused on geometric reasoning and spatial relationships.',
        'Geometric 3D': '3D environments for testing spatial reasoning in three dimensions.',
        'Dynamic 2D': '2D environments involving dynamic physical interactions and motion.',
        'Dynamic 3D': '3D environments with complex dynamics and physical interactions.'
    }
    
    # Group by category
    from collections import defaultdict
    categories = defaultdict(list)
    
    for base_name, variants in groups.items():
        if variants:
            category = variants[0]['category']
            categories[category].append({
                'base_name': base_name,
                'num_variants': len(variants),
                'group_filename': generate_group_filename(base_name)
            })
    
    category_pages = []
    
    for category_name in ['Geometric 2D', 'Geometric 3D', 'Dynamic 2D', 'Dynamic 3D']:
        if category_name not in categories:
            continue
        
        families = sorted(categories[category_name], key=lambda x: x['base_name'])
        
        print(f"\nCreating category page: {category_name} ({len(families)} families)")
        
        # Generate HTML for families list
        families_html = ''
        for family in families:
            if family['num_variants'] > 1:
                # Multiple variants - link to group page
                families_html += f'''                        <div class="family-card">
                            <a href="{family['group_filename']}" class="family-link">
                                <h3>{family['base_name']}</h3>
                                <p class="family-meta">{family['num_variants']} variants</p>
                            </a>
                        </div>
'''
            else:
                # Single variant - could link to group page still (which exists) or directly
                families_html += f'''                        <div class="family-card">
                            <a href="{family['group_filename']}" class="family-link">
                                <h3>{family['base_name']}</h3>
                                <p class="family-meta">1 variant</p>
                            </a>
                        </div>
'''
        
        # Generate category page
        category_filename = generate_category_filename(category_name)
        output_path = Path('environments') / category_filename
        
        html_output = CATEGORY_TEMPLATE.format(
            title=category_name,
            category_name=category_name,
            category_description=category_descriptions.get(category_name, ''),
            families_html=families_html
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_output)
        
        print(f"  Generated: {output_path}")
        
        category_pages.append({
            'name': category_name,
            'filename': category_filename,
            'num_families': len(families)
        })
    
    return category_pages

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

