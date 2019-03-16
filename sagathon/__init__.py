from __future__ import print_function

import sys
from types import GeneratorType

import effects


def send_value(generator, value):
    if isinstance(value, Exception):
        print("throwing value into generator")
        return generator.throw(value)
    else:
        print("sending value into generator")
        return generator.send(value)


def run_saga(saga, *args, **kwargs):
    generator = saga(*args, **kwargs)
    return _run_generator(generator)


def _run_generator(generator):
    value = None
    while True:
        try:
            effect = send_value(generator, value)
            print("got effect", effect.type)
        except StopIteration:
            print("stopping generator", generator)
            break

        try:
            value = run_effect(effect)
        except Exception as e:
            value = e
        else:
            if isinstance(value, GeneratorType):
                return _run_generator(value)
            if isinstance(value, effects.Ret):
                return value


def run_effect(effect):
    try:
        return effect.run()
    except AttributeError:
        print(
            "Yielded value was not an Effect, it was a {}".format(type(effect)),
            file=sys.stderr,
        )
        raise
