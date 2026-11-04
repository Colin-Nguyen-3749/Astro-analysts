#!/usr/bin/env python3
"""Export public LCO archive frame metadata and FITS headers to CSV.

The CSV includes the WCSERR and site_id columns used by lco_codebook.ipynb.
An API token is requested privately at runtime and is never saved in this file.
"""

from __future__ import annotations

import argparse
import csv
import getpass
import os
import sys
import time
from datetime import date, datetime, time as datetime_time
from pathlib import Path
from typing import Any

API_ROOT = "https://archive-api.lco.global"
TIMEOUT_SECONDS = 40
FIELDS = [
    "frame_id",
    "filename",
    "site_id",
    "observation_date",
    "proposal_id",
    "configuration_type",
    "reduction_level",
    "WCSERR",
]


def parse_date(value: str, *, end_of_day: bool) -> str:
    """Convert YYYY-MM-DD to an ISO timestamp accepted by the archive API."""
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use a date in YYYY-MM-DD format.") from exc
    clock = datetime_time(23, 59, 59) if end_of_day else datetime_time.min
    return datetime.combine(parsed, clock).isoformat()


def get_json(session: requests.Session, url: str, *, params: dict[str, str] | None = None) -> dict[str, Any]:
    response = session.get(url, params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected a JSON object from {response.url}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch public LCO frames and their FITS headers into a CSV."
    )
    parser.add_argument("--start-date", required=True, help="First UTC date, YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="Last UTC date, YYYY-MM-DD (inclusive)")
    parser.add_argument("--output", default="lco_data_public.csv", help="CSV path (default: lco_data_public.csv)")
    parser.add_argument("--reduction-level", default="91", help="Frame reduction level (default: 91)")
    parser.add_argument("--configuration-type", default="EXPOSE", help="Frame type (default: EXPOSE)")
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("Missing package 'requests'. Install it with: python3 -m pip install requests")
        return 1

    try:
        start = parse_date(args.start_date, end_of_day=False)
        end = parse_date(args.end_date, end_of_day=True)
        if datetime.fromisoformat(start) > datetime.fromisoformat(end):
            parser.error("--start-date must be on or before --end-date")
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    token = os.environ.get("LCO_API_TOKEN") or getpass.getpass("LCO API token (input hidden): ").strip()
    if not token:
        print("No API token entered. Nothing was downloaded.")
        return 2

    session = requests.Session()
    session.headers.update({"Authorization": f"Token {token}"})
    params = {
        "start": start,
        "end": end,
        "public": "true",
        "configuration_type": args.configuration_type,
        "reduction_level": args.reduction_level,
    }

    try:
        print("Searching the LCO archive…", flush=True)
        frames: list[dict[str, Any]] = []
        next_url: str | None = f"{API_ROOT}/frames/"
        first_page = True
        while next_url:
            payload = get_json(session, next_url, params=params if first_page else None)
            first_page = False
            results = payload.get("results", [])
            if not isinstance(results, list):
                raise RuntimeError("The archive response did not contain a results list.")
            frames.extend(row for row in results if isinstance(row, dict))
            next_value = payload.get("next")
            next_url = str(next_value) if next_value else None

        print(f"Found {len(frames)} matching public frames.", flush=True)
        if not frames:
            print("No frames matched. Try a shorter date range or check the filters.")
            return 0

        rows: list[dict[str, Any]] = []
        failed_headers = 0
        for index, frame in enumerate(frames, start=1):
            frame_id = frame.get("id")
            headers: dict[str, Any] = {}
            if frame_id is not None:
                try:
                    header_payload = get_json(session, f"{API_ROOT}/frames/{frame_id}/headers/")
                    raw_headers = header_payload.get("data", {})
                    if isinstance(raw_headers, dict):
                        headers = raw_headers
                    else:
                        failed_headers += 1
                except (requests.RequestException, ValueError, RuntimeError) as exc:
                    failed_headers += 1
                    print(f"Could not read headers for frame {frame_id}: {exc}", file=sys.stderr)
            else:
                failed_headers += 1

            rows.append(
                {
                    "frame_id": frame_id,
                    "filename": frame.get("filename") or frame.get("basename"),
                    "site_id": frame.get("site_id") or headers.get("SITEID"),
                    "observation_date": frame.get("observation_date") or headers.get("DATE-OBS"),
                    "proposal_id": frame.get("proposal_id"),
                    "configuration_type": frame.get("configuration_type"),
                    "reduction_level": frame.get("reduction_level"),
                    "WCSERR": headers.get("WCSERR", frame.get("WCSERR", "")),
                }
            )
            if index % 25 == 0 or index == len(frames):
                print(f"Read headers for {index}/{len(frames)} frames…", flush=True)
            # Keep requests gentle on the archive while fetching many headers.
            if index % 20 == 0:
                time.sleep(0.2)

        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

        print(f"Saved {len(rows)} rows to: {output_path}")
        if failed_headers:
            print(f"Note: headers failed for {failed_headers} frame(s); their WCSERR cells may be blank.")
        print("In your notebook, load it with: pd.read_csv('lco_data_public.csv')")
        return 0
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        print(f"Archive request failed (HTTP {status}): {exc}", file=sys.stderr)
        if status in (401, 403):
            print("Check that your API token is current and has archive access.", file=sys.stderr)
        return 1
    except (requests.RequestException, ValueError, RuntimeError) as exc:
        print(f"Could not finish the archive request: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
