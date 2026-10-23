# PrismTabs website

Marketing site and manual for [PrismTabs](https://github.com/prismtabs/prismtabs), a JetBrains
plugin. Static HTML/CSS, no build step, no external dependencies.

- `index.html` — landing page
- `docs.html` — the manual
- `licence.html` — the MIT licence and data statement, served at `/licence`; keep the licence text identical to `LICENSE` in the [plugin repository](https://github.com/prismtabs/prismtabs)
- `assets/` — shared stylesheet and favicon

## Previewing locally

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Deploying

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, …) — there's nothing to build,
just serve the files as-is.
