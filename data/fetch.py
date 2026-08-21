#!/usr/bin/env python3
"""
Roshni — pull every source in manifest.json into data/raw/.

    python data/fetch.py              # everything
    python data/fetch.py --grade A    # only grade-A sources
    python data/fetch.py --id bbmp_grievances_2025 bmtc_stops_aggregated

Stdlib only, no dependencies. Skips files already downloaded unless --force.
Run this first, then run the queries in data/overpass.md, then read
docs/data-sources.md before writing a single loader.
"""

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"
UA = "roshni-hackathon/0.1 (+data fetch; contact: team)"


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024.0


def fetch(url: str, dest: Path, force: bool = False) -> tuple[bool, str]:
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return True, f"skip (have {human(dest.stat().st_size)})"
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Several state/municipal hosts serve incomplete cert chains. We are pulling
    # public open data, not authenticating anything, so fall back rather than die.
    contexts = [None, ssl._create_unverified_context()]
    last = ""
    for ctx in contexts:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            kw = {"context": ctx} if ctx else {}
            with urllib.request.urlopen(req, timeout=120, **kw) as r:
                body = r.read()
            if not body:
                last = "empty response"
                continue
            dest.write_bytes(body)
            note = human(len(body))
            if ctx is not None:
                note += "  [tls verification skipped]"
            return True, note
        except urllib.error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
    return False, last


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", nargs="*", help="only these grades, e.g. --grade A B")
    ap.add_argument("--id", nargs="*", help="only these source ids")
    ap.add_argument("--force", action="store_true", help="re-download existing files")
    args = ap.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = manifest["sources"]
    if args.grade:
        sources = [s for s in sources if s.get("grade") in args.grade]
    if args.id:
        sources = [s for s in sources if s["id"] in args.id]

    if not sources:
        print("nothing matched", file=sys.stderr)
        return 1

    width = max(len(s["id"]) for s in sources)
    failed = []
    print(f"roshni: fetching {len(sources)} sources into {HERE / 'raw'}\n")

    for s in sources:
        dest = HERE / s["out"]
        ok, note = fetch(s["url"], dest, force=args.force)
        mark = "ok  " if ok else "FAIL"
        print(f"  [{s.get('grade','?')}] {mark} {s['id']:<{width}}  {note}")
        if not ok:
            failed.append((s["id"], s["url"], note))

    print()
    if failed:
        print(f"{len(failed)} failed:\n")
        for sid, url, note in failed:
            print(f"  {sid}\n    {note}\n    {url}\n")
        print("If OpenCity is unreachable from this machine, open the URL in a")
        print("browser and save it to the path in manifest.json manually. Do not")
        print("burn hackathon hours debugging someone else's TLS config.")
    else:
        print("all sources fetched.")

    print("\nNext:")
    print("  1. data/overpass.md  — run the queries, verify lamp coverage in your bbox")
    print("  2. docs/data-sources.md — read before writing a loader")
    print("  3. docs/risks.md §1 — the ward-name join will bite you")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
