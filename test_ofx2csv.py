import os, sys
from collections import OrderedDict
import decimal
from types import NoneType

# add the parent directory to the path so we can import ofxparse
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from ofx2csv import main, get_positions_from_qfx, get_transactions_from_qfx
from ofxparse import OfxParser
from ofxparse.ofxparse import Security, Signon

def test_parse():
    sample_file = os.path.join(os.path.dirname(__file__), "WealthfrontQuickenExport.QFX")
    with open(sample_file) as f:
        qfx = OfxParser.parse(f)
    return qfx

def disassemble_object(object, indent=0):
    if type(object) in [str, int, float, bool, decimal.Decimal]:
        print("  " * indent + str(object))
    elif type(object) in [list, tuple]:
        print("  " * indent + str(type(object)))
        for item in object:
            disassemble_object(item, indent + 1)
    elif type(object) in [dict, OrderedDict]:
        print("  " * indent + str(type(object)))
        for key in object.keys():
            attr = object[key]
            print("  " * indent + key + ": " + str(type(attr)))
            attr = object[key]
            disassemble_object(attr, indent + 1)
    elif type(object) in [NoneType]:
        pass
    elif getattr(object, "__dict__", None):
        print("  " * indent + str(type(object)))
        for key in object.__dict__.keys():
            print("  " * indent + key + ": " + str(type(getattr(object, key))))
            attr = getattr(object, key)
            disassemble_object(attr, indent + 1)
    else:
        print("  " * indent + str(type(object)))
        print("  " * indent + str(object))

main()