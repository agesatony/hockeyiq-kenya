#!/usr/bin/env python3
"""
Posts a short, real-data-driven update to LinkedIn after a pipeline run.

Design goals, matching the rest of this project's style:
  - Never invent numbers. Every figure in the post is read from the actual
    CSVs the notebooks just produced. If a source file is missing or empty,
    that section is skipped rather than guessed.
  - Never hard-fail the workflow. Missing LinkedIn credentials, an expired
    token, or an API error should not break the data pipeline that runs
    before this script. This script logs a clear reason and exits 0 unless
    --strict is passed.
  - Configurable for either a personal profile or a LinkedIn Company Page,
    since the API call is nearly identical — only the author URN and the
    OAuth scope granted to the access token differ.

Required environment variables (set as GitHub Actions secrets):
  LINKEDIN_ACCESS_TOKEN   OAuth 2.0 access token with w_member_social
                          (posting as a person) or w_organization_social
                          (posting as a Company Page) scope.
  LINKEDIN_AUTHOR_URN     e.g. "urn:li:person:AbCdEfGhIj" for a personal
                          profile, or "urn:li:organization:12345678" for
                          a Company Page. See README.md for how to obtain
                          this — it is not something this script can look
                          up on its own.

Optional:
  DATA_DIR                Path to data/processed (default: ../data/processed
                           relative to this script, matching the notebooks'
                           own layout).
  DIGEST_KIND             "weekly" (default) or "worldcup" — changes which
                           sections are included in the post.

Usage:
  python scripts/post_to_linkedin.py                 # posts for real
  python scripts/post_to_linkedin.py --dry-run        # prints the post, does not call the API
  python scripts/post_to_linkedin.py --strict         # exit non-zero on any failure (for debugging)
"""

import argparse
import csv
import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

LINKEDIN_UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"
LINKEDIN_API_VERSION_HEADER = "202405"  # LinkedIn versioned API; bump periodically, see README


def log(msg: str) -> None:
    print(f"[post_to_linkedin] {msg}", flush=True)


def read_csv_rows(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        return []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        log(f"WARNING: could not read {path}: {e}")
        return []


def build_weekly_digest(data_dir: Path) -> str | None:
    """Weekly domestic-season digest: league leaders + top scorer, drawn
    straight from this run's processed CSVs. Returns None if there isn't
    enough real data yet to say anything meaningful (rather than posting
    a near-empty update)."""
    league_rows = read_csv_rows(data_dir / "performance_metrics.csv")
    scorer_rows = read_csv_rows(data_dir / "top_scorers.csv")

    if not league_rows:
        log("No performance_metrics.csv data found — skipping weekly digest.")
        return None

    # League leaders (Position == "1") per competition, in whatever order
    # the CSV lists competitions.
    leaders = [r for r in league_rows if str(r.get("Position", "")).strip() == "1"]
    leader_lines = []
    for r in leaders[:8]:  # all 8 competitions, if present
        comp = r.get("Competition", "?")
        team = r.get("Team", "?")
        pts = r.get("Points", "?")
        leader_lines.append(f"  • {comp}: {team} ({pts} pts)")

    top_scorer_line = ""
    if scorer_rows:
        top = max(scorer_rows, key=lambda r: int(r.get("Goals", 0) or 0))
        top_scorer_line = (
            f"\nTop scorer so far: {top.get('Player','?')} "
            f"({top.get('Team','?')}) — {top.get('Goals','?')} goals."
        )

    if not leader_lines:
        return None

    post = (
        "HockeyIQ Kenya — weekly season update\n\n"
        "Current leaders across Kenya Hockey Union's 2026 domestic competitions:\n"
        + "\n".join(leader_lines)
        + top_scorer_line
        + "\n\nFull tables, team intelligence and season analytics: "
          "(add your published dashboard URL here — see README)\n"
          "#Hockey #KenyaHockey #SportsAnalytics"
    )
    return post


def build_worldcup_digest(data_dir: Path) -> str | None:
    """Daily World Cup context digest during the tournament window."""
    wc_rows = read_csv_rows(data_dir / "world_cup_standings.csv")
    if not wc_rows:
        log("No world_cup_standings.csv data found — skipping World Cup digest.")
        return None

    # One leader line per pool/gender combination present in the data.
    from collections import defaultdict
    pools = defaultdict(list)
    for r in wc_rows:
        key = (r.get("Gender", "?"), r.get("Pool", "?"))
        pools[key].append(r)

    lines = []
    for (gender, pool), rows in sorted(pools.items()):
        rows_sorted = sorted(rows, key=lambda r: int(r.get("PoolRank", 99) or 99))
        if not rows_sorted:
            continue
        leader = rows_sorted[0]
        if str(leader.get("Played", "0")) == "0":
            continue  # tournament not started yet for this pool
        lines.append(
            f"  • {gender} Pool {pool}: {leader.get('Team','?')} leads "
            f"({leader.get('Points','?')} pts)"
        )

    if not lines:
        log("World Cup data present but no pool has started play yet — skipping digest.")
        return None

    post = (
        "FIH Hockey World Cup 2026 — where things stand\n\n"
        "Kenya isn't competing at this World Cup, but here's the pool picture "
        "for fans following the global game:\n"
        + "\n".join(lines)
        + "\n\nFull standings and how it compares to Kenya's own scoring pattern: "
          "(add your published dashboard URL here — see README)\n"
          "#Hockey #FIHWorldCup2026 #KenyaHockey"
    )
    return post


def post_to_linkedin(text: str, access_token: str, author_urn: str, dry_run: bool) -> bool:
    body = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    if dry_run:
        log("--dry-run set: not calling the LinkedIn API. Post body would be:")
        print("-" * 70)
        print(text)
        print("-" * 70)
        return True

    req = urllib.request.Request(
        LINKEDIN_UGC_POSTS_URL,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": LINKEDIN_API_VERSION_HEADER,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            log(f"LinkedIn API responded {resp.status}. Post published.")
            return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        log(f"LinkedIn API error {e.code}: {err_body}")
        return False
    except Exception as e:
        log(f"LinkedIn API request failed: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Build and print the post, but do not call the LinkedIn API.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any failure instead of exiting 0.")
    parser.add_argument("--data-dir", default=None, help="Override the data/processed directory.")
    args = parser.parse_args()

    kind = os.environ.get("DIGEST_KIND", "weekly").strip().lower()
    data_dir = Path(args.data_dir) if args.data_dir else Path(__file__).resolve().parent.parent / "data" / "processed"

    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "").strip()
    author_urn = os.environ.get("LINKEDIN_AUTHOR_URN", "").strip()

    if not args.dry_run and (not access_token or not author_urn):
        log(
            "LINKEDIN_ACCESS_TOKEN and/or LINKEDIN_AUTHOR_URN are not set. "
            "Skipping the LinkedIn post (this is expected until you complete the "
            "one-time LinkedIn Developer App setup described in README.md)."
        )
        return 1 if args.strict else 0

    if kind == "worldcup":
        text = build_worldcup_digest(data_dir)
    else:
        text = build_weekly_digest(data_dir)

    if not text:
        log("Not enough real data yet to build a meaningful post. Skipping (not an error).")
        return 1 if args.strict else 0

    ok = post_to_linkedin(text, access_token, author_urn, args.dry_run)
    if not ok:
        return 1 if args.strict else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
