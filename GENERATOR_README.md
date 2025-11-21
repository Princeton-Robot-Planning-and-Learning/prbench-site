# Environment Page Generator

This tool automatically generates HTML pages from markdown files describing each environment.

## Setup

1. Install the required Python package:
```bash
pip install markdown
```

## Usage

1. Place your environment markdown files (e.g., `example.md`) in the root directory
2. Run the generator:
```bash
python3 generate_pages.py
```

3. The script will:
   - Find all `.md` files (except `README.md`)
   - Parse the environment name from the first heading
   - Automatically categorize each environment based on its name
   - Generate an HTML page in the `environments/` directory
   - Display a summary of what was generated

## Markdown Format

Your markdown files should follow this structure:

```markdown
# prbench/EnvironmentName

### Description
Environment description here...

### Observation Space
Description and tables...

| **Index** | **Object** | **Feature** |
| --- | --- | --- |
| 0 | robot | x |

### Action Space
| **Index** | **Feature** | **Description** | **Min** | **Max** |
| --- | --- | --- | --- | --- |
| 0 | dx | Description | -0.050 | 0.050 |

### Rewards
Reward description...

### References
References...
```

## Categorization Rules

The script automatically categorizes environments based on their names:

- **Geometric 2D**: Contains "2d" but no dynamic keywords
- **Geometric 3D**: Contains "3d" but no dynamic keywords  
- **Dynamic 2D**: Contains "2d" AND dynamic keywords (stack, push, throw, fall, slide, dynamic, collision)
- **Dynamic 3D**: Contains "3d" AND dynamic keywords

## Output

Generated files will be named based on the environment name (lowercased, with special characters removed).

Example: `ClutteredRetrieval2D-o1-v0` → `clutteredretrieval2d-o1-v0.html`

## Styling

The generated pages include:
- Styled markdown headings (h1, h2, h3)
- Beautiful table formatting with hover effects
- Responsive image display
- Code block styling
- Navigation breadcrumbs
- Back to benchmark link

All styling is in `environments/environment.css`.

