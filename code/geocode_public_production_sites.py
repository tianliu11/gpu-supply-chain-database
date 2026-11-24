#!/usr/bin/env python3
"""Cache OSM Nominatim location proxies for officially documented production sites.

Requests are sequential and rate-limited. City/district queries deliberately
produce approximate logistics screening locations, not asserted factory gates.
Failed or country-mismatched results remain missing.
"""
import argparse
import json
import time
import urllib.parse
import urllib.request
import ssl
from pathlib import Path

from additional_public_research import SITES
from build_full_supply_chain_evidence import research_site_id

COUNTRY_CODES = {
 'Mexico':'mx','Italy':'it','Switzerland':'ch','Hong Kong':'hk','Vietnam':'vn','Jordan':'jo',
 'Philippines':'ph',
 'Japan':'jp',
 'Romania':'ro','Malaysia':'my','Ireland':'ie','United Kingdom':'gb',
 'Taiwan':'tw','France':'fr',
 'Kazakhstan':'kz',
 'United States':'us','Canada':'ca','Brazil':'br','Germany':'de','Austria':'at',
 'Netherlands':'nl','Belgium':'be','Spain':'es','South Africa':'za','China':'cn',
 'South Korea':'kr','Indonesia':'id','New Zealand':'nz','Thailand':'th',
 'Singapore':'sg','Chile':'cl','Egypt':'eg','Australia':'au','Mozambique':'mz',
 'Israel':'il','Peru':'pe','Saudi Arabia':'sa','Papua New Guinea':'pg','India':'in','Finland':'fi',
}
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'data/raw/public_site_geocodes.json'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--retry-missing',action='store_true')
    args=parser.parse_args()
    cache=json.loads(CACHE.read_text()) if CACHE.exists() else {}
    previous=0.0
    for site in SITES:
        fid=research_site_id(site)
        if fid in cache and (cache[fid].get('latitude') is not None or not args.retry_missing):
            continue
        query=site['city']+', '+site['country']
        params=dict(q=query,format='jsonv2',addressdetails=1,limit=1,
                    countrycodes=COUNTRY_CODES[site['country']])
        time.sleep(max(0,1.1-(time.monotonic()-previous)))
        previous=time.monotonic()
        try:
            req=urllib.request.Request('https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode(params),
                headers={'User-Agent':'GPU-Supply-Chain-Academic-Research/1.0 (+https://github.com/tianliu11/gpu-supply-chain-database)'})
            system_bundle=Path('/etc/ssl/cert.pem')
            context=ssl.create_default_context(cafile=str(system_bundle) if system_bundle.exists() else None)
            with urllib.request.urlopen(req,timeout=20,context=context) as resp:
                records=json.load(resp)
            record=records[0] if records else {}
            country=record.get('address',{}).get('country_code','')
            if record and country==COUNTRY_CODES[site['country']]:
                cache[fid]=dict(query=query,latitude=float(record['lat']),longitude=float(record['lon']),
                    display_name=record.get('display_name',''),precision='OSM_city_or_district_proxy_not_factory_gate',
                    osm_type=record.get('osm_type'),osm_id=record.get('osm_id'),
                    source_url='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode(params))
            else:
                cache[fid]=dict(query=query,latitude=None,longitude=None,status='no_country_matched_result')
        except Exception as exc:
            cache[fid]=dict(query=query,latitude=None,longitude=None,status='request_failed',error=str(exc))
        CACHE.write_text(json.dumps(cache,indent=2,ensure_ascii=False)+'\n')
        print(site['facility_name'], 'geocoded' if cache[fid].get('latitude') is not None else cache[fid].get('status'),flush=True)

if __name__=='__main__':
    main()
