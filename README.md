# PRBench Website

This is the static website for PRBench: A Physical Reasoning Benchmark for Robotics, hosted on GitHub Pages.

## GitHub Pages Setup

To host this site on GitHub Pages:

1. Create a repository named `robot-physical-reasoning-benchmark.github.io`
2. Push this code to the repository
3. Go to repository Settings → Pages
4. Under "Source", select the branch (usually `main` or `master`)
5. Save the settings
6. Your site will be available at `https://robot-physical-reasoning-benchmark.github.io`

## Local Development

To view the site locally, simply open `index.html` in your web browser, or use a local server:

```bash
# Using Python 3
python -m http.server 8000

# Using Python 2
python -m SimpleHTTPServer 8000

# Using Node.js (requires http-server package)
npx http-server
```

Then navigate to `http://localhost:8000` in your browser.

## Structure

- `index.html` - Main HTML file
- `styles.css` - Stylesheet
- `README.md` - This file

## Customization

Feel free to modify the content, styling, and structure as needed. The site uses vanilla HTML/CSS for simplicity and maximum compatibility.

