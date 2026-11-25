"""Screen vendor citations against public document text.

Results are retrieval and name/product matching signals for a claim reviewer.
The script stores match metadata, not copies of the source documents.
"""
import argparse
import csv
import hashlib
import io
import ipaddress
import json
import re
import socket
import ssl
import unicodedata
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from reconcile import BASE, OUT, read

MAX_DOWNLOAD = 12 * 1024 * 1024
CONTEXT = ssl.create_default_context(cafile='/etc/ssl/cert.pem' if Path('/etc/ssl/cert.pem').exists() else None)
BOILERPLATE = {'and', 'the', 'with', 'manufacturing', 'supply', 'production',
               'materials', 'material', 'components', 'component', 'process',
               'grade', 'high', 'type', 'raw', 'purity', 'electronic', 'disposable'}
LEGAL_SUFFIX = re.compile(r'\s+(?:co|corp|corporation|company|group|inc|ltd|limited|plc|s a|llc|gmbh)$')


def normalized(value):
    folded = unicodedata.normalize('NFKD', value).casefold()
    return ' '.join(re.findall(r'[a-z0-9]+', folded))


def supplier_terms(value):
    # Parentheses often describe products, a subsidiary, or a cited market.
    # Use the listed supplier, rather than auto-accepting a parent as evidence.
    name = normalized(value.split('(')[0])
    while LEGAL_SUFFIX.search(name):
        name = LEGAL_SUFFIX.sub('', name)
    return [name] if len(name.replace(' ', '')) >= 3 else []


def product_terms(name):
    chunks = re.split(r'[()/&,;]|\bor\b', name, flags=re.I)
    terms = []
    for chunk in chunks:
        tokens = [t for t in normalized(chunk).split() if t not in BOILERPLATE]
        if len(tokens) >= 2:
            terms.extend(' '.join(tokens[i:i+2]) for i in range(len(tokens)-1))
        elif len(tokens) == 1 and len(tokens[0]) >= 5:
            terms.extend(tokens)
    return sorted(set(terms))


class VisibleText(HTMLParser):
    excluded = {'script', 'style', 'noscript', 'template', 'svg', 'nav', 'footer'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = []
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in self.excluded:
            self.skip.append(tag)

    def handle_endtag(self, tag):
        if self.skip and tag == self.skip[-1]:
            self.skip.pop()

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def check_public_url(url):
    parts = urlsplit(url)
    if parts.scheme not in {'https', 'http'} or parts.username or parts.password or not parts.hostname:
        raise ValueError('Unsupported URL')
    if parts.port not in {None, 80, 443}:
        raise ValueError('Unsupported port')
    addresses = socket.getaddrinfo(parts.hostname, parts.port or 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(address[4][0]).is_global for address in addresses):
        raise ValueError('Non-public URL')


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def extract(data, headers):
    if data.startswith(b'%PDF'):
        from pypdf import PdfReader
        document = PdfReader(io.BytesIO(data), strict=False)
        # Bound large consolidated reports; a no-match is never a rejection.
        return ' '.join((page.extract_text() or '') for page in document.pages[:100])
    content_type = headers.get_content_type()
    if content_type not in {'text/html', 'text/plain', 'application/xhtml+xml'}:
        return ''
    decoded = data.decode(headers.get_content_charset() or 'utf-8', errors='replace')
    if content_type == 'text/plain':
        return decoded
    parser = VisibleText()
    parser.feed(decoded)
    return ' '.join(parser.parts)


def run_one(url, claims):
    info = dict(url=url, final_url='', http_status='', source_text_sha256='',
                extraction_status='', text_characters=0)
    document = ''
    try:
        check_public_url(url)
        opener = urllib.request.build_opener(PublicRedirect(), urllib.request.HTTPSHandler(context=CONTEXT))
        request = urllib.request.Request(url, headers={'User-Agent': 'GPU-Supply-Chain-Academic-Research/1.0'})
        with opener.open(request, timeout=9) as reply:
            info.update(final_url=reply.url, http_status=reply.status)
            data = reply.read(MAX_DOWNLOAD + 1)
            if len(data) > MAX_DOWNLOAD:
                info['extraction_status'] = 'document_size_limit'
            else:
                document = normalized(extract(data, reply.headers))
                status = 'text_available' if len(document) >= 120 else 'insufficient_extracted_text'
                info.update(extraction_status=status, text_characters=len(document),
                            source_text_sha256=hashlib.sha256(document.encode()).hexdigest())
    except urllib.error.HTTPError as exc:
        info.update(http_status=exc.code, extraction_status='http_error')
    except Exception as exc:
        info.update(extraction_status=f'retrieval_or_extraction_error:{type(exc).__name__}')
    rows = []
    for claim, source in claims:
        vendor = supplier_terms(claim['vendor_name'])
        product = product_terms(claim['node_name'])
        # A 200-character window is a triage hint. Company navigation and
        # comparative tables can mention a rival without supporting the claim.
        padded = ' ' + document + ' '
        vendor_positions = [m.start() for term in vendor
                            for m in re.finditer(re.escape(' ' + term + ' '), padded)]
        matches = [term for term in product if ' ' + term + ' ' in padded]
        nearby = [term for term in matches if any(' ' + term + ' ' in padded[max(pos-200, 0):pos+200]
                                                   for pos in vendor_positions)]
        status = info['extraction_status']
        if status == 'text_available':
            status = ('nearby_name_and_product_terms' if nearby else
                      'name_and_product_terms_apart' if vendor_positions and matches else
                      'supplier_name_only' if vendor_positions else 'product_terms_only' if matches else
                      'no_selected_terms')
        rows.append(dict(record_id=claim['record_id'], source_id=source['source_id'],
                         node_id=claim['node_id'], vendor_name=claim['vendor_name'],
                         source_type=source['source_type'], screen_result=status,
                         exact_supplier_terms=';'.join(vendor) if vendor_positions else '',
                         product_terms=';'.join(matches), nearby_terms=';'.join(nearby),
                         **info))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT/'vendor_citation_screen.csv')
    args = parser.parse_args()
    sources = {r['source_id']: r for p in sorted((BASE/'batches').glob('*_sources.csv')) for r in read(p)}
    by_url = defaultdict(list)
    for row in read(OUT/'vendor_candidates.csv'):
        for sid in sorted(set(row['source_ids'].split(';')) & sources.keys()):
            source = sources[sid]
            by_url[source['url'].strip()].append((row, source))
    with ThreadPoolExecutor(max_workers=5) as pool:
        records = []
        tasks = pool.map(lambda item: run_one(*item), sorted(by_url.items()))
        for n, result in enumerate(tasks, 1):
            records.extend(result)
            if n % 50 == 0:
                print(f'Screened {n} of {len(by_url)} source URLs', flush=True)
    records.sort(key=lambda r: (r['record_id'], r['source_id']))
    temporary = args.output.with_suffix('.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(records[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)
    temporary.replace(args.output)
    print(f'Screened {len(records)} claim–citation links across {len(by_url)} URLs')
    print(dict(Counter(row['screen_result'] for row in records)))


if __name__ == '__main__':
    main()
