# Environment Group Pages

The generator now creates group pages for environments that have multiple variants!

## How It Works

### Three-Level Hierarchy

1. **Category Level** (e.g., "Geometric 2D")
   - Top-level categorization of environments
   
2. **Group Level** (e.g., "ClutteredRetrieval2D")
   - Groups related environments together
   - Automatically created when multiple variants exist
   - Group page lists all variants with links
   
3. **Environment Level** (e.g., "ClutteredRetrieval2D-o1-v0")
   - Individual environment details from markdown

### Example Structure

```
Geometric 2D
├── ClutteredRetrieval2D (group page)
│   ├── ClutteredRetrieval2D-o1-v0
│   ├── ClutteredRetrieval2D-o10-v0
│   └── ClutteredRetrieval2D-o25-v0
├── Motion2D (group page)
│   ├── Motion2D-p0-v0
│   ├── Motion2D-p1-v0
│   ├── Motion2D-p2-v0
│   └── ...
└── PushPullHook2D (single environment, no group page)
    └── PushPullHook2D-v0
```

## What Gets Generated

### For Multi-Variant Environments:

1. **Individual Environment Pages** (e.g., `clutteredretrieval2d-o1-v0.html`)
   - Full environment details from markdown
   - Breadcrumb: Benchmark / Category / **Group** / Environment
   - Links back to group page

2. **Group Page** (e.g., `clutteredretrieval2d-group.html`)
   - Lists all variants of the environment
   - Shows number of variants
   - Cards link to individual environment pages
   - Breadcrumb: Benchmark / Category / Group

### For Single Environments:

- Only the individual environment page is created
- No group page needed
- Links directly from category to environment

## On the Main Page (index.html)

### Single Environments:
```
Environment Name
  └─ [Card links to environment page]
```

### Multi-Variant Environments:
```
Environment Name (3 variants) ← clickable, links to group page
  ├─ [Card for variant 1]
  ├─ [Card for variant 2]
  └─ [Card for variant 3]
```

## Files Generated

Running `python3 generate_pages.py` creates:

- `environments/*.html` - Individual environment pages (one per markdown file)
- `environments/*-group.html` - Group pages (one per base environment with multiple variants)
- `index.html` - Updated with links to both group pages and individual environments

## Naming Convention

- **Environment pages**: `{env-name}.html` (e.g., `clutteredretrieval2d-o1-v0.html`)
- **Group pages**: `{base-name}-group.html` (e.g., `clutteredretrieval2d-group.html`)

## Customization

To change the group page layout, edit the `GROUP_TEMPLATE` in `generate_pages.py`.

To change how groups are extracted from names, edit `extract_base_environment_name()` function.

