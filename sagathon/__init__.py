from __future__ import print_function

import sys

from effects.runners import run_effect

def send_value(generator, value):
    if isinstance(value, Exception):
        print('throwing value into generator')
        return generator.throw(type(value))
    else:
        print('sending value into generator')
        return generator.send(value)

def run_saga(saga, *args, **kwargs):
    generator = saga(*args, **kwargs)
    previous_value = None
    while True:
        try:
            effect = send_value(generator, previous_value)
            print('got effect', effect)
        except StopIteration:
            print('stopping')
            break
        
        try:
            previous_value = run_effect(effect)
        except Exception as e:
            previous_value = e
