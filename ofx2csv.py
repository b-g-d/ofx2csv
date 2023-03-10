import datetime
import decimal
import os, sys

from collections import OrderedDict
from csv import DictWriter
from glob import glob
from types import NoneType
from typing import List
from ofxparse import OfxParser
from ofxparse.ofxparse import Security, Signon, Ofx

INSTRUCTIONS = """Generate CSV files from OFX files. This works with the Wealthfront OFX export. It will generate two files for each input file: one for transactions and one for positions. \
It currently only supports one account per file.
Usage: python ofx2csv.py <file_path> <output_dir>, where output_dir is optional."""

DATE_FORMAT = "%Y/%m/%d %H:%M:%S"

def write_csv(transactions: List[dict], out_file):
    print("Writing: " + out_file)
    fields = transactions[0].keys()
    with open(out_file, 'w') as f:
        writer = DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for line in transactions:
            writer.writerow(line)
    print("Done")

def convert_value_to_string(value):
    if type(value) in [str, int, float, bool, decimal.Decimal]:
        return value
    if type(value) in [datetime.datetime]:
        return value.strftime(DATE_FORMAT)
    if type(value) in [NoneType]:
        return ""
    else:
        print("not sure how to convert: " + str(type(value)))
        return str(value) 

def get_transactions_from_qfx(qfx):
    transactions = []
    ## transaction attributes
    assert len(qfx.accounts) ==1
    account = qfx.accounts[0]
    assert len(account.statement.transactions) > 0
    all_keys = set()
    for transaction in account.statement.transactions:
        keys = transaction.__dict__.keys()
        all_keys.update(keys)
    for transaction in account.statement.transactions:
        transaction_dict = {}
        for key in all_keys:
            if key in transaction.__dict__:
                transaction_dict[key] = convert_value_to_string(getattr(transaction, key))
            else:
                transaction_dict[key] = ""
        transactions.append(transaction_dict)
    
    return transactions

def get_positions_from_qfx(qfx):
    assert len(qfx.accounts)==1
    account = qfx.accounts[0]
    assert len(account.statement.positions) > 0
    all_keys = set()
    for position in account.statement.positions:
        keys = position.__dict__.keys()
        all_keys.update(keys)
    
    cash_position = {
        "date": account.statement.end_date.strftime(DATE_FORMAT),
        "market_value": 1,
        "unit_price": 1,
        "units": account.statement.available_cash,
        "security": "CASH",
    }

    if set(cash_position.keys()) != all_keys:
        print("cash position keys don't match")
        print(cash_position.keys())
        print(all_keys)
    
    positions = [cash_position]
    
    for position in account.statement.positions:
        position_dict = {}
        for key in all_keys:
            if key in position.__dict__:
                position_dict[key] = convert_value_to_string(getattr(position, key))
            else:
                position_dict[key] = ""
        positions.append(position_dict)

    return positions
    

def main(file_path, output_dir):
    with open(file_path) as f:
        qfx = OfxParser.parse(f)
    transactions = get_transactions_from_qfx(qfx)
    positions = get_positions_from_qfx(qfx)
    filename = os.path.basename(file_path)
    new_file_path = os.path.join(output_dir, filename)
    write_csv(transactions, new_file_path.replace(".QFX", "") + "_transactions.csv")
    write_csv(positions, new_file_path.replace(".QFX", "") + "_positions.csv")
    
if __name__ == "__main__":
    # relative filepath should be first argument
    # optional second argument is output directory
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print(INSTRUCTIONS)
        sys.exit(1)
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = os.path.dirname(file_path)
    
    # check that file and output directory exist
    if not os.path.exists(file_path):
        print("File not found: " + file_path)
        print(INSTRUCTIONS)
        sys.exit(1)
    if not os.path.exists(output_dir):
        print("Output directory not found: " + output_dir)
        print(INSTRUCTIONS)
        sys.exit(1)
    
    main(file_path, output_dir)