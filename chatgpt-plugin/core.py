"""Conservative one-to-one settlement with exact decimal amounts and ambiguity holds."""
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import re

SCALE = {'USD': 2, 'EUR': 2, 'OMR': 3}


def normalize_reference(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Reference required')
    # Formatting separators are ignored; no fuzzy matching or transliteration.
    result = re.sub(r'[\s\-_/]', '', value).upper()
    if not result:
        raise ValueError('Reference required')
    return result


def validate(record):
    for key in ('id', 'tenant', 'currency', 'reference', 'amount', 'date'):
        if not isinstance(record.get(key), str) or not record[key].strip():
            raise ValueError('Missing or invalid ' + key)
    currency = record['currency']
    if currency not in SCALE:
        raise ValueError('Unsupported currency')
    try:
        amount = Decimal(record['amount'])
    except InvalidOperation as exc:
        raise ValueError('Invalid amount') from exc
    if (not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -SCALE[currency]
            or amount.adjusted() > 14 or len(amount.as_tuple().digits) > 18):
        raise ValueError('Invalid amount or minor-unit precision')
    return (record['tenant'], currency, normalize_reference(record['reference']), amount, date.fromisoformat(record['date']))


def reconcile(invoices, payments, *, max_days=45):
    if len(invoices) > 1000 or len(payments) > 1000:
        raise ValueError('Maximum 1000 records per input')
    if not isinstance(max_days, int) or isinstance(max_days, bool) or not 0 <= max_days <= 365:
        raise ValueError('Invalid date window')
    for records in (invoices, payments):
        ids = [r.get('id') for r in records]
        if len(set(ids)) != len(ids):
            raise ValueError('Duplicate record IDs')
    inv = {r['id']: validate(r) for r in invoices}
    pay = {r['id']: validate(r) for r in payments}
    edges, reverse = defaultdict(list), defaultdict(list)
    for iid, i in inv.items():
        for pid, p in pay.items():
            if i[:4] == p[:4] and 0 <= (p[4] - i[4]).days <= max_days:
                edges[iid].append(pid)
                reverse[pid].append(iid)
    results, used = [], set()
    for iid in inv:
        candidates = edges[iid]
        if len(candidates) == 1 and len(reverse[candidates[0]]) == 1:
            pid = candidates[0]
            used.add(pid)
            results.append({'invoice': iid, 'status': 'matched', 'payment': pid})
        else:
            results.append({'invoice': iid, 'status': 'ambiguous' if candidates else 'unmatched',
                            'candidates': sorted(candidates)})
    totals = defaultdict(Decimal)
    for row in results:
        if row['status'] == 'matched':
            value = inv[row['invoice']]
            totals[(value[0], value[1])] += value[3]
    return {'invoices': results,
            'unallocated_payments': sorted(set(pay) - used),
            'settled_totals': [{'tenant': t, 'currency': c, 'amount': f'{v:.{SCALE[c]}f}'}
                               for (t, c), v in sorted(totals.items())]}

