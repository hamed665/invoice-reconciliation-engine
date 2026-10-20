import argparse
import json
from pathlib import Path
from reconcile import reconcile


def run(path=None):
    data=json.loads(Path(path or Path(__file__).with_name('sample.json')).read_text())
    return reconcile(data['invoices'],data['payments'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description='Conservative exact-amount reconciliation; no payments are made.')
    parser.add_argument('--input',type=Path,help='JSON file with invoices and payments arrays')
    args=parser.parse_args()
    print(json.dumps(run(args.input),indent=2))
