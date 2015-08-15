import json
import re
import pprint
import sys
from functools import cmp_to_key

pp = pprint.PrettyPrinter()

if len(sys.argv) != 3:
    raise IndexError('Must give two files as arguments')

first, second = sys.argv[1:]

firstfile = open(first, 'r')
secondfile = open(second, 'r')

firstjson = json.load(firstfile)
secondjson = json.load(secondfile)

firstjson = sorted(firstjson, key=lambda manga: manga['name'])
secondjson = sorted(secondjson, key=lambda manga: manga['name'])


def is_sorted(iterable, key=lambda x, y: x <= y):
    for i, val in enumerate(iterable[1:]):
        if not key(iterable[i - 1], val):
            return False
    return True


def bin_search(iterable, pred=lambda x, y=None: x == y):
    # find first element that satisfies
    if not is_sorted(iterable, lambda x, y: x['name'] < y['name']):
        print('Can\'t binary search on unsorted iterable, \
        attempt to sort first')
        if type(iterable) is not list:
            raise TypeError("can\'t binary search on unsorted {}"
                            .format(type(iterable).__name__))
        iterable = sorted(iterable, key=lambda x: x['name'])
    lo, hi = (0, len(iterable) - 1)
    while True:
        # floor
        # ensures that even for negative indices, we always round down
        mid = lo + (hi - lo) / 2
        if pred(iterable[mid]):
            return mid
        else:
            hi = mid
        if lo >= hi:
            break
    return None

for i, manga in enumerate(secondjson, start=0):
    if manga['name'] != firstjson[i]['name']:
        print 'Json doesn\'t sync up on name'
        print 'Attempting to get the right one'
        index = bin_search(firstjson, lambda x: x['name'] == manga['name'])
        if index is not None:
            firstjson[i].update(manga)
    else:
        firstjson[i].update(manga)

resultfile = open(first, 'w')
json.dump(firstjson, resultfile, indent=0)
