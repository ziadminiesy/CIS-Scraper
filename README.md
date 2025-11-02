# 🧩 CIS Benchmark Scraper

**Automated unified scraper for CIS Benchmark controls and solutions**  
Supports both **Tenable** and **CIS WorkBench** benchmark pages.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Selenium](https://img.shields.io/badge/Selenium-Automation-orange.svg)
![Excel](https://img.shields.io/badge/Output-Excel-lightgrey.svg)
![Platforms](https://img.shields.io/badge/Supports-Windows%20%7C%20macOS%20%7C%20Linux-purple.svg)

---

## ⚡ Quick Start

**Tenable Example**
```bash
python cis_scraper.py --url https://www.tenable.com/audits/CIS_PostgreSQL_17_v1.0.0_L1_Database   --output postgres_controls.xlsx   --limit 20
```

**CIS WorkBench Example**
```bash
python cis_scraper.py   --url https://workbench.cisecurity.org/benchmarks/20223   --cookies cookies.json   --output cis_mysql_controls.xlsx   --limit 10
```

---

## 📘 Overview

The **CIS Benchmark Scraper** is an open-source Python tool that automates the extraction of CIS benchmark controls, solutions, and related details from:

* [🔹 Tenable CIS audit pages](https://www.tenable.com/audits)
* [🔹 CIS WorkBench benchmarks](https://workbench.cisecurity.org/benchmarks)

It detects the platform automatically from the URL and exports all extracted data to an **Excel (.xlsx)** file for compliance review, documentation, or analysis.

---

## 🚀 Features

* 🧠 **Auto-detects source** — identifies Tenable vs. WorkBench automatically  
* 🧩 Extracts:
  * Control name (and ID)
  * Description (first sentence)
  * Solution / remediation steps
  * Source URL  
* ⚙️ Optional `--limit` to scrape only the first *N* controls  
* 🪄 Automatically installs a compatible ChromeDriver  
* 📊 Real-time progress logging (`[12/56] Extracting: Control Name`)  
* 📁 Exports structured Excel output  
* 🧱 Modular — can be run as individual scrapers or through one launcher  
* 🧭 Headless or visible browser modes  

---

## 🧱 Folder Structure

```
CIS-Scraper/
├── cis_scraper.py              # Unified launcher (auto-detects Tenable or WorkBench)
├── tenable_scraper.py          # Tenable benchmark scraper
├── workbench_scraper.py        # CIS WorkBench benchmark scraper
├── requirements.txt
├── README.md
└── cookies.json                # (only required for WorkBench)
```

---

## ⚙️ Installation

### 1️⃣ Prerequisites
* Python **3.11+**
* Google Chrome installed on your machine

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ requirements.txt
```txt
selenium>=4.23.0
openpyxl>=3.1.2
chromedriver-autoinstaller>=0.6.3
pandas>=2.2.2
requests>=2.31.0
lxml[html_clean]>=5.2.1
```

---

## 💻 Usage

### 🔹 Unified Launcher (Recommended)
Run everything through one entry point:
```bash
python cis_scraper.py   --url https://www.tenable.com/audits/items/CIS_PostgreSQL_17_v1.0.0_L1_Database   --output postgres_controls.xlsx   --limit 20
```

For CIS WorkBench:
```bash
python cis_scraper.py   --url https://workbench.cisecurity.org/benchmarks/20223   --cookies cookies.json   --output cis_mysql_controls.xlsx   --limit 10
```

---

## 🧩 Individual Scripts (Optional)

### Tenable Benchmark Scraper
```bash
python tenable_scraper.py   --url https://www.tenable.com/audits/items/CIS_PostgreSQL_17_v1.0.0_L1_Database   --limit 5
```

### CIS WorkBench Scraper
```bash
python workbench_scraper.py   --url https://workbench.cisecurity.org/benchmarks/20223   --cookies cookies.json   --limit 5
```

📝 **Cookies file (WorkBench only):**  
You must be logged into CIS WorkBench.  
Export cookies as JSON using a browser extension (e.g., **“Export Cookies JSON”** for Chrome)  
and save them as `cookies.json` in the same folder.

---

## ⚙️ Command-Line Arguments

| Argument | Description | Required | Default |
|-----------|--------------|-----------|----------|
| `--url` | Benchmark URL (Tenable or WorkBench) | ✅ Yes | — |
| `--cookies` | Path to cookies JSON file (Workbench only) | ❌ No | None |
| `--output` | Output Excel filename | ❌ No | `output.xlsx` |
| `--limit` | Maximum number of controls to scrape | ❌ No | No limit |
| `--headless` | Run Chrome without opening a window | ❌ No | Disabled |

---

## 🗂️ Output Example

| Control | Description | Solution | URL |
|----------|--------------|-----------|-----|
| Ensure 'log_connections' is enabled | Enables logging for successful connections... | Set `log_connections=on` in `postgresql.conf`... | https://... |
| Ensure password lifetime is ≤ 365 days | Enforces regular password rotation... | Set `password_lifetime=365`... | https://... |

The result is saved to `output.xlsx` in your working directory.

---

## 🧠 Logging

Progress is printed to the console:
```
15:23:14 - INFO: Detected source: Tenable
15:23:17 - INFO: Scraping page 1...
15:24:02 - INFO: ✅ Done! Collected 56 controls. Saved to postgres_controls.xlsx
```

---

## 🧑‍💻 Use Cases

* Automate CIS Benchmark documentation  
* Build internal control mapping datasets  
* Feed controls into GRC or compliance dashboards  
* Validate configurations against CIS benchmarks  

---

## 🧪 License

This project is licensed under the **MIT License** — you’re free to use, modify, and distribute it.

```
MIT License © 2025 Ziad Miniesy
```

---

## 🤝 Contributing

Contributions, pull requests, and feature suggestions are welcome!  
If you find a bug or want to add a new benchmark source:

1. Fork the repository  
2. Create a feature branch  
3. Submit a pull request  

---

## 🌐 Author

**Ziad Miniesy**  
Cybersecurity Engineer  
📧 [ziad.miniesy@pwc.com](mailto:ziad.miniesy@pwc.com)

---

## 🏷️ GitHub Tags
```
CIS, Tenable, WorkBench, Cybersecurity, Compliance, Automation, Python, Selenium, OpenSource, Benchmark
```
