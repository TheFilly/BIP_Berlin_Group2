from pathlib import Path
from typing import Dict, List, Iterable
import json

try:
    import yaml  # optional
except Exception:
    yaml = None

DBSchema = Dict[str, Dict[str, object]]  # key -> {"year": str, "description": str, "pictures": List[str]}

def _dedup_keep_order(items: Iterable[str], case_insensitive: bool = True) -> List[str]:
    seen = set()
    out: List[str] = []
    for s in items:
        k = s.lower() if case_insensitive else s
        if k not in seen:
            seen.add(k)
            out.append(s)
    return out

def load_db(path: Path) -> DBSchema:
    if not path.exists():
        return {}
    if path.suffix.lower() in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("PyYAML nicht installiert. Installiere mit: pip install pyyaml")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:  # JSON default
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    # Schema absichern
    db: DBSchema = {}
    for k, v in (data or {}).items():
        pics = v.get("pictures", []) if isinstance(v, dict) else []
        db[k] = {
            "year": str(v.get("year", "")) if isinstance(v, dict) else "",
            "description": str(v.get("description", "")) if isinstance(v, dict) else "",
            "pictures": _dedup_keep_order([str(p) for p in pics]),
        }
    return db

def save_db(db: DBSchema, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("PyYAML nicht installiert. Installiere mit: pip install pyyaml")
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(db, f, allow_unicode=True, sort_keys=True)
    else:  # JSON default
        with open(path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2, sort_keys=True)

def upsert_record(db: DBSchema, key: str, year: str, description: str, pic_names: Iterable[str]) -> None:
    """
    Fügt (key) hinzu oder aktualisiert vorhandenen Eintrag.
    - year/description werden überschrieben, wenn übergeben.
    - pictures werden gemerged (case-insensitive dedup, Reihenfolge bleibt erhalten).
    """
    key = str(key).strip()
    year = str(year).strip()
    description = str(description).strip()
    pics_new = [str(p).strip() for p in pic_names if str(p).strip()]

    if key not in db:
        db[key] = {"year": year, "description": description, "pictures": _dedup_keep_order(pics_new)}
        return

    rec = db[key]
    if year:
        rec["year"] = year
    if description:
        rec["description"] = description
    rec["pictures"] = _dedup_keep_order([*rec.get("pictures", []), *pics_new])

