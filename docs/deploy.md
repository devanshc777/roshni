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

## Cloudflare Pages, and why both

Worth running alongside Pages rather than instead of it. Two live URLs is better
insurance than picking a winner, and they cost nothing to keep.

Setup, once: **Cloudflare dashboard → Workers & Pages → Create → Pages → Connect
to Git → this repo.** Framework preset **None**, build command **empty**, output
directory **`web`**. That is the whole configuration, because there is no build.

Two things Cloudflare does better *for this specific demo*:

**Latency where the judges are.** Cloudflare has Mumbai and Bengaluru points of
presence. GitHub Pages fronts with Fastly, which is fine but further away. On
conference wifi, opening a 1.6 MB page from a PoP in the same city is a
noticeable difference.

**`web/_headers` is honoured.** GitHub Pages ignores it, which is why shipping it
costs nothing. On Cloudflare it does two jobs:

- `/data/*` and `/vendor/*` are served `immutable` for a year. 7.8 MB of the 9.2
  MB total is precomputed data that only changes when the pipeline is re-run, so
  a second visit downloads almost nothing. `index.html` is `no-cache`, so a
  deploy is never masked by a stale page — the hosted version of the cache trap
  described above.
- A **Content-Security-Policy** that is unusually strict because the app earns
  it: no backend, no CDN, no analytics, no third-party anything, and zero network
  requests at runtime. `connect-src 'self'` with nothing else would break most
  sites; here nothing notices.

The CSP was verified rather than assumed — injected as a `<meta>` tag into a copy
of the app, loaded in a real browser, and every surface driven under it. It needs
`'unsafe-inline'` for script and style, because the app is deliberately one file
with an inline module and inline CSS, and `blob:` for `worker-src`, because
MapLibre spawns its worker that way. `frame-ancestors` is ignored when delivered
by `<meta>` but works as a real header, which is how `_headers` sends it.

## What Cloudflare is not needed for here

Worth stating, because the obvious comparison is misleading. LDR Jigsaw is on
Cloudflare Workers for a real architectural reason — one Durable Object per room,
matching one engine per room, plus R2 and WebSockets. **Roshni has no server, no
state, no sockets and no uploads.** Every primitive that made Cloudflare the
right call there is absent here, so this is a plain static-hosting decision and
almost any host would do. Pick the host whose primitives match the architecture;
do not carry a previous project's answer across.

## Other hosts

Any static host works with zero changes, because there is nothing to configure:

- **Netlify / Vercel** — publish directory `web`, no build command.
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
