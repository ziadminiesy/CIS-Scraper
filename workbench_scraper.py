"""
=========================================================
CIS WorkBench Benchmark Scraper (Auto Sidebar Link Version)
---------------------------------------------------------
- Input: Benchmark URL (e.g. https://workbench.cisecurity.org/benchmarks/20223)
- Automatically expands sidebar, extracts recommendation links,
  and scrapes: Name (if exists), Description (first sentence only),
  Rationale, Audit Procedure, Remediation Procedure.
- Output: Excel file with all recommendations.

New Features:
  --limit <number> : Stop scraping after collecting N recommendations
  Enhanced Name extraction: captures both number and title (e.g., 2.1.3 Secure Backup Credentials)
=========================================================
Usage:
  python cis_workbench_benchmark_scraper.py --url https://workbench.cisecurity.org/benchmarks/20223 \
      --cookies cookies.json --output cis_mysql_benchmark.xlsx --limit 10
=========================================================
"""

import json
import time
import os
import argparse
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def scrape_workbench(benchmark_url, cookies_file, output_file, headless=False, limit=None):
    # Load cookies
    if not os.path.exists(cookies_file):
        raise FileNotFoundError(f"Cookies file not found: {cookies_file}")
    with open(cookies_file, "r") as f:
        cookies = json.load(f)

    # Setup Chrome
    chromedriver_path = r"C:\DRIVER\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}")

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")

    print("[+] Launching Chrome...")
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)

    # Authenticate with cookies
    print("[+] Authenticating to CIS WorkBench...")
    driver.get("https://workbench.cisecurity.org/")
    time.sleep(2)
    for name, value in cookies.items():
        driver.add_cookie({"name": name, "value": value, "domain": "workbench.cisecurity.org"})
    driver.refresh()
    time.sleep(2)

    # Open benchmark
    print(f"[+] Opening benchmark: {benchmark_url}")
    driver.get(benchmark_url)
    time.sleep(4)

    # Scroll sidebar to load all sections
    print("[+] Scrolling sidebar...")
    try:
        sidebar = driver.find_element(By.CSS_SELECTOR, "div.sidebar")
        for _ in range(15):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
            time.sleep(0.5)
    except Exception:
        print("[!] Sidebar not found; proceeding anyway.")

    # Collect recommendation links
    print("[+] Collecting recommendation links...")
    all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/recommendations/']")
    rec_links = []
    for link in all_links:
        href = link.get_attribute("href")
        if href and "/recommendations/" in href and href not in rec_links:
            rec_links.append(href)

    print(f"[+] Found {len(rec_links)} recommendations total.")
    if not rec_links:
        print("[!] No links found; check login cookies.")
        driver.quit()
        return

    # Limit results if requested
    if limit is not None:
        limit = min(limit, len(rec_links))
        rec_links = rec_links[:limit]
        print(f"[+] Limiting scraping to first {limit} recommendations.")

    # Check if Name field exists using the first recommendation
    driver.get(rec_links[0])
    time.sleep(3)
    has_name_field = False
    try:
        driver.find_element(By.CSS_SELECTOR, "h1.page-title")
        has_name_field = True
        print("[+] Name field detected — will include 'Name' column.")
    except Exception:
        print("[+] No Name field found — skipping 'Name' column.")

    # IDs to extract
    IDS = {
        "Description": "description-recommendation-data",
        "Rationale": "rationale_statement-recommendation-data",
        "Audit Procedure": "audit_procedure-recommendation-data",
        "Remediation Procedure": "remediation_procedure-recommendation-data",
    }

    # Scrape loop
    records = []
    for idx, url in enumerate(rec_links, start=1):
        print(f"\n[{idx}/{len(rec_links)}] Scraping: {url}")
        driver.get(url)
        time.sleep(3)

        row = {"URL": url}

        # Optional Name (number + title)
        if has_name_field:
            try:
                number_elem = driver.find_element(By.CSS_SELECTOR, "h1.page-title span.view-level")
                title_elem = driver.find_element(By.CSS_SELECTOR, "h1.page-title span[style*='overflow-wrap']")
                number = number_elem.text.strip()
                title = title_elem.text.strip()
                name_text = f"{number} {title}".strip()
                row["Name"] = name_text
            except Exception:
                # fallback: try whole h1 text
                try:
                    h1_elem = driver.find_element(By.CSS_SELECTOR, "h1.page-title")
                    row["Name"] = h1_elem.text.strip()
                except:
                    row["Name"] = ""

        # Extract data from content blocks
        for label, eid in IDS.items():
            try:
                script = f"var el = document.getElementById('{eid}'); return el ? el.innerText.trim() : '';"
                text = driver.execute_script(script)
                text = " ".join(text.split()) if text else ""

                # Keep only first sentence for Description
                if label == "Description" and text:
                    match = re.split(r'(?<=[.!?])\s+', text.strip())
                    first_sentence = match[0] if match else text
                    row[label] = first_sentence
                else:
                    row[label] = text
            except Exception as e:
                print(f"    [!] Error extracting {label}: {e}")
                row[label] = ""

        print("    ->", {k: ("[EMPTY]" if not v else v[:90] + "...") for k, v in row.items() if k != "URL"})
        records.append(row)
        time.sleep(1.0)

        # Stop early if limit reached
        if limit and idx >= limit:
            print(f"[+] Reached scraping limit ({limit}). Stopping early.")
            break

    driver.quit()

    # Save to Excel
    columns = ["URL"]
    if has_name_field:
        columns.append("Name")
    columns += list(IDS.keys())

    df = pd.DataFrame(records, columns=columns)
    df.to_excel(output_file, index=False)
    print(f"\n✅ Done! Scraped {len(records)} recommendations. Saved to {output_file}")


# --- CLI ENTRY POINT ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIS WorkBench Benchmark Scraper")
    parser.add_argument("--url", required=True, help="Benchmark base URL (e.g. https://workbench.cisecurity.org/benchmarks/20223)")
    parser.add_argument("--cookies", default="cookies.json", help="Path to cookies JSON file")
    parser.add_argument("--output", default="cis_workbench_output.xlsx", help="Output Excel filename")
    parser.add_argument("--limit", type=int, help="Maximum number of recommendations to extract (optional)")
    args = parser.parse_args()

    scrape_workbench(args.url, args.cookies, args.output, limit=args.limit)
