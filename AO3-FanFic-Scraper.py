# ===============================================
# AO3 Fanfiction Scraper mit Fortschrittsanzeige & Logging
# ===============================================

import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import socket
from unidecode import unidecode
from datetime import datetime
from tqdm.notebook import tqdm
import pandas as pd
from io import StringIO
import argparse

# === Standardparameter ===
DELAY = 10
DEFAULT_HEADER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) "
    "Gecko/20100101 Firefox/131.0"
)
OUTPUT_DIR = "Ausgabedokumente"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ordner automatisch anlegen

# ==========================================================
# Logging-Hilfsfunktionen
# ==========================================================
def init_logger(script_name, params, log_dir, log_name=None):
    os.makedirs(log_dir, exist_ok=True)
    start_time = datetime.now()
    logfile = os.path.join(
        log_dir,
        log_name if log_name else f"{script_name}_{start_time.strftime('%Y%m%d_%H%M%S')}.log"
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
# Diagnosefunktionen
# ==========================================================
def diagnose_environment():
    try:
        socket.create_connection(("archiveofourown.org", 80), timeout=5)
    except OSError:
        print("⚠ Keine Verbindung zu AO3. Bitte Internet prüfen.", flush=True)

# ==========================================================
# Hilfsfunktionen
# ==========================================================
def get_tag_info(category, meta):
    try:
        tag_list = meta.find("dd", class_=f"{category} tags").find_all(class_="tag")
        return [unidecode(t.text) for t in tag_list]
    except AttributeError:
        return []

def get_tags(meta):
    tags = ["rating", "category", "fandom", "relationship", "character", "freeform"]
    return [get_tag_info(tag, meta) for tag in tags]

def access_denied(soup):
    return soup.find(class_="flash error") or not soup.find("dl", class_="work meta group")

# ==========================================================
# Kernfunktion zum Scrapen einzelner Works
# ==========================================================
def write_fic_to_csv(fic_id, meta_writer, text_writer, errorwriter, header_info):
    url = f"https://archiveofourown.org/works/{fic_id}?view_adult=true&view_full_work=true"
    headers = {"User-Agent": header_info}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
    except Exception as e:
        errorwriter.writerow([fic_id, f"Verbindungsfehler: {e}"])
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    if access_denied(soup):
        errorwriter.writerow([fic_id, "Access Denied"])
        return False

    meta = soup.find("dl", class_="work meta group")
    title = unidecode(soup.find("h2", class_="title heading").text.strip())
    tags = get_tags(meta)

    content = soup.find("div", id="chapters")
    paragraphs = [unidecode(p.text) for p in content.select("p")] if content else []
    chaptertext = "\n\n".join(paragraphs)

    meta_writer.writerow([
        fic_id,
        title,
        ", ".join(tags[0]),  # rating
        ", ".join(tags[1]),  # category
        ", ".join(tags[3]),  # relationship
        ", ".join(tags[4]),  # character
        ", ".join(tags[5])   # freeform
    ])

    text_writer.writerow([fic_id, chaptertext])
    return True

# ==========================================================
# Hauptfunktion
# ==========================================================
def run_scraper(
    input_csv,
    text_csv,
    meta_csv,
    error_csv,
    delay=DELAY,
    header_info=DEFAULT_HEADER,
    log_dir=OUTPUT_DIR,
    log_name=None
):
    logger, logfile, start_time = init_logger(
        script_name="ao3_works",
        params={
            "input_csv": input_csv,
            "text_csv": text_csv,
            "meta_csv": meta_csv,
            "delay": delay,
            "header": header_info
        },
        log_dir=log_dir,
        log_name=log_name
    )

    diagnose_environment()

    input_path = os.path.join(OUTPUT_DIR, input_csv) if not os.path.isabs(input_csv) else input_csv
    fic_ids = pd.read_csv(input_path).iloc[:, 0].astype(str).tolist()
    if fic_ids[0].lower().startswith("work"):
        fic_ids = fic_ids[1:]

    text_path = os.path.join(OUTPUT_DIR, text_csv)
    meta_path = os.path.join(OUTPUT_DIR, meta_csv)
    error_path = os.path.join(OUTPUT_DIR, error_csv)

    with open(text_path, "a", encoding="utf-8", newline="") as f_text, \
         open(meta_path, "a", encoding="utf-8", newline="") as f_meta, \
         open(error_path, "a", encoding="utf-8", newline="") as f_err:

        text_writer = csv.writer(f_text)
        meta_writer = csv.writer(f_meta)
        errorwriter = csv.writer(f_err)

        if os.stat(text_path).st_size == 0:
            text_writer.writerow(["work_id", "text"])
        if os.stat(meta_path).st_size == 0:
            meta_writer.writerow([
                "work_id", "title",
                "rating", "category",
                "relationship", "character", "freeform"
            ])
        if os.stat(error_path).st_size == 0:
            errorwriter.writerow(["work_id", "error"])

        for idx, fic_id in enumerate(fic_ids, start=1):
            write_fic_to_csv(fic_id, meta_writer, text_writer, errorwriter, header_info)
            print(f"[{idx}/{len(fic_ids)}] Work ID {fic_id} verarbeitet.")
            time.sleep(delay)

    logfile = finalize_logger(
        logger,
        logfile,
        start_time,
        summary_lines=[
            f"Verarbeitete Works: {len(fic_ids)}",
            f"Text-CSV: {text_path}",
            f"Meta-CSV: {meta_path}",
            f"Fehlerdatei: {error_path}"
        ]
    )

    return logfile

# ==========================================================
# CLI-Unterstützung
# ==========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape AO3 FanFics by work IDs.")
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--text_csv", default="works_text.csv")
    parser.add_argument("--meta_csv", default="works_meta.csv")
    parser.add_argument("--error_csv", default="errors.csv")
    parser.add_argument("--delay", type=int, default=DELAY)
    parser.add_argument("--header", default=DEFAULT_HEADER)
    parser.add_argument("--log_dir", default=OUTPUT_DIR)
    parser.add_argument("--log_name", default=None)
    args = parser.parse_args()

    logfile = run_scraper(
        input_csv=args.input_csv,
        text_csv=args.text_csv,
        meta_csv=args.meta_csv,
        error_csv=args.error_csv,
        delay=args.delay,
        header_info=args.header,
        log_dir=args.log_dir,
        log_name=args.log_name
    )
    print("Log-Datei gespeichert unter:", logfile)
