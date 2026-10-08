#!/usr/bin/env python3
from pathlib import Path
import sqlite3

root = Path(__file__).resolve().parents[1]
db_path = root / "var" / "modeling-lab.sqlite"
schema_path = root / "db" / "schema.sql"

db_path.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(db_path) as conn:
    conn.executescript(schema_path.read_text())
    conn.commit()

print(f"initialized: {db_path}")
