from __future__ import print_function

from . import types

def call(fn, *args, **kwargs):
    print('making call effect for fn', fn)
    return {
        'type': types.CALL,
        'fn': fn,
        'args': args,
        'kwargs': kwargs,
    }