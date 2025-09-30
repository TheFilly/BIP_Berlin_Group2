from pathlib import Path
import pandas as pd
import re
import math
import shutil
from typing import List

# === Pfade ===
metadata_liste2 = Path("/Users/filly/Documents/Uni - HTW/IuG/Data/Objektdaten/liste2.xls") 
metadata_liste3 = Path("/Users/filly/Documents/Uni - HTW/IuG/Data/Objektdaten/liste3.xls") 
source_pics = Path("/Users/filly/Documents/Uni - HTW/IuG/Data/Objektbilder")
target_dir_list2 = Path("/Users/filly/Documents/Uni - HTW/IuG/Code/Pictures/List2")
target_dir_list3 = Path("/Users/filly/Documents/Uni - HTW/IuG/Code/Pictures/List3")
log_missing_pictures = Path("/Users/filly/Documents/Uni - HTW/IuG/Code/Pictures/missingPictures.txt")

def read_e_and_cd(path: Path, start_row: int, end_row: int, sheet_name=0):

    df = pd.read_excel(
        path,
        sheet_name=sheet_name,
        usecols="E,CD",       
        engine="xlrd" if path.suffix.lower()==".xls" else None
    )

    col_E, col_CD = df.columns[0], df.columns[1]

    start_idx = max(0, start_row - 2)
    end_idx_exclusive = max(0, end_row - 1) 

    df_slice = df.iloc[start_idx:end_idx_exclusive]

    rows_as_tuples = [(row[col_E], row[col_CD]) for _, row in df_slice.iterrows()]
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
    log_missing_pictures.parent.mkdir(parents=True, exist_ok=True)

    # Bereits geloggte Namen laden (falls Datei existiert)
    existing = set()
    if log_missing_pictures.exists():
        with open(log_missing_pictures, "r", encoding="utf-8") as f:
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
        with open(log_missing_pictures, "a", encoding="utf-8") as f:
            for n in to_write:
                f.write(n + "\n")

    print(
        f"Fertig: {copied} kopiert, "
        f"{len(missing_names_this_run)} nicht gefunden "
        f"({len(to_write)} neu ins Log geschrieben). "
        f"Log: {log_missing_pictures if to_write else '—'}"
    )
    return copied, len(missing_names_this_run), len(to_write)

start_row_list2 = 301
end_row_list2 = 600

start_row_list3 = 1
end_row_list3 = 500

rows_list2 = read_e_and_cd(metadata_liste2, start_row_list2, end_row_list2)
rows_list3 = read_e_and_cd(metadata_liste3, start_row_list3, end_row_list3)


for e_value, cd_value in rows_list2:
    year = transform_e_value(e_value)
    source_dir_year = Path(f"{source_pics}/{year}")
    pic_names = extract_jpg_filenames(cd_value)
    copy_pictures(pic_names, source_dir_year, target_dir_list2)

for e_value, cd_value in rows_list3:
    year = transform_e_value(e_value)
    source_dir_year = Path(f"{source_pics}/{year}")
    pic_names = extract_jpg_filenames(cd_value)
    copy_pictures(pic_names, source_dir_year, target_dir_list3)





