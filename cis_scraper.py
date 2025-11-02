"""
=========================================================
CIS Scraper — Unified Benchmark Scraper
---------------------------------------------------------
Automatically detects if the URL is from Tenable or CIS WorkBench,
then runs the appropriate scraper.

Usage Examples:
---------------
Tenable:
    python cis_scraper.py --url https://www.tenable.com/audits/items/CIS_PostgreSQL_17_v1.0.0_L1_Database \
        --output postgres.xlsx --limit 20

CIS WorkBench:
    python cis_scraper.py --url https://workbench.cisecurity.org/benchmarks/20223 \
        --cookies cookies.json --output cis_mysql.xlsx --limit 15
=========================================================
"""

import argparse
import sys
import logging
import importlib

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)
log = logging.getLogger("launcher")

# ---------------------------------------------------------------------------
# Unified Launcher
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Unified launcher for Tenable and CIS WorkBench scrapers."
    )
    parser.add_argument("--url", required=True, help="Benchmark URL (Tenable or WorkBench)")
    parser.add_argument("--cookies", help="Path to cookies.json (WorkBench only)")
    parser.add_argument("--output", default="benchmark_output.xlsx", help="Output Excel filename")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--limit", type=int, default=None, help="Max number of controls to scrape")
    args = parser.parse_args()

    url = args.url.strip()

    # --- Detect Source ------------------------------------------------------
    if "tenable.com" in url:
        log.info("Detected source: Tenable")
        scraper = importlib.import_module("tenable_scraper")
        scraper.scrape_tenable(url, args.output, headless=args.headless, limit=args.limit)

    elif "workbench.cisecurity.org" in url:
        log.info("Detected source: CIS WorkBench")
        scraper = importlib.import_module("workbench_scraper")
        scraper.scrape_workbench(url, args.cookies, args.output, headless=args.headless, limit=args.limit)

    else:
        log.error("❌ Unsupported URL. Must be Tenable or CIS WorkBench.")
        sys.exit(1)


if __name__ == "__main__":
    main()
