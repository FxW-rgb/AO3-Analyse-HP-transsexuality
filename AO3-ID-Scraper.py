# ===============================================
# AO3 Fanfiction ID-Scraper mit Diagnosefunktion & Fortschrittsbalken
# ===============================================

import requests
from bs4 import BeautifulSoup
import argparse
import csv
import time
import sys
import os
from datetime import datetime
from io import StringIO
from tqdm import tqdm  # <- Fortschrittsbalken

# === Standardparameter ===
DELAY = 10
DEFAULT_HEADER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) "
    "Gecko/20100101 Firefox/131.0 ForschungsprojektDH"
)
OUTPUT_FILE = "Scraper_IDs.csv"
LOG_DIR = "logs"

# ==========================================================
# Gemeinsame Logging-Hilfsfunktionen
# ==========================================================
def init_logger(script_name, params, log_dir, log_name):
    os.makedirs(log_dir, exist_ok=True)
    start_time = datetime.now()
    logfile = os.path.join(
        log_dir,
        log_name or f"{script_name}_{start_time.strftime('%Y%m%d_%H%M%S')}.log"
    )

    logger = StringIO()
    logger.write("===== AO3 SCRAPER LOG =====\n")
    logger.write(f"Script: {script_name}\n")
    logger.write(f"Startzeit: {start_time.isoformat(timespec='seconds')}\n")
    logger.write("Parameter / Aufruf:\n")
    for k, v in params.items():
        logger.write(f"  {k}: {v}\n")
    logger.write("==========================\n\n")

    return logger, logfile, start_time


def finalize_logger(logger, logfile, start_time, summary_lines):
    end_time = datetime.now()
    runtime = (end_time - start_time).total_seconds()

    logger.write("\n=== Zusammenfassung ===\n")
    for line in summary_lines:
        logger.write(line + "\n")
    logger.write(f"Laufzeit: {runtime:.1f} Sekunden\n")
    logger.write("===== ENDE =====\n")

    with open(logfile, "w", encoding="utf-8") as f:
        f.write(logger.getvalue())

    return logfile

# ==========================================================
# Diagnosefunktion (UNVERÄNDERT)
# ==========================================================
def diagnose_response(resp, fic_url=""):
    msg = []
    msg.append(f"\n--- Diagnose für Anfrage: {fic_url} ---")
    msg.append(f"Status-Code: {resp.status_code}")
    msg.append("Header:")
    for k, v in resp.headers.items():
        msg.append(f"  {k}: {v}")
    if "cf-ray" in resp.headers or "cloudflare" in resp.text.lower():
        msg.append("Hinweis: Cloudflare blockiert evtl. die Anfrage.")
    if "error" in resp.text.lower() or "denied" in resp.text.lower():
        snippet = resp.text[:300].replace("\n", " ")
        msg.append(f"Möglicher Fehlertext: {snippet} ...")
    msg.append("--- Ende Diagnose ---\n")
    return "\n".join(msg)

# ==========================================================
# IDs extrahieren mit Fortschrittsbalken
# ==========================================================
def get_work_ids(search_url, num_to_retrieve, header_info, delay, logger):
    headers = {"User-Agent": header_info}
    seen_ids = set()
    all_ids = []

    logger.write(f"Starte Scraping für: {search_url}\n")
    logger.write(f"Maximal abzurufende IDs: {num_to_retrieve}\n")

    page = 1
    pbar = tqdm(total=num_to_retrieve, desc="IDs sammeln", ncols=90)

    while len(all_ids) < num_to_retrieve:
        page_url = f"{search_url}&page={page}"
        try:
            resp = requests.get(page_url, headers=headers)
        except Exception as e:
            logger.write(f"Verbindungsfehler: {e}\n")
            break

        if resp.status_code != 200:
            logger.write(f"Fehler {resp.status_code} auf Seite {page}\n")
            logger.write(diagnose_response(resp, page_url))
            break

        soup = BeautifulSoup(resp.text, "lxml")
        works = soup.find_all("li", class_="work")
        if not works:
            logger.write("Keine weiteren Ergebnisse gefunden.\n")
            break

        for work in works:
            link = work.find("a", href=True)
            if link and "/works/" in link["href"]:
                work_id = link["href"].split("/works/")[-1].split("?")[0]
                if work_id not in seen_ids:
                    seen_ids.add(work_id)
                    all_ids.append(work_id)
                    pbar.update(1)
                    if len(all_ids) >= num_to_retrieve:
                        break

        logger.write(f"Seite {page} verarbeitet, {len(all_ids)} IDs gesammelt.\n")
        page += 1
        time.sleep(delay)

    pbar.close()
    return all_ids

# ==========================================================
# CSV speichern (UNVERÄNDERT)
# ==========================================================
def save_to_csv(ids, out_csv, logger):
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["work_id"])
        for wid in ids:
            writer.writerow([wid])
    logger.write(f"{len(ids)} IDs gespeichert in: {out_csv}\n")

# ==========================================================
# Hauptprogramm
# ==========================================================
def main():
    parser = argparse.ArgumentParser(description="Scrape AO3 work IDs with error diagnostics.")
    parser.add_argument("search_url")
    parser.add_argument("--out_csv", default=OUTPUT_FILE)
    parser.add_argument("--num_to_retrieve", type=int, default=100)
    parser.add_argument("--header", default=DEFAULT_HEADER)
    parser.add_argument("--log_dir", default=LOG_DIR)
    parser.add_argument("--log_name", default=None)
    parser.add_argument("--delay", type=int, default=DELAY)

    args = parser.parse_args()

    logger, logfile, start_time = init_logger(
        script_name="ao3_ids",
        params={
            "search_url": args.search_url,
            "out_csv": args.out_csv,
            "num_to_retrieve": args.num_to_retrieve,
            "header": args.header,
            "delay": args.delay
        },
        log_dir=args.log_dir,
        log_name=args.log_name
    )

    ids = get_work_ids(args.search_url, args.num_to_retrieve, args.header, args.delay, logger)
    if ids:
        save_to_csv(ids, args.out_csv, logger)
    else:
        logger.write("Keine IDs gefunden oder Fehler beim Abruf.\n")

    logfile = finalize_logger(
        logger,
        logfile,
        start_time,
        summary_lines=[
            f"IDs gesammelt: {len(ids)}",
            f"Ausgabe-CSV: {args.out_csv}"
        ]
    )

    print("Log-Datei gespeichert unter:", logfile)
    print(logger.getvalue())


if __name__ == "__main__":
    main()
