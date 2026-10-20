import unittest
from reconcile import reconcile, normalize_reference


def record(key, **overrides):
    return dict(id=key, tenant='demo', currency='OMR', reference='INV-100', amount='12.345', date='2026-01-01', **{}) | overrides


class Tests(unittest.TestCase):
    def run_match(self, invoices=None, payments=None):
        return reconcile(invoices if invoices is not None else [record('i')],
                         payments if payments is not None else [record('p', date='2026-01-02')])

    def test_exact_match(self):
        result = self.run_match()
        self.assertEqual(result['invoices'][0]['status'], 'matched')
        self.assertEqual(result['settled_totals'][0]['amount'], '12.345')

    def test_reference_normalization(self):
        self.assertEqual(normalize_reference(' inv / 100 '), 'INV100')

    def test_currency_isolation(self):
        self.assertEqual(self.run_match(payments=[record('p',currency='USD',amount='12.34')])['invoices'][0]['status'], 'unmatched')

    def test_tenant_isolation(self):
        self.assertEqual(self.run_match(payments=[record('p',tenant='other')])['invoices'][0]['status'], 'unmatched')

    def test_duplicate_payment_ambiguity(self):
        result = self.run_match(payments=[record('p1'),record('p2')])
        self.assertEqual(result['invoices'][0]['status'], 'ambiguous')
        self.assertEqual(len(result['unallocated_payments']), 2)

    def test_payment_cannot_settle_two_invoices(self):
        result = self.run_match(invoices=[record('i1'),record('i2')])
        self.assertTrue(all(r['status']=='ambiguous' for r in result['invoices']))

    def test_date_window(self):
        for day in ['2025-12-31','2026-04-01']:
            self.assertEqual(self.run_match(payments=[record('p',date=day)])['invoices'][0]['status'], 'unmatched')

    def test_invalid_amounts(self):
        for amount in ['NaN','Infinity','-1','0','12.3456','oops']:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                self.run_match(invoices=[record('i',amount=amount)])

    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):
            self.run_match(invoices=[record('i'),record('i')])

    def test_exact_decimal_totals(self):
        invoices=[record('i1',amount='0.100',reference='a'),record('i2',amount='0.200',reference='b')]
        payments=[record('p1',amount='0.100',reference='a'),record('p2',amount='0.200',reference='b')]
        self.assertEqual(self.run_match(invoices,payments)['settled_totals'][0]['amount'],'0.300')

    def test_unsupported_currency_and_invalid_date(self):
        for changes in [{'currency':'XXX'},{'date':'yesterday'}]:
            with self.assertRaises(ValueError):
                self.run_match(invoices=[record('i',**changes)])

    def test_empty_and_precision(self):
        self.assertEqual(reconcile([],[])['settled_totals'], [])
        with self.assertRaises(ValueError):
            self.run_match(invoices=[record('i',currency='USD')])
