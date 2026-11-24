"""Check supplied URLs for retrieval problems, not factual correctness.

Does not bypass authentication/paywalls or store article text. A successful HTTP
response cannot verify a vendor, ranking, manufacturing site or relationship.
"""
import csv
import html
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
CACHE=BASE/'merged/source_url_checks.json'

def check(url):
    if not url.startswith(('https://','http://')):
        return dict(url=url,retrieval_status='invalid_url',content_verified=False)
    start=time.monotonic()
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'GPU-Supply-Chain-Academic-Research/1.0 (+https://github.com/tianliu11/gpu-supply-chain-database)'})
        context=ssl.create_default_context(cafile='/etc/ssl/cert.pem')
        with urllib.request.urlopen(req,timeout=15,context=context) as response:
            chunk=response.read(131072)
            typ=response.headers.get('Content-Type','')
            title=''
            if 'html' in typ:
                match=re.search(r'<title[^>]*>(.*?)</title>',chunk.decode('utf-8','replace'),re.S|re.I)
                if match: title=html.unescape(re.sub(r'\s+',' ',match.group(1)))[:250]
            return dict(url=url,http_status=response.status,final_url=response.url,
                retrieval_status='retrieved_not_content_verified',content_type=typ,title=title,
                content_verified=False,checked_on='2026-11-24')
    except urllib.error.HTTPError as exc:
        return dict(url=url,http_status=exc.code,retrieval_status='http_error',content_verified=False,checked_on='2026-11-24')
    except Exception as exc:
        return dict(url=url,retrieval_status='request_error',error=str(exc)[:250],content_verified=False,checked_on='2026-11-24')
    finally:
        time.sleep(max(0,1.0-(time.monotonic()-start)))

def main():
    rows=[]
    for path in sorted((BASE/'batches').glob('*_sources.csv')):
        with path.open(encoding='utf-8-sig',newline='') as f: rows.extend(csv.DictReader(f))
    cache=json.loads(CACHE.read_text()) if CACHE.exists() else {}
    urls=sorted({r['url'].strip() for r in rows})
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending={pool.submit(check,u):u for u in urls if u not in cache}
        for i,future in enumerate(as_completed(pending),1):
            u=pending[future];cache[u]=future.result()
            CACHE.write_text(json.dumps(cache,indent=2)+'\n')
            if i%25==0: print(f'Checked {i}/{len(pending)} new URLs',flush=True)
    result=[dict(source_id=r['source_id'],**cache[r['url'].strip()]) for r in rows]
    fields=list(dict.fromkeys(k for r in result for k in r))
    with (BASE/'merged/source_url_checks.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(result)
    from collections import Counter
    print(dict(Counter(r['retrieval_status'] for r in result)))

if __name__=='__main__': main()
