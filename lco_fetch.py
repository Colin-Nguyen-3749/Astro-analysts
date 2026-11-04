"""
LCO archive: paginated frame fetch + FITS header collection.

Usage in a notebook:
    from lco_fetch import fetch_all_frames, build_dataframe
    frames = fetch_all_frames('2026-08-01', '2026-08-08')
    df = build_dataframe(frames)
"""

'''
Please note that this code is generated using Claude AI, which 
permission to do so by LCO!
'''
import os
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://archive-api.lco.global"

# Put the token in an environment variable instead of in the notebook:
#   Windows (PowerShell):  setx LCO_API_TOKEN "your_token"   (then restart Jupyter)
API_TOKEN = os.environ.get("LCO_API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("Set the LCO_API_TOKEN environment variable first.")

# One shared session: reuses connections and retries on rate limits / server errors.
session = requests.Session()
session.headers.update({"Authorization": f"Token {API_TOKEN}"})
session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=5, backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)))


# ---------------------------------------------------------------- frames ----
def fetch_frames_window(start, end, extra_params=None, limit=1000):
    """Yield every frame between start and end using cursor pagination."""
    params = {
        "start": start,
        "end": end,
        "reduction_level": 91,
        "configuration_type": "EXPOSE",   # filter on the server, not after download
        "limit": limit,
        "pagination_style": "cursor",
    }
    params.update(extra_params or {})

    url = f"{BASE}/frames/"
    while url:
        r = session.get(url, params=params if url.endswith("/frames/") else None, timeout=60)
        r.raise_for_status()
        page = r.json()
        yield from page["results"]
        url = page.get("next")   # full URL incl. cursor; None on the last page


def fetch_all_frames(start, end, window_days=1, extra_params=None):
    """
    Walk a date range in 1-day windows (more robust than one giant query),
    de-duplicating by frame id in case windows overlap at the edges.
    """
    t0 = datetime.fromisoformat(start)
    t1 = datetime.fromisoformat(end)
    seen, frames = set(), []

    while t0 < t1:
        t_next = min(t0 + timedelta(days=window_days), t1)
        w_start = t0.strftime("%Y-%m-%dT%H:%M:%SZ")
        w_end = t_next.strftime("%Y-%m-%dT%H:%M:%SZ")
        n_before = len(frames)
        for f in fetch_frames_window(w_start, w_end, extra_params):
            if f["id"] not in seen:
                seen.add(f["id"])
                frames.append(f)
        print(f"{w_start} -> {w_end}: +{len(frames) - n_before} (total {len(frames)})")
        t0 = t_next
    return frames


# --------------------------------------------------------------- headers ----
HEADER_FIELDS = ["WCSERR", "SATFRAC", "EXPTIME", "FILTER", "AIRMASS", "L1FWHM",
                 "MOONFRAC", "MOONDIST", "SKYMAG", "WMSHUMID", "WMSTEMP", "PIXSCALE"]
FRAME_FIELDS = ["basename", "observation_date", "site_id", "telescope_id", "instrument_id"]


def _get_row(frame):
    r = session.get(f"{BASE}/frames/{frame['id']}/headers/", timeout=60)
    r.raise_for_status()
    h = r.json()["data"]
    row = {"id": frame["id"]}
    row.update({k: frame.get(k) for k in FRAME_FIELDS})
    row.update({k: h.get(k) for k in HEADER_FIELDS})   # missing keys become NaN, not dropped
    return row


def build_dataframe(frames, workers=8, cache_csv="lco_headers_cache.csv"):
    """Fetch headers in parallel; resumes from a cache file if one exists."""
    done = pd.read_csv(cache_csv) if os.path.exists(cache_csv) else pd.DataFrame()
    done_ids = set(done["id"]) if len(done) else set()
    todo = [f for f in frames if f["id"] not in done_ids]
    print(f"{len(done_ids)} cached, {len(todo)} to fetch")

    rows = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, row in enumerate(ex.map(_get_row, todo), 1):
            rows.append(row)
            if i % 200 == 0:   # checkpoint so a crash doesn't lose everything
                pd.concat([done, pd.DataFrame(rows)]).to_csv(cache_csv, index=False)
                print(f"  {i}/{len(todo)}")

    df = pd.concat([done, pd.DataFrame(rows)], ignore_index=True)
    df = df.drop_duplicates(subset="id")
    df.to_csv(cache_csv, index=False)
    return df


if __name__ == "__main__":
    frames = fetch_all_frames("2026-08-01T00:00:00", "2026-08-08T00:00:00")
    df = build_dataframe(frames)
    print(df.shape)
    print(df["WCSERR"].value_counts(dropna=False))
