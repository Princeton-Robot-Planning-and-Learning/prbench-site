#!/usr/bin/env python3
"""Generate environment HTML pages from markdown files."""

import csv
import re
import shutil
from collections import defaultdict
from pathlib import Path

import markdown
from PIL import Image

CATEGORY_DESCRIPTIONS = {
    'Geometric 2D': '2D environments focused on geometric reasoning and spatial relationships.',
    'Geometric 3D': '3D environments for testing spatial reasoning in three dimensions.',
    'Dynamic 2D': '2D environments involving dynamic physical interactions and motion.',
    'Dynamic 3D': '3D environments with complex dynamics and physical interactions.'
}

NAV_ITEMS = [
    ('about', 'About'),
    ('usage', 'Usage'),
    ('benchmark', 'Environments'),
    ('results', 'Results'),
    ('real-robots', 'Real Robots'),
    ('acknowledgements', 'Acknowledgements'),
]

FOOTER_TEXT = '&copy; 2025 PRBench. All rights reserved.'
DRAFT_BANNER_TEXT = 'EARLY DRAFT: DO NOT DISTRIBUTE'


def generate_header(prefix='', title='PRBench'):
    """Generate the site header HTML.

    prefix: path prefix for links ('' for index.html, '../' for depth=1, etc.)
    title: the h1 title text
    """
    if prefix:
        nav_links = '\n'.join(
            f'                    <li><a href="{prefix}index.html#{id}">{label}</a></li>'
            for id, label in NAV_ITEMS
        )
        title_html = f'<a href="{prefix}index.html" style="color: white; text-decoration: none;">{title}</a>'
    else:
        nav_links = '\n'.join(
            f'                    <li><a href="#{id}">{label}</a></li>'
            for id, label in NAV_ITEMS
        )
        title_html = title

    return f'''    <div class="draft-banner">{DRAFT_BANNER_TEXT}</div>
    <header>
        <nav>
            <div class="container">
                <h1>{title_html}</h1>
                <ul class="nav-links">
{nav_links}
                </ul>
            </div>
        </nav>
    </header>'''


def generate_footer():
    """Generate the site footer HTML."""
    return f'''    <footer>
        <div class="container">
            <p>{FOOTER_TEXT}</p>
        </div>
    </footer>'''


def base_template(title, breadcrumb_html, content_html, depth=1):
    """Generate a complete HTML page with consistent header/footer.

    depth=1: environments/*.html (category pages)
    depth=2: environments/<group>/*.html (group and variant pages)
    """
    prefix = '../' * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | PRBench</title>
    <link rel="stylesheet" href="{prefix}styles.css">
    <link rel="stylesheet" href="{prefix}environments/environment.css">
</head>
<body>
{generate_header(prefix, 'PRBench')}
    <main>
        <section class="environment-detail">
            <div class="container">
                <div class="breadcrumb">{breadcrumb_html}</div>
{content_html}
                <div class="back-link">
                    <a href="{prefix}index.html#benchmark">← Back to Benchmark</a>
                </div>
            </div>
        </section>
    </main>
{generate_footer()}
</body>
</html>
"""


def slugify(name):
    """Convert a name to a URL-safe slug."""
    return re.sub(r'[-\s]+', '-', re.sub(r'[^\w\s-]', '', name.lower()))


def extract_base_name(env_name):
    """Extract base environment name without variant suffixes."""
    name = re.sub(r'-v\d+$', '', env_name)

    for prefix in ('TidyBot3D', 'RBY1A3D'):
        if name.startswith(prefix):
            parts = name.split('-')
            if len(parts) >= 3 and re.match(r'^[a-z]\d+$', parts[-1]):
                return '-'.join(parts[:-1])

    parts = name.split('-')
    if len(parts) >= 2 and re.match(r'^[a-z]\d+$', parts[-1]):
        return '-'.join(parts[:-1])
    return name


def categorize_environment(env_name):
    """Determine category based on environment name."""
    name_lower = env_name.lower()
    is_3d = '3d' in name_lower

    if is_3d:
        is_dynamic = 'tidybot' in name_lower or 'rby1a' in name_lower
        return "Dynamic 3D" if is_dynamic else "Geometric 3D"
    else:
        is_dynamic = name_lower.startswith('dyn')
        return "Dynamic 2D" if is_dynamic else "Geometric 2D"


def extract_first_frame_as_png(gif_path, png_path):
    """Extract the first frame of a GIF and save as PNG."""
    try:
        with Image.open(gif_path) as img:
            img.seek(0)
            frame = img.convert('RGBA')
            frame.save(png_path, 'PNG')
            return True
    except Exception as e:
        print(f"  Warning: Could not extract PNG from {gif_path}: {e}")
        return False


def generate_gif_grid_html(gifs, labels=None):
    """Generate HTML for a grid of GIFs."""
    if not gifs:
        return ''
    labels = labels or ['Random Actions', 'Initial State Distribution', 'Example Demonstration']
    items = '\n'.join(
        f'                        <div class="gif-container">\n'
        f'                            <h3>{labels[i] if i < len(labels) else f"GIF {i+1}"}</h3>\n'
        f'                            <img src="{gif}" alt="{labels[i] if i < len(labels) else ""}">\n'
        f'                        </div>'
        for i, gif in enumerate(gifs[:3])
    )
    return f'                    <div class="gifs-grid">\n{items}\n                    </div>\n\n'


def get_hero_gif_path(group_name, assets_dir):
    """Get the hero GIF path for a group from group_gifs directory."""
    gif_path = assets_dir / 'group_gifs' / f'{group_name}.gif'
    if gif_path.exists():
        return gif_path
    return None


def extract_gifs_from_markdown(content, depth=2):
    """Extract GIF paths from markdown content."""
    prefix = '../' * depth
    gifs = []
    for match in re.findall(r'!\[.*?\]\((assets/.*?\.gif)\)', content):
        gifs.append(match.replace('assets/', f'{prefix}prpl-mono/prbench/docs/envs/assets/'))
    return gifs[:3]


def extract_section(content, section_name):
    """Extract a section's content from markdown using ## headers."""
    match = re.search(rf'^## {section_name}\s*\n(.*?)(?=\n## |\Z)', content, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ''


def has_demo_gif(content):
    """Check if content has a demonstration GIF."""
    return bool(re.search(r'## Example Demonstration\s*\n!\[.*?\]\(assets/.*?\.gif\)', content))


def parse_group_file(md_path, assets_dir):
    """Parse a group markdown file and return structured data."""
    content = md_path.read_text(encoding='utf-8')
    name_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    group_name = name_match.group(1).strip() if name_match else "Unknown"

    hero_gif = get_hero_gif_path(group_name, assets_dir)

    return {
        'name': group_name,
        'content': content,
        'hero_gif': hero_gif,
        'description': extract_section(content, 'Description'),
        'references': extract_section(content, 'References'),
        'action_space': extract_section(content, 'Action Space'),
        'rewards': extract_section(content, 'Rewards'),
        'has_demo': hero_gif is not None,
        'md_path': md_path,
    }


def parse_variant_file(md_path, group_name):
    """Parse a variant markdown file and return structured data."""
    content = md_path.read_text(encoding='utf-8')
    name_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    variant_name = name_match.group(1).strip() if name_match else "Unknown"

    return {
        'name': variant_name,
        'content': content,
        'gifs': extract_gifs_from_markdown(content, depth=2),
        'description': extract_section(content, 'Description'),
        'usage': extract_section(content, 'Usage'),
        'observation_space': extract_section(content, 'Observation Space'),
        'has_demo': has_demo_gif(content),
        'md_path': md_path,
        'group_name': group_name,
    }


def filter_markdown_for_html(content, depth=2):
    """Remove GIF sections, fix paths, and ensure tables have blank lines."""
    lines = content.split('\n')
    filtered = []
    skip = False

    for line in lines:
        if 'random_action_gifs' in line:
            continue
        if line.strip() in ('## Initial State Distribution', '## Example Demonstration'):
            skip = True
            continue
        if skip and line.strip().startswith('## '):
            skip = False
        if skip:
            continue
        filtered.append(line)

    processed = []
    in_table = False
    for line in filtered:
        is_table_line = line.strip().startswith('|') and line.strip().endswith('|')
        if is_table_line and not in_table:
            if processed and processed[-1].strip():
                processed.append('')
            in_table = True
        elif not is_table_line and in_table:
            in_table = False
            if line.strip():
                processed.append('')
        processed.append(line)

    prefix = '../' * depth
    result = '\n'.join(processed)
    result = result.replace('](assets/', f']({prefix}prpl-mono/prbench/docs/envs/assets/')
    result = result.replace('="assets/', f'="{prefix}prpl-mono/prbench/docs/envs/assets/')
    return result


def convert_markdown_to_html(md_content):
    """Convert markdown content to HTML."""
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    return md.convert(md_content)


def create_environment_page(variant_data, group_data, category):
    """Create an HTML page for a single environment variant."""
    prefix = '../../'
    cat_slug = slugify(category)
    group_name = variant_data['group_name']
    group_slug = slugify(group_name)

    breadcrumb = (f'<a href="{prefix}index.html#benchmark">Benchmark</a> / '
                  f'<a href="{prefix}environments/{cat_slug}.html">{category}</a> / '
                  f'<a href="{prefix}environments/{group_slug}/index.html">{group_name}</a> / '
                  f'<span>{variant_data["name"]}</span>')

    filtered = filter_markdown_for_html(variant_data['content'], depth=2)
    html_content = convert_markdown_to_html(filtered)

    title_match = re.search(r'<h1>(.*?)</h1>', html_content)
    title_html = f'<h1>{title_match.group(1)}</h1>\n' if title_match else ''
    html_content = re.sub(r'<h1>.*?</h1>\n?', '', html_content, count=1)

    content = f'''
                <div class="environment-content">
                    {title_html}{generate_gif_grid_html(variant_data['gifs'])}{html_content}
                </div>
'''
    return base_template(variant_data['name'], breadcrumb, content, depth=2)


def generate_hero_gif_html(hero_gif_url):
    """Generate HTML for the hero GIF display."""
    if not hero_gif_url:
        return ''
    return f'''                    <div class="hero-gif">
                        <img src="{hero_gif_url}" alt="Environment demonstration">
                    </div>

'''


def create_group_page(group_data, category, variants):
    """Create an HTML page for an environment group (index.html in group folder)."""
    prefix = '../../'
    cat_slug = slugify(category)
    group_name = group_data['name']

    breadcrumb = (f'<a href="{prefix}index.html#benchmark">Benchmark</a> / '
                  f'<a href="{prefix}environments/{cat_slug}.html">{category}</a> / '
                  f'<span>{group_name}</span>')

    desc = group_data.get('description', '')
    desc_html = convert_markdown_to_html(desc) if desc else '<p>No description available.</p>'
    refs = group_data.get('references', '')
    refs_html = convert_markdown_to_html(refs) if refs else '<p>No references available.</p>'

    hero_gif_url = group_data.get('hero_gif_url', '')
    hero_html = generate_hero_gif_html(hero_gif_url)

    variants_html = '\n'.join(
        f'''                        <div class="variant-card">
                            <a href="{slugify(v['name'])}.html" class="variant-link">
                                <h3>{v['name']}</h3>
                                <p class="variant-description">{v.get('description', 'View details →')[:100]}</p>
                            </a>
                        </div>'''
        for v in sorted(variants, key=lambda x: x['name'])
    )

    content = f'''
                <h1>{group_name}</h1>

                <div class="environment-content">
{hero_html}                    <h2>Description</h2>
                    {desc_html}

                    <h2>Variants</h2>
                    <p>This environment has {len(variants)} variant(s).</p>

                    <div class="variant-list">
{variants_html}
                    </div>

                    <h2>References</h2>
                    {refs_html}
                </div>
'''
    return base_template(group_name, breadcrumb, content, depth=2)


def create_category_page(category_name, families):
    """Create an HTML page for a category."""
    prefix = '../'
    breadcrumb = f'<a href="{prefix}index.html#benchmark">Benchmark</a> / <span>{category_name}</span>'

    families_html = '\n'.join(
        f'''                        <div class="family-card">
                            <a href="{slugify(f['base_name'])}/index.html" class="family-link">
                                <h3>{f['base_name']}</h3>
                                <p class="family-meta">{f['count']} variant{"s" if f['count'] != 1 else ""}</p>
                            </a>
                        </div>'''
        for f in sorted(families, key=lambda x: x['base_name'])
    )

    content = f'''
                <h1>{category_name}</h1>

                <div class="environment-content">
                    <p class="category-page-description">{CATEGORY_DESCRIPTIONS.get(category_name, '')}</p>

                    <h2>Environment Families</h2>

                    <div class="env-families-list">
{families_html}
                    </div>
                </div>
'''
    return base_template(category_name, breadcrumb, content, depth=1)


def generate_results_table_html(groups):
    """Generate the results table HTML from CSV."""
    csv_path = Path('data/unified_table.csv')
    if not csv_path.exists():
        print("Warning: data/unified_table.csv not found!")
        return None

    data = defaultdict(lambda: defaultdict(dict))
    with open(csv_path, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            data[row['method']][row['env']][row['metric']] = row['value']

    methods = [
        ('RL-PPO', 'success_rate_mean', 'success_rate_std', 'RL-PPO'),
        ('RL-SAC', 'success_rate_mean', 'success_rate_std', 'RL-SAC'),
        ('ImitationLearning-DiffusionPolicy', 'success rate_mean', 'success rate_std', 'Diffusion Policy'),
        ('LLMPlanning', 'solve_rate', 'solve_rate_std', 'LLM Planning'),
        ('VLMPlanning', 'solve_rate', 'solve_rate_std', 'VLM Planning'),
        ('BilevelPlanning', 'success_mean', 'success_std', 'Bilevel Planning'),
    ]

    envs = sorted(set(env for m, *_ in methods for env in data[m]))
    header = ''.join(f'                                <th>{m[3]}</th>\n' for m in methods)

    # Build a map from env name to its group
    env_to_group = {}
    for group_name, group_info in groups.items():
        for v in group_info['variants']:
            env_to_group[v['name']] = group_name

    rows = []
    for env in envs:
        group_slug = slugify(env_to_group.get(env, extract_base_name(env)))
        env_slug = slugify(env)
        link = f'environments/{group_slug}/{env_slug}.html'
        cells = [f'                                <td><a href="{link}">{env}</a></td>']
        for method, mean_key, std_key, _ in methods:
            env_data = data[method].get(env, {})
            try:
                mean, std = float(env_data.get(mean_key, '')), float(env_data.get(std_key, ''))
                cells.append(f'                                <td>{mean:.3f} ± {std:.3f}</td>')
            except (ValueError, TypeError):
                cells.append('                                <td>-</td>')
        rows.append('                            <tr>\n' + '\n'.join(cells) + '\n                            </tr>')

    return f'''        <section id="results">
            <div class="container">
                <h2>Very Preliminary Results</h2>
                <p>Success rates: mean ± std across 5 seeds and 50 episodes per seed.</p>

                <div class="results-table-wrapper">
                    <table class="results-table">
                        <thead>
                            <tr>
                                <th>Environment</th>
{header}                            </tr>
                        </thead>
                        <tbody>
{chr(10).join(rows)}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>'''


def generate_hero_section_html(groups):
    """Generate the hero section HTML with GIF grid for index.html."""
    items = []
    for group_name in sorted(groups.keys()):
        group_info = groups[group_name]
        group_data = group_info['data']
        if not group_data.get('hero_gif'):
            continue
        slug = slugify(group_name)
        gif_path = f'prpl-mono/prbench/docs/envs/assets/group_gifs/{group_name}.gif'
        png_path = f'environments/thumbnails/{group_name}.png'
        items.append(
            f'                        <a href="environments/{slug}/index.html" class="demo-gif-item" '
            f'data-gif="{gif_path}" data-static="{png_path}">\n'
            f'                            <img src="{png_path}" alt="{group_name} Demo">\n'
            f'                            <span class="demo-label">{group_name}</span>\n'
            f'                        </a>'
        )

    if not items:
        return ''

    return f'''        <section id="hero">
            <div class="container">
                <p class="hover-instruction">Hover over the environments below to see them in action</p>
                <div class="demo-showcase">
                    <div class="demo-gif-grid">
{chr(10).join(items)}
                    </div>
                </div>
            </div>
        </section>'''


def generate_index_category_html(category_name, groups):
    """Generate HTML for a category card in index.html."""
    items = []
    for base_name, variants in sorted(groups.items()):
        count = len(variants)
        link = f"environments/{slugify(base_name)}/index.html"
        items.append(f'                            <li><a href="{link}">{base_name}</a> '
                     f'<span class="env-count">{count} variant{"s" if count != 1 else ""}</span></li>')

    return f'''
                    <div class="env-category-card">
                        <h3><a href="environments/{slugify(category_name)}.html">{category_name}</a></h3>
                        <p class="category-desc">{CATEGORY_DESCRIPTIONS.get(category_name, '')}</p>
                        <ul class="env-list">
{chr(10).join(items)}
                        </ul>
                    </div>
'''


def load_whitelist(path):
    """Load environment whitelist from file."""
    whitelist_path = Path(path)
    if not whitelist_path.exists():
        return None
    return set(line.strip() for line in whitelist_path.read_text().splitlines() if line.strip())


def main():
    print("PRBench Environment Page Generator")
    print("=" * 60)

    md_dir = Path('prpl-mono/prbench/docs/envs')
    assets_dir = md_dir / 'assets'
    if not md_dir.exists():
        print("Error: prpl-mono/prbench/docs/envs/ directory not found!")
        return

    # Load whitelist
    whitelist = load_whitelist('env_whitelist.txt')
    if whitelist:
        print(f"Loaded whitelist with {len(whitelist)} environments")
    else:
        print("No whitelist found, including all environments")

    # Parse group files from root of envs directory
    group_files = [f for f in md_dir.glob('*.md') if f.name.lower() != 'readme.md']
    print(f"Found {len(group_files)} group files")

    groups = {}
    for group_file in group_files:
        group_data = parse_group_file(group_file, assets_dir)
        group_name = group_data['name']
        # Skip groups not in whitelist
        if whitelist and group_name not in whitelist:
            continue
        group_data['category'] = categorize_environment(group_name)
        groups[group_name] = {
            'data': group_data,
            'variants': []
        }

    print(f"Including {len(groups)} groups (after whitelist filtering)")

    # Parse variant files from variants subdirectories
    variants_dir = md_dir / 'variants'
    variant_count = 0
    for group_name in groups:
        group_variant_dir = variants_dir / group_name
        if group_variant_dir.exists():
            for variant_file in group_variant_dir.glob('*.md'):
                variant_data = parse_variant_file(variant_file, group_name)
                variant_data['category'] = groups[group_name]['data']['category']
                groups[group_name]['variants'].append(variant_data)
                variant_count += 1

    print(f"Found {variant_count} variant files across {len(groups)} groups")

    # Build categories structure
    categories = defaultdict(lambda: defaultdict(list))
    for group_name, group_info in groups.items():
        category = group_info['data']['category']
        categories[category][group_name] = group_info['variants']

    out_dir = Path('environments')

    # Clean up old flat HTML files (but keep environment.css and subdirectories we'll create)
    print("\nCleaning up old files...")
    for old_file in out_dir.glob('*.html'):
        old_file.unlink()
    for old_dir in out_dir.iterdir():
        if old_dir.is_dir():
            shutil.rmtree(old_dir)

    # Generate static PNGs from hero GIFs
    print("\nGenerating static thumbnails from GIFs...")
    thumbnails_dir = out_dir / 'thumbnails'
    thumbnails_dir.mkdir(parents=True, exist_ok=True)
    png_count = 0
    for group_name, group_info in groups.items():
        group_data = group_info['data']
        hero_gif = group_data.get('hero_gif')
        if hero_gif and hero_gif.exists():
            png_path = thumbnails_dir / f'{group_name}.png'
            if extract_first_frame_as_png(hero_gif, png_path):
                png_count += 1
            # Set URLs for use in templates (relative to group page at depth=2)
            group_data['hero_gif_url'] = f'../../prpl-mono/prbench/docs/envs/assets/group_gifs/{group_name}.gif'
            group_data['thumbnail_url'] = f'../thumbnails/{group_name}.png'
        else:
            group_data['hero_gif_url'] = ''
            group_data['thumbnail_url'] = ''
    print(f"  Generated {png_count} PNG thumbnails")

    # Generate group directories with variant pages and index.html
    print("\nGenerating environment pages...")
    for group_name, group_info in groups.items():
        group_data = group_info['data']
        variants = group_info['variants']
        category = group_data['category']

        group_dir = out_dir / slugify(group_name)
        group_dir.mkdir(parents=True, exist_ok=True)

        # Generate variant pages
        for variant in variants:
            html = create_environment_page(variant, group_data, category)
            (group_dir / f"{slugify(variant['name'])}.html").write_text(html, encoding='utf-8')

        # Generate group index page
        html = create_group_page(group_data, category, variants)
        (group_dir / 'index.html').write_text(html, encoding='utf-8')

    print(f"  Generated {variant_count} variant pages in {len(groups)} group directories")

    # Generate category pages
    print("\nGenerating category pages...")
    for cat_name in ['Geometric 2D', 'Geometric 3D', 'Dynamic 2D', 'Dynamic 3D']:
        if cat_name in categories:
            families = [{'base_name': bn, 'count': len(vs)} for bn, vs in categories[cat_name].items()]
            html = create_category_page(cat_name, families)
            (out_dir / f"{slugify(cat_name)}.html").write_text(html, encoding='utf-8')
    print(f"  Generated {len(categories)} category pages")

    # Generate index.html from template
    print("\nGenerating index.html from template...")
    template_path = Path('index_template.html')
    index_path = Path('index.html')
    if template_path.exists():
        content = template_path.read_text(encoding='utf-8')

        # Replace header and footer
        content = content.replace('{{HEADER}}', generate_header(
            prefix='',
            title='PRBench: A Physical Reasoning Benchmark for Robotics'
        ))
        content = content.replace('{{FOOTER}}', generate_footer())

        # Replace hero section
        hero_html = generate_hero_section_html(groups)
        content = content.replace('{{HERO_SECTION}}', hero_html)

        benchmark_html = '''        <section id="benchmark">
            <div class="container">
                <h2>Environments</h2>
                <p>PRBench environments are organized into four categories.</p>

                <div class="env-categories-grid">
'''
        for cat_name in ['Geometric 2D', 'Geometric 3D', 'Dynamic 2D', 'Dynamic 3D']:
            if cat_name in categories:
                benchmark_html += generate_index_category_html(cat_name, categories[cat_name])
        benchmark_html += '''                </div>
            </div>
        </section>'''

        content = content.replace('{{BENCHMARK_SECTION}}', benchmark_html)

        results_html = generate_results_table_html(groups)
        if results_html:
            content = content.replace('{{RESULTS_SECTION}}', results_html)

        index_path.write_text(content, encoding='utf-8')
        print("  Generated index.html")
    else:
        print("  Warning: index_template.html not found!")

    print("\n" + "=" * 60)
    print("Summary:")
    for cat, cat_groups in categories.items():
        print(f"  {cat}: {sum(len(v) for v in cat_groups.values())} environments in {len(cat_groups)} families")
    print("=" * 60)
    print(f"\n✓ Generated {variant_count} pages successfully!")


if __name__ == '__main__':
    main()
