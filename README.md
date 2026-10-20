# josh-archer.github.io

The personal website and open-source portfolio of Josh Archer, hosted on GitHub Pages.

- **Live site:** [https://josh-archer.github.io](https://josh-archer.github.io)
- **GitHub profile:** [https://github.com/Josh-Archer](https://github.com/Josh-Archer)

## Overview

The site includes:
- Home page with about, projects, and contact sections.
- Responsive, accessible static layout styled via `style.css`.
- Curated list of public open-source projects on GitHub.

## Local development

The site is built with plain static HTML and CSS without a build step. You can view it locally by opening `index.html` in a web browser or by running a local HTTP server:

```bash
python3 -m http.server
```

Then open `http://localhost:8000` in your browser.

## Testing and validation

Run the test suite and HTML validator:

```bash
python3 -m unittest discover tests/
npx html-validate "**/*.html"
```

## Contact

Contact information is available via the GitHub profile: [https://github.com/Josh-Archer](https://github.com/Josh-Archer).
