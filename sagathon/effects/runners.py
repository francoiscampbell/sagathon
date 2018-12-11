from __future__ import print_function

import sys

from . import types

def run_call_effect(effect):
    fn = effect['fn']
    args = effect['args']
    kwargs = effect['kwargs']
    print('running call effect for fn', fn)
    return fn(*args, **kwargs)

effect_map = {
    types.CALL: run_call_effect,
}

def run_effect(effect):
    effect_type = effect['type']
    try:
        runner = effect_map[effect_type]
        print('got runner', runner)
    except KeyError:
        print(
            'Could not find runner for effect type: {}'.format(effect_type),
            file=sys.stderr
        )
        raise

    return runner(effect)