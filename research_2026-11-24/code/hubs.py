"""Nearest commercial ports and airports for each production site.

Uses the checked-in WPI and OurAirports snapshots and the existing repository
loaders. Ports are geographic candidates; cargo/commodity suitability unverified.
Airports are scheduled medium/large facilities, not necessarily cargo airports.
Distances are great-circle km. Returns the actual nearest three; the original
10 km exclusion is disabled because it could skip a genuinely closer facility.
"""
import csv, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'code'))
from build_full_supply_chain_evidence import load_ports as repository_ports
from build_full_supply_chain_evidence import load_airports as repository_airports

def hav(a, b, c, d):
    R = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def load_ports():
    return [dict(id=p['hub_id'],name=p['hub_name'],country=p['country'],lat=p['latitude'],lon=p['longitude'],
                 cls='WPI port candidate',extra='Cargo suitability unverified') for p in repository_ports()]

def load_airports():
    return [dict(id=p['hub_id'],name=p['hub_name'],country=p['country'],lat=p['latitude'],lon=p['longitude'],
                 cls='scheduled medium/large airport',extra='Cargo suitability unverified') for p in repository_airports()]

def nearest(lat, lon, hubs, k=3, sep=0.0):
    ranked = sorted(((hav(lat, lon, h["lat"], h["lon"]), h) for h in hubs), key=lambda t: t[0])
    chosen = []
    for d, h in ranked:
        if any(hav(h["lat"], h["lon"], c["lat"], c["lon"]) < sep for _, c in chosen):
            continue
        chosen.append((d, h))
        if len(chosen) == k:
            break
    return chosen

if __name__ == "__main__":
    fac_csv, out_csv = sys.argv[1], sys.argv[2]
    ports, airports = load_ports(), load_airports()
    print(len(ports), "commercial ports;", len(airports), "commercial airports")
    rows = []
    for f in csv.DictReader(open(fac_csv, encoding="utf-8")):
        if not f.get("latitude") or not f.get("longitude"):
            continue
        lat, lon = float(f["latitude"]), float(f["longitude"])
        for typ, hubs in (("seaport", ports), ("airport", airports)):
            for r, (d, h) in enumerate(nearest(lat, lon, hubs), 1):
                rows.append(dict(site_id=f.get('site_id',f.get('facility_id')), site_name=f.get('site_name',f.get('facility_name')), vendor_name=f.get('vendor_name',f.get('company')),
                                 site_country=f["country"], hub_type=typ, rank=r, hub_code=h["id"], hub_name=h["name"],
                                 hub_country=h["country"], hub_class=h["cls"], hub_note=h["extra"],
                                 hub_latitude=h["lat"], hub_longitude=h["lon"], great_circle_km=round(d, 1),
                                 site_coordinate_precision=f.get("coordinate_precision", ""),
                                 hub_source="Repository NGA World Port Index snapshot" if typ == "seaport" else "Repository OurAirports snapshot"))
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        if not rows:
            raise ValueError('No geocoded production-site rows; no nearest-hub result can be written')
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(len(rows), "hub rows")
