"""Offline city-level geocoder: UN/LOCODE (UNECE, via github.com/datasets/un-locode) with
OurAirports municipality only as an explicitly enabled fallback. Returns
(lat, lon, method) or None. City proxies are never factory-gate coordinates."""
import csv, re, unicodedata, os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXT = os.environ.get('GPU_GEODATA_DIR',str(ROOT/'data/external'))

def records(path):
    if not Path(path).exists(): return []
    with open(path,encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
ALIAS = {"south korea": "KR", "korea": "KR", "republic of korea": "KR", "taiwan": "TW", "united states": "US", "usa": "US",
         "united kingdom": "GB", "uk": "GB", "russia": "RU", "vietnam": "VN", "viet nam": "VN", "czech republic": "CZ", "czechia": "CZ",
         "iran": "IR", "laos": "LA", "bolivia": "BO", "venezuela": "VE", "tanzania": "TZ", "dr congo": "CD",
         "democratic republic of the congo": "CD", "drc": "CD", "congo (drc)": "CD", "republic of the congo": "CG",
         "china": "CN", "mainland china": "CN", "hong kong": "HK", "macau": "MO", "the netherlands": "NL", "netherlands": "NL",
         "turkey": "TR", "türkiye": "TR", "turkiye": "TR", "ivory coast": "CI", "côte d'ivoire": "CI", "brunei": "BN",
         "syria": "SY", "moldova": "MD", "north macedonia": "MK", "palestine": "PS", "uae": "AE", "united arab emirates": "AE",
         "kazakhstan": "KZ", "kyrgyzstan": "KG", "eswatini": "SZ", "myanmar": "MM", "burma": "MM", "cape verde": "CV",
         "philippines": "PH", "slovakia": "SK", "scotland": "GB", "england": "GB", "wales": "GB", "puerto rico": "PR"}

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(city|shi|si|gun|ku|county|prefecture|province|district|town|township|village|municipality)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", "", s)

def _coord(c):
    m = re.match(r"(\d{2})(\d{2})([NS])\s+(\d{3})(\d{2})([EW])", c or "")
    if not m: return None
    lat = int(m[1]) + int(m[2]) / 60; lon = int(m[4]) + int(m[5]) / 60
    return (-lat if m[3] == "S" else lat, -lon if m[6] == "W" else lon)

CC = {}
for r in records(f"{EXT}/datasets_un-locode/data/country-codes.csv"):
    CC[r["CountryName"].lower()] = r["CountryCode"]
CC.update(ALIAS)

IDX = {}
for r in records(f"{EXT}/datasets_un-locode/data/code-list.csv"):
    c = _coord(r["Coordinates"])
    if not c: continue
    for nm in (r["Name"], r["NameWoDiacritics"]):
        IDX.setdefault((r["Country"], norm(nm)), []).append((c, r["Subdivision"]))
SUB = {}
for r in records(f"{EXT}/datasets_un-locode/data/subdivision-codes.csv"):
    SUB[(r["SUCountry"], r["SUCode"])] = norm(r["SUName"])
AIRP = {}
for a in records(ROOT/'data/raw/ourairports_airports.csv'):
    if a["municipality"]:
        AIRP.setdefault((a["iso_country"], norm(a["municipality"])), (float(a["latitude_deg"]), float(a["longitude_deg"])))

def iso2(country):
    c = (country or "").strip().lower()
    if len(c) == 2: return c.upper()
    return CC.get(c) or next((v for k, v in CC.items() if k.startswith(c) and len(c) > 3), None)

def geocode(city, state, country, allow_airport_proxy=False):
    # Reuse only unambiguous, exact locality matches from the existing cache.
    # This fallback neither invents missing UN/LOCODE data nor treats a factory
    # city as an exact factory gate.
    cached=[]
    for f in records(ROOT/'data/clean/full_supply_chain_facilities.csv'):
        if norm(f['city'])==norm(city) and norm(f['country'])==norm(country) and f['latitude'] and f['longitude']:
            if state and norm(state) not in norm(f['geocode_display_name']): continue
            cached.append((float(f['latitude']),float(f['longitude']),f['coordinate_precision']))
    if len({(a,b) for a,b,_ in cached})==1:
        return cached[0]
    cc = iso2(country)
    if not cc: return None
    cands = [city] + re.split(r"[,/;()]| - ", city or "")
    ns = norm(state)
    for nm in cands:
        n = norm(nm)
        if len(n) < 3 or (cc, n) not in IDX: continue
        opts = IDX[(cc, n)]
        if ns:
            m = [o for o in opts if SUB.get((cc, o[1]), "") and (SUB[(cc, o[1])] in ns or ns in SUB[(cc, o[1])])]
            if m: return (*m[0][0], "UN/LOCODE city centroid")
        if len({(round(o[0][0],6), round(o[0][1],6)) for o in opts}) == 1:
            return (*opts[0][0], "UN/LOCODE city centroid")
        # Do not pick the first of several distinct same-name municipalities.
    if ns and (cc, ns) in IDX:   # prefecture/state capital of the same name, only if subdivision agrees
        m = [o for o in IDX[(cc, ns)] if SUB.get((cc, o[1]), "") == ns]
        if m: return (*m[0][0], "UN/LOCODE state-capital proxy")
    if not allow_airport_proxy: return None
    for nm in cands:
        n = norm(nm)
        if len(n) >= 3 and (cc, n) in AIRP:
            return (*AIRP[(cc, n)], "OurAirports municipality proxy")
    return None

if __name__ == "__main__":
    for t in [("Hsinchu", "", "Taiwan"), ("Burghausen", "Bavaria", "Germany"), ("Imari", "Saga", "Japan"),
              ("Pyeongtaek", "Gyeonggi", "South Korea"), ("Ogaki", "Gifu", "Japan"), ("Kulim", "Kedah", "Malaysia")]:
        print(t, geocode(*t))
