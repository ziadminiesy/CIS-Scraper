"""
=========================================================
Tenable CIS Benchmark Scraper (Open Source Edition)
---------------------------------------------------------
Extracts CIS benchmark controls and their 'Solution' sections
from Tenable audit pages and saves them to Excel.

New Feature:
  --limit <number> : Stop scraping after collecting N controls.

Author: Ziad Miniesy
License: MIT
=========================================================
"""

import argparse
import logging
import random
import time
import re
from urllib.parse import urlparse
from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller


# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s - %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)
log = logging.getLogger("tenable_scraper")


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------
def setup_driver(headless: bool = False):
    """Install ChromeDriver automatically and set up Selenium driver."""
    chromedriver_autoinstaller.install()
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.set_page_load_timeout(120)
    return driver


def get_total_controls(driver):
    """Extract 'Estimated Item Count' from the page."""
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "h4")))
        elem = driver.find_element(
            By.XPATH, "//strong[contains(., 'Estimated Item Count')]/following-sibling::span"
        )
        count = int(elem.text.strip())
        log.info(f"Detected estimated item count: {count}")
        return count
    except Exception:
        log.warning("Could not auto-detect item count. Defaulting to 50.")
        return 50


def extract_solution(driver):
    """Extract text from the 'Solution' section only."""
    h4s = driver.find_elements(By.TAG_NAME, "h4")
    for h4 in h4s:
        if "solution" in h4.text.strip().lower():
            parts = []
            siblings = h4.find_elements(By.XPATH, "following-sibling::*")
            for el in siblings:
                if el.tag_name.lower() == "h4":
                    break
                text = el.text.strip()
                if text:
                    parts.append(text)
            return " ".join(parts)
    return ""


# ---------------------------------------------------------------------------
# Main scraper logic
# ---------------------------------------------------------------------------
def scrape_tenable(url, output_file, headless=False, limit=None):
    driver = None
    try:
        driver = setup_driver(headless=headless)
        wait = WebDriverWait(driver, 30)

        log.info(f"Opening base page: {url}")
        driver.get(url)

        benchmark_slug = urlparse(url).path.split("/")[-1]
        log.info(f"Detected benchmark slug: {benchmark_slug}")

        total_controls = get_total_controls(driver)

        wb = Workbook()
        ws = wb.active
        ws.title = "Tenable_CIS_Data"
        ws.append(["Control", "Solution", "URL"])

        seen = set()
        page_num = 1
        scraped_count = 0

        while len(seen) < total_controls:
            log.info(f"Scraping page {page_num}...")
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='audits/items/']")))
            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='audits/items/']")

            new_controls = []
            for a in links:
                href = a.get_attribute("href")
                text = a.text.strip()

                if not href or not text:
                    continue
                if any(x in href for x in ["search", "filters", "create", "edit", "tag"]):
                    continue
                if benchmark_slug not in href:
                    continue
                if href in seen:
                    continue

                new_controls.append((text, href))

            log.info(f"Found {len(new_controls)} new controls on this page")

            for name, ctrl_url in new_controls:
                scraped_count += 1
                seen.add(ctrl_url)
                log.info(f"[{scraped_count}/{total_controls}] Extracting: {name}")
                driver.get(ctrl_url)
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "h4")))

                solution = extract_solution(driver)
                ws.append([name, solution, ctrl_url])

                # Save partial progress occasionally
                if scraped_count % 10 == 0:
                    wb.save(output_file)

                # Check if limit reached
                if limit and scraped_count >= limit:
                    log.info(f"Reached scraping limit ({limit}). Stopping early.")
                    wb.save(output_file)
                    raise StopIteration

                # Return to main list
                for attempt in range(3):
                    try:
                        driver.back()
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='audits/items/']"))
                        )
                        time.sleep(random.uniform(2.5, 4.5))
                        break
                    except TimeoutException:
                        log.warning(f"Page reload timeout (attempt {attempt + 1}), refreshing...")
                        driver.refresh()
                        time.sleep(5)
                else:
                    log.error("Failed to reload list page after 3 attempts.")

                if len(seen) >= total_controls:
                    break

            if len(seen) >= total_controls:
                log.info(f"Target reached ({len(seen)} controls).")
                break

            try:
                next_btn = driver.find_element(
                    By.XPATH, "//nav[@aria-label='pagination']//button[span[normalize-space()='Next']]"
                )
                if "disabled" in next_btn.get_attribute("class"):
                    log.info("No more pages available.")
                    break
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                next_btn.click()
                time.sleep(3)
                page_num += 1
            except Exception:
                log.info("Pagination ended or not found.")
                break

    except StopIteration:
        log.info("✅ Scraping stopped by limit parameter.")
    except Exception as e:
        log.exception(f"Unexpected error: {e}")
    finally:
        if driver:
            driver.quit()
        try:
            wb.save(output_file)
        except Exception:
            pass
        log.info(f"\n✅ Done! Collected {len(seen)} controls (limited={limit}). Saved to {output_file}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Tenable CIS Benchmarks and export 'Solution' sections to Excel."
    )
    parser.add_argument("--url", required=True, help="Tenable CIS benchmark URL")
    parser.add_argument("--output", default="tenable_scraper_output.xlsx", help="Output Excel filename")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--limit", type=int, help="Maximum number of controls to extract (optional)")
    args = parser.parse_args()

    scrape_tenable(args.url, args.output, headless=args.headless, limit=args.limit)
