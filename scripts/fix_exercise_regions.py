"""
Batch-restore body-region tags on exercise_catalog rows that lost them.

Only touches catalog entries that are BOTH:
  - actually logged at least once (an entry you've really used), and
  - currently carrying ZERO region tags.

Entries that still have tags are never rewritten, so the tagging that
survived is left exactly as-is. Unlogged wger `suggested_exercise` rows
are a different table entirely and are never written to.

Tag values come from one of two places, never from a guess:
  1. OVERRIDES below -- the authoritative path. Slugs you supply win.
  2. wger's own anatomical data, via the same rapidfuzz name match
     get_or_create() already uses, and only above MATCH_THRESHOLD.
     Anything that doesn't match confidently is reported and skipped
     rather than tagged with something approximate.

Usage:
    # report only, writes nothing (start here)
    docker compose exec app python3 scripts/fix_exercise_regions.py

    # back up current tagging first -- there is no other copy of it
    docker compose exec app python3 scripts/fix_exercise_regions.py --export regions.json

    # write the proposed tags
    docker compose exec app python3 scripts/fix_exercise_regions.py --apply

    # one exercise at a time
    docker compose exec app python3 scripts/fix_exercise_regions.py --only 41 --apply
"""

import argparse
import json
import sys
from pathlib import Path

from rapidfuzz import fuzz, process, utils
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.connection import get_conn
from app.db.repositories import exercise_catalog as exercise_catalog_repo
from utils.body_regions import REGION_SLUGS

# Same bar get_or_create()/link_suggested_match() use. Below this, a name
# match isn't trustworthy enough to write muscle tags from.
MATCH_THRESHOLD = 88

# Exercise name (exactly as stored: lowercase) -> region slugs in PRIORITY
# order. First slug becomes rank 1 (primary target), which is what drives
# freshness and the volume ranking on the workout page.
#
# These win over any wger match. The nine names below are the entries that
# currently have no tags -- fill in the ones you want set and leave the
# rest commented out. Valid slugs are in utils/body_regions.py:
#
#   chest  biceps  triceps  forearm  front-deltoids  abs  obliques
#   quadriceps  abductors  back-deltoids  trapezius  upper-back
#   lower-back  hamstring  gluteal  adductor  calves
OVERRIDES: dict[str, list[str]] = {
    # "bicep curls": [],
    # "db skull crushers": [],
    # "flat bench press": [],
    # "lat row": [],
    # "one arm shoulder row": [],
    # "pull up": [],
    # "romanian deadlift": [],
    # "squats": [],
    # "tricep ext": [],
}


def resolve_user_id(conn, requested: int | None) -> int:
    if requested is not None:
        return requested
    rows = conn.execute(text("SELECT id FROM app_user ORDER BY id")).mappings().all()
    if len(rows) != 1:
        raise SystemExit(
            f"Found {len(rows)} users; pass --user-id to pick one."
        )
    return rows[0]["id"]


def load_logged_catalog(conn, user_id: int):
    """Catalog entries with >=1 real log, plus their current region tags."""
    sql = """
        SELECT
            ec.id,
            ec.name,
            ec.metric_type,
            COUNT(e.id) AS log_count,
            (SELECT string_agg(ecr.region_slug, ',' ORDER BY ecr.rank)
             FROM exercise_catalog_region ecr
             WHERE ecr.exercise_catalog_id = ec.id) AS regions
        FROM exercise_catalog ec
        JOIN exercise e ON e.exercise_catalog_id = ec.id
        WHERE ec.user_id = :user_id
        GROUP BY ec.id, ec.name, ec.metric_type
        ORDER BY ec.name
    """
    return conn.execute(text(sql), {"user_id": user_id}).mappings().all()


def wger_proposal(conn, name: str, suggestion_names: dict[int, str]):
    """(slugs, matched_name, score) from wger data, or (None, name, score)."""
    match = process.extractOne(
        name, suggestion_names, scorer=fuzz.WRatio, processor=utils.default_process
    )
    if match is None:
        return None, None, 0

    matched_name, score, matched_id = match
    if score < MATCH_THRESHOLD:
        return None, matched_name, score

    region_rows = conn.execute(
        text(
            """
            SELECT region_slug
            FROM suggested_exercise_region
            WHERE suggested_exercise_id = :sid
            ORDER BY (role = 'primary') DESC, region_slug
            """
        ),
        {"sid": matched_id},
    ).mappings().all()
    slugs = [r["region_slug"] for r in region_rows]
    return (slugs or None), matched_name, score


def validate(slugs: list[str], label: str) -> list[str]:
    bad = [s for s in slugs if s not in REGION_SLUGS]
    if bad:
        raise SystemExit(f"{label}: unknown region slug(s) {bad}. See utils/body_regions.py")
    return list(dict.fromkeys(slugs))  # dedupe, keep priority order


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changes (default: report only)")
    parser.add_argument("--only", type=int, metavar="ID", help="restrict to one exercise_catalog id")
    parser.add_argument("--user-id", type=int, help="user to operate on")
    parser.add_argument("--export", metavar="PATH", help="dump current tagging to JSON and exit")
    args = parser.parse_args()

    conn = get_conn()
    try:
        user_id = resolve_user_id(conn, args.user_id)
        rows = load_logged_catalog(conn, user_id)

        if args.export:
            payload = {
                r["name"]: (r["regions"].split(",") if r["regions"] else [])
                for r in rows
            }
            Path(args.export).write_text(json.dumps(payload, indent=2, sort_keys=True))
            print(f"wrote {len(payload)} entries to {args.export}")
            return

        if args.only:
            rows = [r for r in rows if r["id"] == args.only]
            if not rows:
                raise SystemExit(f"No logged catalog entry with id {args.only} for user {user_id}.")

        suggestion_names = {
            r["id"]: r["name"]
            for r in conn.execute(text("SELECT id, name FROM suggested_exercise")).mappings().all()
        }

        planned: list[tuple[int, str, list[str], str]] = []
        skipped: list[str] = []
        kept = 0

        for row in rows:
            name = row["name"]
            current = row["regions"].split(",") if row["regions"] else []

            if current:
                kept += 1
                print(f"  [{row['id']:>3}] {name:<24} logs={row['log_count']:<3} keeping: {', '.join(current)}")
                continue

            if row["metric_type"] == "endurance":
                skipped.append(f"{name} (endurance -- regions are resistance-only by design)")
                continue

            if name in OVERRIDES and OVERRIDES[name]:
                slugs = validate(OVERRIDES[name], f"OVERRIDES[{name!r}]")
                planned.append((row["id"], name, slugs, "override"))
                print(f"  [{row['id']:>3}] {name:<24} logs={row['log_count']:<3} -> {', '.join(slugs)}  (your override)")
                continue

            slugs, matched_name, score = wger_proposal(conn, name, suggestion_names)
            if not slugs:
                detail = f'best "{matched_name}" scored {score:.0f}' if matched_name else "no candidate"
                skipped.append(f"{name} -- {detail}, below {MATCH_THRESHOLD}; add an OVERRIDES entry")
                print(f"  [{row['id']:>3}] {name:<24} logs={row['log_count']:<3} !! no confident match ({detail})")
                continue

            slugs = validate(slugs, f'wger match for "{name}"')
            planned.append((row["id"], name, slugs, f'wger "{matched_name}" {score:.0f}'))
            print(f"  [{row['id']:>3}] {name:<24} logs={row['log_count']:<3} -> {', '.join(slugs)}  (wger \"{matched_name}\" {score:.0f})")

        print(f"\n{kept} already tagged (untouched), {len(planned)} to write, {len(skipped)} skipped")
        if skipped:
            print("\nSkipped -- these need an OVERRIDES entry to get tagged:")
            for line in skipped:
                print(f"  - {line}")

        if not args.apply:
            print("\nReport only. Re-run with --apply to write the above.")
            return

        for catalog_id, name, slugs, source in planned:
            exercise_catalog_repo.tag_regions(conn, catalog_id, slugs, commit=False)
            print(f"tagged {name}: {', '.join(slugs)}  [{source}]")
        conn.commit()
        print(f"\ndone -- {len(planned)} exercise(s) tagged")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
