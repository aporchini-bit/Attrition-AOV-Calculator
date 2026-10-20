#!/usr/bin/env python3
"""
ROPS Attrition & AOV Calculator local server.
Authenticates via Salesforce session ID (no CLI required).

Usage:
  python3 rops-calculator-server.py
  Then open: http://localhost:8766
"""
import http.server
import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error

PORT = int(os.environ.get('ROPS_PORT', '8766'))
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
HTML_FILE   = os.path.join(SCRIPT_DIR, 'rops-calculator.html')
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'rops-calculator-config.json')

INSTANCE_URL = 'https://org62.my.salesforce.com'
API_VERSION  = 'v64.0'

SF_ID_RE = re.compile(r'^[A-Za-z0-9]{15,18}$')
CONTRACT_URL_RE = re.compile(r'/r/Contract/([A-Za-z0-9]{15,18})', re.I)
QUOTE_URL_RE    = re.compile(r'/r/Quote/([A-Za-z0-9]{15,18})', re.I)

NQE_FIELDS = """Id,
  AssetContract__c,
  AssetContract__r.CurrencyIsoCode,
  AssetOrderLine__r.CurrencyIsoCode,
  AssetOrderLine__r.Id,
  AssetOrderLine__r.OrderItemNumber,
  AssetOrderLine__r.ProvisioningStatus,
  AssetOrderLine__r.Product2.Id,
  AssetOrderLine__r.Product2.ProductCode,
  AssetOrderLine__r.Product2.Name,
  AssetOrderLine__r.Product2.SKUNumber__c,
  AssetOrderLine__r.Product2.SKU_Name__c,
  AssetOrderLine__r.Product2.Derived_Price_Product__c,
  AssetOrderLine__r.Product2.Purchase_Metrics__c,
  AssetOrderLine__r.Product2.Phase_Out_Status__c,
  AssetOrderLine__r.sfbase__OrderItemEffectiveDate__c,
  AssetOrderLine__r.EndDate,
  AssetOrderLine__r.sfbase__ProductBillingFrequency__c,
  AssetOrderLine__r.sfbase__OrderItemTermMonths__c,
  AssetOrderLine__r.Quantity,
  AssetOrderLine__r.PricebookEntry.UnitPrice,
  AssetOrderLine__r.DPP_List_Price__c,
  AssetOrderLine__r.UnitPrice,
  AssetOrderLine__r.TotalPrice,
  AssetOrderLine__r.RenewalTerm__c,
  AssetOrderLine__r.sfbase__AvailableQuantity__c,
  AssetOrderLine__r.Auto_Renewal_Uplift_Unit_Price__c,
  AssetOrderLine__r.Auto_Renewal_ACV__c,
  AssetOrderLine__r.Incremental_Uplift_ACV__c,
  AssetOrderLine__r.Eligible_For_Auto_Renew_Uplift__c,
  AssetOrderLine__r.Bookings_Treatment__c,
  AssetOrderLine__r.RelatedQuoteLine__c,
  AssetOrderLine__r.RelatedQuoteLine__r.Apttus_Proposal__Proposal__c,
  AssetOrderLine__r.RelatedQuoteLine__r.Apttus_Proposal__Proposal__r.Name,
  ContributingProductAsset__r.Id,
  ContributingProductAsset__r.Name,
  ContributingProductAsset__r.AssetOrderLine__c,
  ContributingProductAsset__r.Quantity,
  ContributingProductAsset__r.AssetOrderLine__r.PricebookEntry.UnitPrice,
  ContributingProductAsset__r.AssetOrderLine__r.UnitPrice"""

APTTUS_FIELDS = """Id,
  SfdcAssetContract__c,
  SfdcAssetContract__r.CurrencyIsoCode,
  SfdcAssetOrderLine__r.CurrencyIsoCode,
  SfdcAssetOrderLine__r.Id,
  SfdcAssetOrderLine__r.OrderItemNumber,
  SfdcAssetOrderLine__r.ProvisioningStatus,
  SfdcAssetOrderLine__r.Product2.Id,
  SfdcAssetOrderLine__r.Product2.ProductCode,
  SfdcAssetOrderLine__r.Product2.Name,
  SfdcAssetOrderLine__r.Product2.SKUNumber__c,
  SfdcAssetOrderLine__r.Product2.SKU_Name__c,
  SfdcAssetOrderLine__r.Product2.Derived_Price_Product__c,
  SfdcAssetOrderLine__r.Product2.Purchase_Metrics__c,
  SfdcAssetOrderLine__r.Product2.Phase_Out_Status__c,
  SfdcAssetOrderLine__r.sfbase__OrderItemEffectiveDate__c,
  SfdcAssetOrderLine__r.EndDate,
  SfdcAssetOrderLine__r.sfbase__ProductBillingFrequency__c,
  SfdcAssetOrderLine__r.sfbase__OrderItemTermMonths__c,
  SfdcAssetOrderLine__r.Quantity,
  SfdcAssetOrderLine__r.PricebookEntry.UnitPrice,
  SfdcAssetOrderLine__r.DPP_List_Price__c,
  SfdcAssetOrderLine__r.UnitPrice,
  SfdcAssetOrderLine__r.TotalPrice,
  SfdcAssetOrderLine__r.RenewalTerm__c,
  SfdcAssetOrderLine__r.sfbase__AvailableQuantity__c,
  SfdcAssetOrderLine__r.Auto_Renewal_Uplift_Unit_Price__c,
  SfdcAssetOrderLine__r.Auto_Renewal_ACV__c,
  SfdcAssetOrderLine__r.Incremental_Uplift_ACV__c,
  SfdcAssetOrderLine__r.Eligible_For_Auto_Renew_Uplift__c,
  SfdcAssetOrderLine__r.Bookings_Treatment__c,
  SfdcAssetOrderLine__r.RelatedQuoteLine__c,
  SfdcAssetOrderLine__r.RelatedQuoteLine__r.Apttus_Proposal__Proposal__c,
  SfdcAssetOrderLine__r.RelatedQuoteLine__r.Apttus_Proposal__Proposal__r.Name,
  SfdcContributingProductAssetId__r.Id,
  SfdcContributingProductAssetId__r.Name,
  SfdcContributingProductAssetId__r.SfdcAssetOrderLine__r.Id,
  SfdcContributingProductAssetId__r.SfdcAssetOrderLine__r.Quantity,
  SfdcContributingProductAssetId__r.SfdcAssetOrderLine__r.PricebookEntry.UnitPrice,
  SfdcContributingProductAssetId__r.SfdcAssetOrderLine__r.UnitPrice"""

QUOTE_LINE_FIELDS = """Id, Quote.Id, Quote.Name, Quote.Status, Quote.ContractTermMonths__c,
  CurrencyIsoCode, Product2.Id, Product2.Name, Product2.ProductCode, Product2.SKUNumber__c,
  ListPrice__c, NetUnitPrice__c, Quantity, Product2.Purchase_Metrics__c,
  Product2.Bookings_Treatment__c, Product2.PriceTreatment__c,
  ContributingAsset__r.Id, ContributingAsset__r.AssetOrderLine__c, ContributingAsset__r.SalesPrice__c,
  StartDate__c, EndDate__c"""


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_config(data):
    cfg = load_config()
    cfg.update(data)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)


def soql_escape(value):
    return str(value).replace('\\', '\\\\').replace("'", "\\'")


def sf_query(session_id, soql):
    url = f'{INSTANCE_URL}/services/data/{API_VERSION}/query?q={urllib.parse.quote(soql)}'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {session_id}',
        'Content-Type': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def sf_query_all(session_id, soql):
    """Follows nextRecordsUrl pagination; returns the full combined record list."""
    data = sf_query(session_id, soql)
    records = list(data.get('records', []))
    next_url = data.get('nextRecordsUrl')
    while next_url:
        req = urllib.request.Request(INSTANCE_URL + next_url, headers={
            'Authorization': f'Bearer {session_id}',
        })
        with urllib.request.urlopen(req, timeout=60) as resp:
            page = json.loads(resp.read())
        records.extend(page.get('records', []))
        next_url = page.get('nextRecordsUrl')
    return records


def flatten(record, prefix=''):
    """Flattens a Salesforce nested-relationship record into dot-path keys,
    matching the field paths used in the SOQL field lists above."""
    out = {}
    for key, value in record.items():
        if key == 'attributes':
            continue
        path = f'{prefix}{key}'
        if isinstance(value, dict):
            out.update(flatten(value, path + '.'))
        else:
            out[path] = value
    return out


def parse_contract_tokens(raw):
    """Splits free-form input into (ids, numbers, unmatched_raw_tokens)."""
    tokens = [t.strip() for t in re.split(r'[\n,]+', raw) if t.strip()]
    ids, numbers = [], []
    for tok in tokens:
        url_match = CONTRACT_URL_RE.search(tok)
        if url_match:
            ids.append(url_match.group(1))
        elif SF_ID_RE.match(tok):
            ids.append(tok)
        else:
            numbers.append(tok)
    return ids, numbers, tokens


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f'[rops] {fmt % args}')

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length) if length else b''

    def session_id(self):
        return load_config().get('sessionId', '').strip()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        if self.path == '/save-session':
            try:
                body = json.loads(self.read_body())
                sid = body.get('sessionId', '').strip()
                if not sid:
                    self.send_json({'error': 'sessionId is required'}, 400)
                    return
                save_config({'sessionId': sid})
                self.send_json({'ok': True})
                print('Session ID saved to config.')
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path == '/health':
            self.send_json({'ok': True, 'configured': bool(self.session_id())})
            return

        if path == '/test-session':
            self.handle_test_session()
            return

        if path == '/resolve-contracts':
            self.handle_resolve_contracts(qs)
            return

        if path == '/contract-assets':
            self.handle_contract_assets(qs)
            return

        if path == '/quote-lines':
            self.handle_quote_lines(qs)
            return

        # Static file serving
        try:
            with open(HTML_FILE, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'rops-calculator.html not found')

    # ── Endpoint handlers ──────────────────────────────────────────

    def handle_test_session(self):
        """Validates the saved session ID against Salesforce and returns a
        clear verdict (valid / invalid / API-disabled), including the raw
        Salesforce errorCode so failures are self-explanatory."""
        sid = self.session_id()
        if not sid:
            self.send_json({'ok': False, 'verdict': 'no_session',
                            'message': 'No session ID saved yet. Paste one in Step 1 and click Save first.'}, 200)
            return
        try:
            url = f'{INSTANCE_URL}/services/data/{API_VERSION}/limits'
            req = urllib.request.Request(url, headers={'Authorization': f'Bearer {sid}'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                json.loads(resp.read())
            self.send_json({'ok': True, 'verdict': 'valid',
                            'message': f'✓ Session is valid — connected to {INSTANCE_URL}.',
                            'instance': INSTANCE_URL, 'sidLength': len(sid)}, 200)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            code = ''
            try:
                parsed = json.loads(body)
                if isinstance(parsed, list) and parsed:
                    code = parsed[0].get('errorCode', '')
            except Exception:
                pass
            print(f'[test-session] SF {e.code} {code}: {body[:200]}')
            self.send_json({'ok': False, 'verdict': 'rejected',
                            'httpStatus': e.code, 'errorCode': code,
                            'message': f'Salesforce rejected the token (HTTP {e.code}, {code or "unknown"}).',
                            'instance': INSTANCE_URL, 'sidLength': len(sid),
                            'raw': body[:300]}, 200)
        except Exception as e:
            self.send_json({'ok': False, 'verdict': 'error',
                            'message': f'Could not reach Salesforce: {e}',
                            'instance': INSTANCE_URL}, 200)

    def handle_resolve_contracts(self, qs):
        sid = self.session_id()
        if not sid:
            self.send_json({'error': 'No session ID configured. Paste your Salesforce session ID in Step 1.'}, 401)
            return
        raw = (qs.get('input') or [''])[0]
        ids, numbers, tokens = parse_contract_tokens(raw)
        if not ids and not numbers:
            self.send_json({'error': 'No contract numbers, IDs, or URLs found in the input.'}, 400)
            return

        conditions = []
        if ids:
            id_list = ','.join(f"'{soql_escape(i)}'" for i in ids)
            conditions.append(f'Id IN ({id_list})')
        if numbers:
            num_list = ','.join(f"'{soql_escape(n)}'" for n in numbers)
            conditions.append(f'ContractNumber IN ({num_list})')
        where = ' OR '.join(conditions)
        soql = (
            "SELECT Id, ContractNumber, Status, EndDate, StartDate, Account.Name "
            f"FROM Contract WHERE {where} LIMIT 200"
        )

        try:
            records = sf_query_all(sid, soql)
        except urllib.error.HTTPError as e:
            self.handle_sf_error(e)
            return
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
            return

        matched_numbers = {r.get('ContractNumber') for r in records if r.get('ContractNumber')}
        matched_ids = {r.get('Id') for r in records}
        unmatched = [
            t for t in tokens
            if t not in matched_numbers and t not in matched_ids
            and not any(t in str(mid) for mid in matched_ids)
        ]
        self.send_json({'contracts': records, 'unmatched': unmatched})

    def handle_contract_assets(self, qs):
        sid = self.session_id()
        if not sid:
            self.send_json({'error': 'No session ID configured.'}, 401)
            return
        ids_raw = (qs.get('ids') or [''])[0]
        contract_ids = [i.strip() for i in ids_raw.split(',') if i.strip()]
        if not contract_ids:
            self.send_json({'error': 'No contract IDs supplied.'}, 400)
            return

        id_list = ','.join(f"'{soql_escape(i)}'" for i in contract_ids)
        result = {cid: {'model': None, 'rows': []} for cid in contract_ids}

        try:
            nqe_soql = (
                f"SELECT {NQE_FIELDS} FROM Asset "
                "WHERE (NOT AssetOrderLine__r.Bookings_Treatment__c LIKE '%NonACV-NonRecurring%') "
                f"AND AssetContract__r.Id IN ({id_list}) "
                "ORDER BY ContributingProductAsset__r.Id ASC, AssetOrderLine__r.Product2.Name ASC"
            )
            nqe_records = sf_query_all(sid, nqe_soql)
            for rec in nqe_records:
                flat = flatten(rec)
                cid = flat.get('AssetContract__c')
                if cid in result:
                    result[cid]['model'] = 'NQE'
                    result[cid]['rows'].append(flat)

            missing = [cid for cid in contract_ids if not result[cid]['rows']]
            if missing:
                miss_list = ','.join(f"'{soql_escape(i)}'" for i in missing)
                apttus_soql = (
                    f"SELECT {APTTUS_FIELDS} FROM Apttus_Config2__AssetLineItem__c "
                    "WHERE (NOT SfdcAssetOrderLine__r.Bookings_Treatment__c LIKE '%NonACV-NonRecurring%') "
                    f"AND SfdcAssetContract__c IN ({miss_list}) "
                    "ORDER BY SfdcContributingProductAssetId__r.Id ASC, SfdcAssetOrderLine__r.Product2.Name ASC"
                )
                apttus_records = sf_query_all(sid, apttus_soql)
                for rec in apttus_records:
                    flat = flatten(rec)
                    cid = flat.get('SfdcAssetContract__c')
                    if cid in result:
                        result[cid]['model'] = 'Apttus'
                        result[cid]['rows'].append(flat)
        except urllib.error.HTTPError as e:
            self.handle_sf_error(e)
            return
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
            return

        self.send_json(result)

    def handle_quote_lines(self, qs):
        sid = self.session_id()
        if not sid:
            self.send_json({'error': 'No session ID configured.'}, 401)
            return
        raw = (qs.get('id') or [''])[0].strip()
        url_match = QUOTE_URL_RE.search(raw)
        quote_id = url_match.group(1) if url_match else (raw if SF_ID_RE.match(raw) else None)
        if not quote_id:
            self.send_json({'error': 'Enter a Salesforce quote URL or a 15/18-character quote ID.'}, 400)
            return

        soql = (
            f"SELECT {QUOTE_LINE_FIELDS} FROM QuoteLineItem "
            f"WHERE QuoteId = '{soql_escape(quote_id)}' "
            "AND (NOT Product2.Bookings_Treatment__c LIKE '%NonACV-NonRecurring%') "
            "ORDER BY Product2.Name, Id"
        )
        try:
            records = sf_query_all(sid, soql)
        except urllib.error.HTTPError as e:
            self.handle_sf_error(e)
            return
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
            return

        self.send_json({'lines': [flatten(r) for r in records]})

    def handle_sf_error(self, e):
        body = e.read().decode('utf-8', errors='replace')
        print(f'SF API error {e.code}: {body[:300]}')
        if e.code in (401, 403):
            self.send_json({'error': 'Session expired — paste a fresh session ID in Step 1.'}, 401)
        else:
            self.send_json({'error': f'Salesforce error: HTTP {e.code} — {body[:200]}'}, 500)


if __name__ == '__main__':
    try:
        server = http.server.HTTPServer(('localhost', PORT), Handler)
    except OSError as e:
        if 'Address already in use' in str(e) or getattr(e, 'errno', None) == 48:
            print(f'\n⚠  The calculator already seems to be running — a browser tab may already be open.')
            print(f'   Try going to http://localhost:{PORT} instead of starting it again.')
            print(f'   If that page doesn\'t load, close any other window running this tool, then try again.\n')
            input('Press Enter to close this window...')
            raise SystemExit(1)
        raise
    cfg = load_config()
    configured = bool(cfg.get('sessionId'))
    print(f'\033[1;34mROPS Calculator → http://localhost:{PORT}\033[0m')
    if not configured:
        print('\033[33m⚠  No session ID yet — open the page and paste one in Step 1.\033[0m')
    else:
        print('\033[32m✓  Session ID loaded from config.\033[0m')
    print('Stop: Ctrl+C\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
