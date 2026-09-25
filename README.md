# PrismTabs website

Marketing site and manual for [PrismTabs](https://github.com/prismtabs/prismtabs), a JetBrains
plugin. Static HTML/CSS, no build step, no external dependencies.

- `index.html` — landing page
- `docs.html` — the manual
- `eula.html` — the canonical End-User Licence Agreement, served at `/eula`
- `assets/` — shared stylesheet and favicon
- `tools/` — the EULA sync check and its git hook

## Previewing locally

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Deploying

Any static host works (GitHub Pages, Netlify, Cloudflare Pages, …) — there's nothing to build,
just serve the files as-is.

## Keeping the EULA in sync

`eula.html` in this repository, published at `prismtabs.com/eula`, is the canonical End-User
Licence Agreement. The [plugin repository](https://github.com/prismtabs/prismtabs) keeps a mirror
at `docs/EULA.md` so the licence text travels with the code. Edit `eula.html` first, then update
that mirror to match. A legal document that silently drifts between the two is worse than one that
only lives in one place, so the prose is checked rather than trusted:

```bash
tools/check-eula-sync.py
```

It compares the two word for word, ignoring formatting, and prints a diff of the offending
sentences when they diverge. The mirror defaults to `../prismtabs/docs/EULA.md` — override it with
`--mirror` or by setting `PRISMTABS_EULA`. Page furniture that was never part of the Agreement is
excluded: the nav, the table of contents, any element marked `data-site-only`, and HTML comments
in the mirror.

To have it run automatically before every commit:

```bash
git config core.hooksPath tools/git-hooks
```

The hook is advisory: because the mirror lives in a separate repository and cannot be updated in
the same commit, it prints a reminder when `eula.html` and `docs/EULA.md` disagree but never
blocks. CI is the enforcing net.

Per-machine setup for the local hook (macOS / Windows): see `docs/eula-sync-setup.md` in the
[plugin repository](https://github.com/prismtabs/prismtabs).

### In CI

Two workflows run the same check, one in each repository, because drift can start on either side
and an edit on one side produces no commit — and so no build — on the other:

| Workflow | Fires when | Catches |
| --- | --- | --- |
| `.github/workflows/eula-sync.yml` here | `eula.html` or `tools/` changes; weekly; on demand | A canonical edit landed without the mirror being brought up to match |
| `.github/workflows/eula-sync.yml` in the plugin repository | `docs/EULA.md` changes; on demand | The mirror edited directly and left out of step with the canonical page |

The weekly schedule here is the backstop for anything that slips past both.

The two repositories cannot be pushed atomically, so a push-triggered run may start before the
other side's push lands. On a push, both workflows therefore wait five minutes after a first
mismatch, fetch the other repository again, and check once more before reporting drift. Pull
requests, the schedule, and manual runs fail on the first mismatch.

Each workflow reads one file from the other, private, repository. That needs a credential, and the
credential is a **read-only deploy key** rather than a personal access token: a deploy key never
expires and is scoped to a single repository, so there is no annual re-issue and no access to
anything else in the account. Two keys are needed, one per direction:

| Deploy key on | Private half stored in | As secret |
| --- | --- | --- |
| `prismtabs/prismtabs` | `prismtabs/prismtabs-website` | `PRISMTABS_DEPLOY_KEY` |
| `prismtabs/prismtabs-website` | `prismtabs/prismtabs` | `WEBSITE_DEPLOY_KEY` |

To create one of them (repeat with the two repositories swapped for the other direction):

```bash
ssh-keygen -t ed25519 -N '' -C 'eula-sync' -f /tmp/eula-sync-key
gh repo deploy-key add /tmp/eula-sync-key.pub --repo prismtabs/prismtabs --title 'eula-sync (read-only)'
gh secret set PRISMTABS_DEPLOY_KEY --repo prismtabs/prismtabs-website < /tmp/eula-sync-key
shred -u /tmp/eula-sync-key /tmp/eula-sync-key.pub
```

`gh repo deploy-key add` grants read-only access unless `--allow-write` is passed, which is what
these jobs want: neither of them writes anything.

A missing key fails the job with an explicit message. It is never treated as a reason to skip: an
unverified legal document is exactly what these jobs exist to prevent.

One caveat worth knowing: GitHub disables scheduled workflows in a repository after 60 days without
activity, so the weekly run here is a backstop rather than a guarantee. The plugin-side workflow is
not affected — it is triggered by the very commit that would cause the drift.
