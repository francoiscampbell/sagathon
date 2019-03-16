from __future__ import print_function

import sys
from collections import deque
from types import GeneratorType

import effects


def run_saga(saga, *args, **kwargs):
    generator = saga(*args, **kwargs)
    return _run_stacks(deque([generator]), deque([None]))


def _run_stacks(generator_stack, return_stack):
    while generator_stack and return_stack:
        _step_stacks(generator_stack, return_stack)

    return return_stack.pop()


def _step_stacks(generator_stack, return_stack):
    generator = generator_stack.pop()
    value = return_stack.pop()
    try:
        effect = _send_value(generator, value)
        print("got effect", effect.type)
    except StopIteration as e:
        print("stopping generator", generator)
        return_stack.append(getattr(e, "value", None))
        return

    try:
        value = _run_effect(effect)
    except Exception as e:
        generator_stack.append(generator)
        return_stack.append(e)
        return

    if isinstance(effect, effects.Ret):
        return_stack.append(value)
        return

    if isinstance(value, GeneratorType):
        generator_stack.append(generator)
        generator_stack.append(value)
        return_stack.append(None)
        return

    generator_stack.append(generator)
    return_stack.append(value)


def _send_value(generator, value):
    if isinstance(value, Exception):
        print("throwing value into generator")
        return generator.throw(value)
    else:
        print("sending value into generator")
        return generator.send(value)


def _run_effect(effect):
    try:
        return effect.run()
    except AttributeError:
        print(
            "Yielded value was not an Effect, it was a {}".format(type(effect)),
            file=sys.stderr,
        )
        raise
