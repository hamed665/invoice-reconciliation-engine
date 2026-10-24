"""Bounded CSV adapter and explainable, non-executing reconciliation reports."""
import csv
import io
import json
from collections import Counter
from pathlib import Path
from core import reconcile

FIELDS = ('id', 'tenant', 'currency', 'reference', 'amount', 'date')
MAX_BYTES = 128_000
MAX_ROWS = 200

def parse_csv(text, label):
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_BYTES:
        raise ValueError(f'{label}: CSV must be at most {MAX_BYTES} UTF-8 bytes')
    if '\x00' in text:
        raise ValueError(f'{label}: null bytes are not supported')
    reader = csv.DictReader(io.StringIO(text.lstrip('\ufeff')), strict=True)
    if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError(f'{label}: missing or duplicate column headers')
    if set(reader.fieldnames) != set(FIELDS):
        raise ValueError(f'{label}: required columns are {", ".join(FIELDS)}')
    result = []
    try:
        for row in reader:
            if len(result) >= MAX_ROWS:
                raise ValueError(f'{label}: maximum {MAX_ROWS} rows')
            if None in row or any(v is None for v in row.values()):
                raise ValueError(f'{label}: inconsistent CSV row length')
            cleaned = {k: v.strip() for k, v in row.items()}
            if any(not v or len(v) > 160 for v in cleaned.values()):
                raise ValueError(f'{label}: every cell must contain 1–160 characters')
            result.append(cleaned)
    except csv.Error as exc:
        raise ValueError(f'{label}: malformed CSV') from exc
    if not result:
        raise ValueError(f'{label}: at least one data row is required')
    return result

def to_csv(records):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(records)
    return out.getvalue()

def sample_inputs():
    data = json.loads((Path(__file__).parent/'samples/example.json').read_text())
    return {'invoices_csv': to_csv(data['invoices']), 'payments_csv': to_csv(data['payments'])}

def spreadsheet_safe(value):
    s = str(value)
    return "'" + s if s.lstrip().startswith(('=', '+', '-', '@')) or s.startswith(('\t', '\r')) else s

def build_report(invoices_csv, payments_csv, max_days=45):
    invoices = parse_csv(invoices_csv, 'Invoices')
    payments = parse_csv(payments_csv, 'Payments')
    result = reconcile(invoices, payments, max_days=max_days)
    by_invoice = {r['id']: r for r in invoices}
    by_payment = {r['id']: r for r in payments}
    reasons = {
        'matched': 'Unique one-to-one match on tenant, normalized reference, currency, exact amount and date window.',
        'ambiguous': 'Multiple candidate links compete for an invoice or payment. No allocation was made; human review is required.',
        'unmatched': 'No payment satisfies every matching rule within the selected date window.'}
    rows = []
    for decision in result['invoices']:
        invoice = by_invoice[decision['invoice']]
        ids = [decision['payment']] if decision['status']=='matched' else decision.get('candidates', [])
        rows.append({'invoice_id':invoice['id'], 'tenant':invoice['tenant'], 'currency':invoice['currency'],
                     'amount':invoice['amount'], 'reference':invoice['reference'], 'date':invoice['date'],
                     'status':decision['status'], 'payment_id':decision.get('payment'),
                     'candidate_payments':[{'id':p, 'date':by_payment[p]['date'], 'amount':by_payment[p]['amount']} for p in ids],
                     'reason':reasons[decision['status']]})
    counts = Counter(r['status'] for r in rows)
    fields = ['invoice_id','tenant','currency','amount','reference','date','status','payment_id','candidate_payment_ids','reason']
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output,fieldnames=fields,lineterminator='\n')
    writer.writeheader()
    for row in rows:
        export = {k: row.get(k) or '' for k in fields}
        export['candidate_payment_ids'] = '; '.join(p['id'] for p in row['candidate_payments'])
        writer.writerow({k:spreadsheet_safe(v) for k,v in export.items()})
    return {'schema_version':'1.0', 'max_days':max_days,
            'summary':{'invoices':len(rows),'payments':len(payments),'matched':counts['matched'],
                       'ambiguous':counts['ambiguous'],'unmatched':counts['unmatched'],
                       'unallocated_payments':len(result['unallocated_payments'])},
            'rows':rows, 'matched_totals':result['settled_totals'],
            'unallocated_payment_ids':result['unallocated_payments'], 'csv_export':output.getvalue(),
            'notice':'Matching evidence only. No money is moved, no ledger is changed, and ambiguous items require human review.'}
