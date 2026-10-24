import csv
import io
import json
from pathlib import Path
import pytest
from reconciliation import build_report, sample_inputs, to_csv, parse_csv

def fixtures():
    return json.loads((Path(__file__).parents[1]/'samples/example.json').read_text())

def compute(data,**kwargs):
    return build_report(to_csv(data['invoices']),to_csv(data['payments']),**kwargs)

def test_sample_and_export():
    r=build_report(**sample_inputs())
    assert r['summary']=={'invoices':3,'payments':3,'matched':1,'ambiguous':1,'unmatched':1,'unallocated_payments':2}
    assert r['matched_totals']==[{'tenant':'synthetic-a','currency':'OMR','amount':'12.345'}]
    assert len(list(csv.DictReader(io.StringIO(r['csv_export']))))==3
    assert all(row['reason'] for row in r['rows'])

def test_one_payment_cannot_settle_two_invoices():
    d=fixtures(); d['invoices']=[d['invoices'][0],dict(d['invoices'][0],id='INV-DUP')];d['payments']=[d['payments'][0]]
    r=compute(d)
    assert r['summary']['ambiguous']==2 and r['matched_totals']==[]
    assert r['unallocated_payment_ids']==['PAY-1']

@pytest.mark.parametrize('field,value',[('tenant','other'),('currency','EUR'),('amount','12.346'),('reference','different'),('date','2025-12-31'),('date','2027-01-01')])
def test_every_match_constraint_required(field,value):
    d=fixtures();d['invoices']=d['invoices'][:1]
    d['invoices'][0]['amount']='12.34'
    d['payments'][0]['amount']='12.34'
    d['payments']=[dict(d['payments'][0],**{field:value})]
    assert compute(d)['summary']['matched']==0

@pytest.mark.parametrize('amount',['12.3456','NaN','Infinity','0','-1','1e999','1234567890123456','oops'])
def test_invalid_money_rejected(amount):
    d=fixtures();d['invoices'][0]['amount']=amount
    with pytest.raises(ValueError):compute(d)

def test_usd_minor_unit_precision():
    d=fixtures();d['invoices'][1]['amount']='85.001'
    with pytest.raises(ValueError):compute(d)

def test_bom_and_quoted_csv():
    d=fixtures();d['invoices'][0]['id']='Invoice, with comma'
    assert build_report('\ufeff'+to_csv(d['invoices']),to_csv(d['payments']))['rows'][0]['invoice_id']=='Invoice, with comma'

def test_duplicate_ids_rejected():
    d=fixtures();d['payments'].append(d['payments'][0])
    with pytest.raises(ValueError,match='Duplicate'):compute(d)

def test_csv_formula_cells_are_not_executable_exports():
    d=fixtures();d['invoices'][0]['id']='=HYPERLINK("example")'
    r=compute(d)
    assert list(csv.DictReader(io.StringIO(r['csv_export'])))[0]['invoice_id'].startswith("'=")
    assert r['rows'][0]['invoice_id'].startswith('=')

@pytest.mark.parametrize('bad',['','id,id,tenant,currency,reference,amount,date\n','id,tenant\na,b\n','id,tenant,currency,reference,amount,date\na,b,c,d,e\n','\x00'])
def test_malformed_csv_rejected(bad):
    with pytest.raises(ValueError):parse_csv(bad,'Invoices')

def test_row_and_byte_limits():
    d=fixtures();rows=[dict(d['invoices'][0],id=str(i)) for i in range(201)]
    with pytest.raises(ValueError,match='200'):parse_csv(to_csv(rows),'Invoices')
    with pytest.raises(ValueError,match='128000'):parse_csv('x'*128001,'Invoices')

@pytest.mark.parametrize('days',[-1,366,True,1.5,'45'])
def test_invalid_windows(days):
    with pytest.raises(ValueError):build_report(**sample_inputs(),max_days=days)

def test_stateless_no_input_mutation():
    d=fixtures();before=json.dumps(d,sort_keys=True)
    assert compute(d)==compute(d)
    assert json.dumps(d,sort_keys=True)==before
