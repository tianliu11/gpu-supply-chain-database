"""Nearest commercial ports and airports for each production site.

Ports: NGA Pub.150 World Port Index (2019) via github.com/tayljordan/ports.
  commercial = harbor size Major/Minor/Small (WPI Large/Medium/Small) AND a recorded cargo pier
  (excludes Very Small harbors, fishing/yacht harbors and oil-terminal-only islands).
Airports: OurAirports (github.com/davidmegginson/ourairports-data).
  commercial = large_airport or medium_airport with scheduled_service = yes.
Distances are great-circle (haversine) km. Up to 3 of each; a hub within 10 km of an
already-chosen hub of the same type is skipped so the three options are distinct facilities.
"""
import csv, json, math, sys

EXT = "/home/claude/ext"

def hav(a, b, c, d):
    R = 6371.0088
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

def load_ports():
    P = json.load(open(f"{EXT}/tayljordan_ports/ports.json"))["ports"]
    out = []
    for p in P:
        if p.get("port_size") in ("Major", "Minor", "Small") and p.get("cargo_pier_depth_max_m") is not None:
            size = {"Major": "large", "Minor": "medium", "Small": "small"}[p["port_size"]]
            out.append(dict(id=f"WPI{p['wpi_port_id']}", name=p["wpi_port_name"].title(), country=p.get("country") or "",
                            lat=p["latitude"], lon=p["longitude"], cls=f"WPI harbor size {size}",
                            extra=p.get("max_vessel_size") or ""))
    return out

def load_airports():
    out = []
    for a in csv.DictReader(open(f"{EXT}/davidmegginson_ourairports-data/airports.csv", encoding="utf-8")):
        if a["type"] in ("large_airport", "medium_airport") and a["scheduled_service"] == "yes":
            code = a["iata_code"] or a["icao_code"] or a["ident"]
            out.append(dict(id=code, name=a["name"], country=a["iso_country"], lat=float(a["latitude_deg"]),
                            lon=float(a["longitude_deg"]), cls=a["type"], extra=a["municipality"]))
    return out

def nearest(lat, lon, hubs, k=3, sep=10.0):
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
                rows.append(dict(site_id=f["site_id"], site_name=f["site_name"], vendor_name=f["vendor_name"],
                                 site_country=f["country"], hub_type=typ, rank=r, hub_code=h["id"], hub_name=h["name"],
                                 hub_country=h["country"], hub_class=h["cls"], hub_note=h["extra"],
                                 hub_latitude=h["lat"], hub_longitude=h["lon"], great_circle_km=round(d, 1),
                                 site_coordinate_precision=f.get("coordinate_precision", ""),
                                 hub_source="NGA World Port Index Pub.150 (2019)" if typ == "seaport" else "OurAirports"))
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(len(rows), "hub rows")
