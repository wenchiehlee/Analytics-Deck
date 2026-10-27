#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/fetch_analytics.py
Sync analytics telemetry data (Pageviews and 30D Active Users) from GA4 into data/endpoints.json.
Runs 4 times a day (every 6 hours) via GitHub Actions or locally with .env.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ENDPOINTS_JSON = DATA_DIR / "endpoints.json"
DOCS_DIR = BASE_DIR / "docs"

MASTER_PROPERTY_ID = "463673189"

def load_env_file():
    """Load variables from .env file if present."""
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val

def update_offline_snapshot(data: dict):
    """Fallback when GA4 credentials are not configured in environment."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    now_tpe = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    print(f"[*] Executing offline snapshot sync at {now_utc} (Taipei: {now_tpe})...")
    data["metadata"]["last_sync"] = now_utc
    data["metadata"]["last_sync_local"] = f"{now_tpe} (4 renewals/day)"

    for ep in data.get("endpoints", []):
        analytics = ep.get("analytics", {})
        analytics["last_sync"] = now_utc
        ep["analytics"] = analytics

    with open(ENDPOINTS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] Refreshed telemetry timestamps across {len(data['endpoints'])} endpoints.")
    
    # Auto rebuild index.html
    rebuild_pages()

def rebuild_pages():
    try:
        if str(BASE_DIR) not in sys.path:
            sys.path.insert(0, str(BASE_DIR))
        from scripts.build_page import build_index_html
        build_index_html()
    except Exception as e:
        print(f"[!] Warning building index.html: {e}")

def get_service_account_token(creds_input: str) -> str:
    """Acquire OAuth2 access token for GA4 Data API from Service Account."""
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request

    if os.path.exists(creds_input):
        creds = service_account.Credentials.from_service_account_file(
            creds_input,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )
    else:
        creds_info = json.loads(creds_input)
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"]
        )

    creds.refresh(Request())
    return creds.token

def fetch_live_ga4(data: dict, credentials_input: str):
    """Query live GA4 Data API via REST for each endpoint."""
    print("[*] Authenticating with Google Analytics Data API via Service Account...")
    try:
        token = get_service_account_token(credentials_input)
        print("[✓] Service Account access token acquired successfully.")
    except Exception as e:
        print(f"[!] Authentication error: {e}")
        update_offline_snapshot(data)
        return

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    now_tpe = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["metadata"]["last_sync"] = now_utc
    data["metadata"]["last_sync_local"] = f"{now_tpe} (4 renewals/day)"

    property_id = data["endpoints"][0]["analytics"]["ga4"].get("property_id", MASTER_PROPERTY_ID)
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"[*] Querying GA4 Property {property_id} for {len(data['endpoints'])} endpoints...")

    for ep in data.get("endpoints", []):
        ep_id = ep["id"]
        # Determine filter keyword for GA4 path
        if "mkdocs-life" in ep_id:
            filter_kw = "mkdocs-life"
        elif "mkdocs-investment" in ep_id:
            filter_kw = "mkdocs-investment"
        else:
            filter_kw = ep_id

        # Query lifetime views
        p_lifetime = {
            "dateRanges": [{"startDate": "2020-01-01", "endDate": "today"}],
            "metrics": [{"name": "screenPageViews"}],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "pagePath",
                    "stringFilter": {
                        "matchType": "CONTAINS",
                        "value": filter_kw
                    }
                }
            }
        }

        # Query 30-day active users
        p_30d = {
            "dateRanges": [{"startDate": "30daysAgo", "endDate": "today"}],
            "metrics": [{"name": "activeUsers"}],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "pagePath",
                    "stringFilter": {
                        "matchType": "CONTAINS",
                        "value": filter_kw
                    }
                }
            }
        }

        try:
            req_l = urllib.request.Request(url, data=json.dumps(p_lifetime).encode(), headers=headers)
            res_l = json.loads(urllib.request.urlopen(req_l).read().decode())
            views = int(res_l["rows"][0]["metricValues"][0]["value"]) if res_l.get("rows") else 0

            req_a = urllib.request.Request(url, data=json.dumps(p_30d).encode(), headers=headers)
            res_a = json.loads(urllib.request.urlopen(req_a).read().decode())
            active_users = int(res_a["rows"][0]["metricValues"][0]["value"]) if res_a.get("rows") else 0

            if views > 0:
                ep["analytics"]["views_total"] = views
                ep["analytics"]["active_users_30d"] = f"{active_users:,}"
                print(f"    [✓] {ep_id:<22} -> Views: {views:>6,} | 30D Active: {active_users:>5,}")
            else:
                ep["analytics"]["views_total"] = None
                ep["analytics"]["active_users_30d"] = "---"
                print(f"    [-] {ep_id:<22} -> No GA4 records for Property {property_id} (shows ---)")

            ep["analytics"]["last_sync"] = now_utc

        except Exception as err:
            print(f"    [!] Error querying {ep_id}: {err}")
            ep["analytics"]["views_total"] = None
            ep["analytics"]["active_users_30d"] = "---"

    with open(ENDPOINTS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n[🎉] Live GA4 telemetry sync completed successfully!")

    rebuild_pages()

def main():
    load_env_file()

    parser = argparse.ArgumentParser(description="Fetch GA4 telemetry data for Analytics-Deck.")
    parser.add_argument("--dry-run", action="store_true", help="Run without calling Google API")
    args = parser.parse_args()

    if not ENDPOINTS_JSON.exists():
        print(f"[!] Error: {ENDPOINTS_JSON} not found. Run scripts/sync_from_ux_deck.py first.")
        sys.exit(1)

    with open(ENDPOINTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    ga4_creds = os.environ.get("GA4_SERVICE_ACCOUNT_KEY")
    if ga4_creds and not args.dry_run:
        fetch_live_ga4(data, ga4_creds)
    else:
        update_offline_snapshot(data)

if __name__ == "__main__":
    main()
