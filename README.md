# PrismTabs website

The site for [PrismTabs](https://github.com/prismtabs/prismtabs) at <https://prismtabs.com>: a
landing page, the user manual and the licence. Static HTML and CSS with one small script for the
manual's table of contents. There is no build step and no third-party requests; the only font,
Sora, is served from `assets/fonts/`.

| Path | Contents |
| --- | --- |
| `index.html` | Landing page |
| `docs.html` | The manual, published at `/docs` |
| `licence.html` | The MIT licence and data statement, published at `/licence` |
| `assets/` | Stylesheet, `toc.js`, logo, favicon, screenshots and the font |

## Preview locally

```bash
python3 -m http.server 8080
```

Open <http://localhost:8080>.

## Keep in step with the plugin

- **Licence:** the text in `licence.html` must match `LICENSE` in the
  [plugin repository](https://github.com/prismtabs/prismtabs).
- **Manual:** `docs.html` describes the released plugin. Update it in the same change as a user-visible
  plugin change, and keep the wording consistent with the plugin's
  [naming guide](https://github.com/prismtabs/prismtabs/blob/master/docs/naming-and-terminology.md).
- **Screenshots:** `assets/` has a dark and a light variant of each; replace both together.

## Deploy

Serve the files as they are from any static host; there is nothing to build.
