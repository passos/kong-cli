#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
from datetime import datetime

import simplejson as json
from simplejson import JSONEncoder

class CustomJSONEncoder(JSONEncoder):

    def default(self, o):
        # to support arbitrary iterators
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)

        # support datetime
        if isinstance(o, datetime):
            # return o.isoformat() if o else ''
            return datetime.strftime(o, '%Y-%m-%d %H:%M:%S') if o else ''
        elif hasattr(o, '__dict__'):
            return o.__dict__

        return str(o)
        # return JSONEncoder.default(self, o)


def tojson(o, **kwargs):
    if 'ensure_ascii' not in kwargs:
        kwargs['ensure_ascii'] = False
    if 'cls' not in kwargs:
        kwargs['cls'] = CustomJSONEncoder
    return json.dumps(o, **kwargs)


def tojson_pretty(o, **kwargs):
    if 'sort_keys' not in kwargs:
        kwargs['sort_keys'] = True
    if 'indent' not in kwargs:
        kwargs['indent'] = 2
    return tojson(o, **kwargs)


def get_dict_value(d, keys, default=None):
    for key in keys.split('.'):
        if type(d) != dict:
            return default
        if key in d:
            d = d[key]
        else:
            return default

    return d


def update_json(s, **kwargs):
    try:
        data = json.loads(s)
        data.update(kwargs)
        return tojson(data)
    except Exception as e:
        print "update refer info error: %s" % str(e)
        return s


def flatten(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
