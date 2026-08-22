# Deployment

The app is a static site with no build step and no backend. That is the whole
reason deployment is easy, and it was a deliberate constraint rather than a
shortcut: hackathon wifi fails at exactly the wrong moment, so the demo had to
survive with no server of ours in the loop.

## What actually gets deployed

Only `web/`.

| | |
|---|---|
| `web/index.html` | the entire app, one file |
| `web/vendor/` | MapLibre GL, vendored — no CDN, so no third-party outage can kill the demo |
| `web/data/` | every number precomputed by the pipeline |
| **Raw** | **9.2 MB** |
| **Gzipped** | **1.6 MB** (18%) — Pages gzips text automatically |

Nothing else ships. The pipeline, the 300 MB of raw sources, the docs and the
deck all stay in the repo and out of the site.

## Primary: local server

**This stays the demo path.** It is the only one that cannot be broken by the
venue's network.

```bash
python -m http.server 8080 --directory web
# http://localhost:8080/index.html
```

It needs a server rather than `file://` because the app uses ES modules and
`fetch`, both of which browsers block on the file protocol. Any static server
works; Python's is just the one everybody already has.

**Cache warning.** If you have loaded the page before, the browser may serve you
stale JavaScript. Append a cache-buster when you want certainty:
`http://localhost:8080/index.html?v=2`. This bit me repeatedly while testing —
fixes appeared not to work because the old build was still running.

## Backup: GitHub Pages

`.github/workflows/pages.yml` publishes `web/` on every push to `main` or
`reimagine` that touches it, and can be run by hand from the Actions tab.

**One manual step, once:** repo **Settings → Pages → Source → "GitHub Actions"**.
Until that is set the workflow runs and fails at the final step, which is the
expected behaviour rather than a broken config.

Once enabled the site is at:

```
https://devanshc777.github.io/roshni/
```

The workflow verifies before it publishes: every file the app fetches at runtime
must exist and be non-empty, and every `./data/` and `./vendor/` reference in
`index.html` must resolve. A missing data file fails the build rather than
shipping a page that loads and then dies on a 404.

Deploys are queued rather than cancelled, so a push made minutes before a demo
cannot be silently dropped by a later one.

## Why the paths survive relocation

Every reference in `index.html` is relative — `./data/…`, `./vendor/…`. There is
not a single absolute path, which is why the same files work unchanged at
`localhost:8080/`, at `devanshc777.github.io/roshni/`, and from any other static
host or subdirectory.

## Other hosts

Any static host works with zero changes, because there is nothing to configure:

- **Netlify / Vercel / Cloudflare Pages** — publish directory `web`, no build command.
- **A USB stick and a laptop** — clone, run the Python server. This is the real
  disaster plan, and it needs no network at all.

## Regenerating the data

Only needed if the pipeline changes. `web/data/` is a copy of `out/`.

```bash
.venv/Scripts/python.exe data/pipeline.py       # segments, scoring, graph, stats, basemap
.venv/Scripts/python.exe data/derive_screens.py # routes, curve, telemetry
.venv/Scripts/python.exe data/build_city.py     # city.geojson, city_labels.json
cp out/*.json out/*.geojson web/data/
```

`build_city.py` asserts 225 wards, a payload under 900 KB and a scope share
between 5% and 20%, so a bad rebuild fails loudly instead of shipping quietly.

## What is deliberately not deployed

No backend, no database, no tile server, no auth, no analytics, no API keys. The
site makes **no network requests at runtime** — not one — which is both the
privacy story and the reason it cannot fail live.
