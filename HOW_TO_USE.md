# PRBench Website - How to Use

## Quick Start

1. **Generate all environment pages from markdown files:**
   ```bash
   python3 generate_pages.py
   ```

   This will:
   - Read all `.md` files from `markdowns/` directory
   - Generate HTML pages in `environments/` directory
   - Automatically update `index.html` with all environments
   - Categorize environments into Geometric/Dynamic 2D/3D

2. **Preview categorization (optional):**
   ```bash
   python3 test_categorization.py
   ```
   
   This shows you how each environment will be categorized without generating files.

3. **View the website locally:**
   - Open `index.html` in your browser, or
   - Use a local server:
     ```bash
     python3 -m http.server 8000
     ```
     Then visit http://localhost:8000

## File Structure

```
prbench-website/
├── index.html              # Main page with all categories
├── styles.css              # Main stylesheet
├── generate_pages.py       # Script to generate environment pages
├── test_categorization.py  # Preview categorization
├── requirements.txt        # Python dependencies
├── markdowns/              # Source markdown files
│   ├── assets/            # Images and GIFs
│   └── *.md               # Environment descriptions
└── environments/           # Generated HTML pages
    ├── environment.css    # Environment page styling
    └── *.html            # Individual environment pages (auto-generated)
```

## Adding New Environments

1. Create a new `.md` file in `markdowns/` directory
2. Follow the format:
   ```markdown
   # prbench/EnvironmentName-v0
   ![random action GIF](assets/random_action_gifs/env.gif)
   
   ### Description
   ...
   
   ### Observation Space
   ...
   
   ### Action Space
   ...
   ```
3. Run `python3 generate_pages.py`
4. The environment will automatically appear on the website!

## Deployment to GitHub Pages

1. Create a repository named `robot-physical-reasoning-benchmark.github.io`
2. Push all files:
   ```bash
   git add .
   git commit -m "Update website"
   git push
   ```
3. The site will be live at `https://robot-physical-reasoning-benchmark.github.io`

## Customization

### Changing Colors
Edit `styles.css` to change the color scheme. Main colors:
- Header: `#2c3e50` (dark blue)
- Accent: `#667eea` (purple)
- Gradient: `#667eea` to `#764ba2`

### Changing Category Descriptions
Edit the `category_descriptions` dictionary in `generate_pages.py`

### Changing Categorization Logic
Edit the `categorize_environment()` function in `generate_pages.py`

## Troubleshooting

**Problem: Tables not rendering properly**
- Make sure you ran the latest version of `generate_pages.py`
- The script adds blank lines around tables for proper markdown parsing

**Problem: Images not showing**
- Check that images are in `markdowns/assets/`
- The script automatically fixes paths to `../markdowns/assets/`

**Problem: Environment in wrong category**
- Check the categorization logic in `generate_pages.py`
- Run `test_categorization.py` to preview categories
- Adjust the `dynamic_keywords` or `geometric_keywords` lists

## Notes

- Don't manually edit generated HTML files in `environments/` - they will be overwritten
- Always edit the markdown source files in `markdowns/` instead
- Run `generate_pages.py` after any changes to markdown files
- The script automatically updates `index.html` with all environments

