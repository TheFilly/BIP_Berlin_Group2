from pathlib import Path
import pandas as pd
import re
import math
import shutil
from typing import List, Iterable, Set


import helper.filePaths as filePaths



def readColumns(path: Path, start_row: int, end_row: int, sheet_name=0):
   
    engine = "xlrd" if path.suffix.lower() == ".xls" else None

    # genau die vier Spalten laden (in dieser Reihenfolge)
    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        usecols="E,CA,CD,CE",
        engine=engine
    )

    # DataFrame-Indizes aus Excel-Zeilen (Header in Zeile 1 angenommen)
    start_idx = max(0, start_row - 2)
    end_idx_exclusive = max(0, end_row - 1)

    df_slice = df.iloc[start_idx:end_idx_exclusive]

    # Spalten in der Reihenfolge E, CA, CD, CE ausgeben
    col_E, col_CA, col_CD, col_CE = df.columns.tolist()
    rows_as_tuples = [(row[col_E], row[col_CA], row[col_CD], row[col_CE]) for _, row in df_slice.iterrows()]
    return rows_as_tuples

def transform_e_value(e_value):

    if e_value is None or (isinstance(e_value, float) and math.isnan(e_value)):
        return None, None

    s = str(e_value).strip()

    m = re.search(r'^[^/]*?/(\d{4})', s)
    year = m.group(1) if m else None

    return year

def extract_jpg_filenames(cd_value) -> List[str]:
    
    if cd_value is None or (isinstance(cd_value, float) and math.isnan(cd_value)):
        return []

    s = str(cd_value)

    # Dateinamen matchen (alles außer verbotene/Trennzeichen), die auf ".jpg" enden
    pattern = re.compile(r'([^\s\\/:*?"<>|]+\.(?:jpg))', re.IGNORECASE)
    matches = pattern.findall(s)

    # Doppelte entfernen, Reihenfolge beibehalten
    seen = set()
    unique = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            unique.append(m)
    return unique

def copy_pictures(pic_names, source_dir_year: Path, target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    filePaths.log_missing_pictures.parent.mkdir(parents=True, exist_ok=True)

    # Bereits geloggte Namen laden (falls Datei existiert)
    existing = set()
    if filePaths.log_missing_pictures.exists():
        with open(filePaths.log_missing_pictures, "r", encoding="utf-8") as f:
            existing = {line.strip() for line in f if line.strip()}

    copied = 0
    missing_names_this_run = set()  # innerhalb dieses Laufs deduplizieren

    for name in pic_names:
        src = source_dir_year / name
        if src.exists():
            shutil.copy2(src, target_dir / src.name)
            copied += 1
        else:
            # Fallback: case-insensitive Suche
            candidates = [p for p in source_dir_year.glob("*") if p.name.lower() == name.lower()]
            if candidates:
                shutil.copy2(candidates[0], target_dir / candidates[0].name)
                copied += 1
            else:
                missing_names_this_run.add(name)  # nur der Name

    # Nur neue, noch nicht geloggte Namen anhängen
    to_write = [n for n in sorted(missing_names_this_run) if n not in existing]
    if to_write:
        with open(filePaths.log_missing_pictures, "a", encoding="utf-8") as f:
            for n in to_write:
                f.write(n + "\n")

    print(
        f"Fertig: {copied} kopiert, "
        f"{len(missing_names_this_run)} nicht gefunden "
        f"({len(to_write)} neu ins Log geschrieben). "
        f"Log: {filePaths.log_missing_pictures if to_write else '—'}"
    )
    return copied, len(missing_names_this_run), len(to_write)

def extractID(pic_names: Iterable[str]) -> Set[str]:
    extractedID = set()
    for name in pic_names:
        stem = Path(name).stem   # ohne Endung (.jpg/.JPG)
        parts = stem.split("-")
        if len(parts) > 1:
            obername = "-".join(parts[:-1])  # alles außer die letzten drei Ziffern
            extractedID.add(obername)
    return extractedID

