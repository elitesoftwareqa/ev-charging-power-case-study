#!/usr/bin/env python3
"""Flatten Open Charge Map (ocm-export) data to a California-only CSV.

Usage:
    python3 ocm_california.py [REPO_DIR] [OUTPUT_CSV]

Defaults: REPO_DIR=~/open_charge_map  OUTPUT_CSV=./california_ev_chargers.csv

Output: one row per connector group (a location can have several), so each row
describes a piece of charging hardware: connector type, current type
(AC/DC), level, kW, amps, volts, and quantity, plus location/operator info.
"""
import csv
import json
import os
import sys
from pathlib import Path

repo = Path(sys.argv[1] if len(sys.argv) > 1 else "~/open_charge_map").expanduser()
out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "california_ev_chargers.csv")
data_dir = repo / "data"

# StateOrProvince is free text in OCM, so match common spellings and also
# fall back to a bounding box around California for records with no state.
CA_NAMES = {"california", "ca", "calif", "calif.", "ca.", "cali"}
LAT_MIN, LAT_MAX = 32.5, 42.1
LON_MIN, LON_MAX = -124.5, -114.1


def is_california(addr):
    state = (addr.get("StateOrProvince") or "").strip().lower()
    if state:
        return state in CA_NAMES
    lat, lon = addr.get("Latitude"), addr.get("Longitude")
    if lat is None or lon is None:
        return False
    return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX


ref = json.loads((data_dir / "referencedata.json").read_text(encoding="utf-8"))


def lookup(key):
    return {x["ID"]: x for x in ref.get(key, [])}


conn_types = lookup("ConnectionTypes")
current_types = lookup("CurrentTypes")
levels = lookup("ChargerTypes")
operators = lookup("Operators")
statuses = lookup("StatusTypes")
usage = lookup("UsageTypes")


def title(table, key):
    item = table.get(key)
    return item.get("Title") if item else None


FIELDS = [
    "poi_id", "uuid", "name", "address", "city", "state", "postcode",
    "latitude", "longitude", "operator", "usage_type", "poi_status",
    "number_of_points", "date_created", "date_last_verified",
    "connection_type", "connection_formal_name", "current_type", "charge_level",
    "power_kw", "amps", "voltage", "connector_quantity", "connector_status",
]

us_dir = data_dir / "US"
rows = pois = 0
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    for name in sorted(os.listdir(us_dir)):
        if not name.endswith(".json"):
            continue
        try:
            poi = json.loads((us_dir / name).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"skipping {name}: {e}", file=sys.stderr)
            continue
        addr = poi.get("AddressInfo") or {}
        if not is_california(addr):
            continue
        pois += 1
        base = {
            "poi_id": poi.get("ID"),
            "uuid": poi.get("UUID"),
            "name": addr.get("Title"),
            "address": addr.get("AddressLine1"),
            "city": addr.get("Town"),
            "state": addr.get("StateOrProvince"),
            "postcode": addr.get("Postcode"),
            "latitude": addr.get("Latitude"),
            "longitude": addr.get("Longitude"),
            "operator": title(operators, poi.get("OperatorID")),
            "usage_type": title(usage, poi.get("UsageTypeID")),
            "poi_status": title(statuses, poi.get("StatusTypeID")),
            "number_of_points": poi.get("NumberOfPoints"),
            "date_created": poi.get("DateCreated"),
            "date_last_verified": poi.get("DateLastVerified"),
        }
        for c in poi.get("Connections") or [{}]:
            ct = conn_types.get(c.get("ConnectionTypeID"), {})
            row = dict(base)
            row.update({
                "connection_type": ct.get("Title"),
                "connection_formal_name": ct.get("FormalName"),
                "current_type": title(current_types, c.get("CurrentTypeID")),
                "charge_level": title(levels, c.get("LevelID")),
                "power_kw": c.get("PowerKW"),
                "amps": c.get("Amps"),
                "voltage": c.get("Voltage"),
                "connector_quantity": c.get("Quantity"),
                "connector_status": title(statuses, c.get("StatusTypeID")),
            })
            w.writerow(row)
            rows += 1

print(f"Wrote {rows} connector rows from {pois} California locations to {out_path}")
