from __future__ import print_function

import sys
from collections import deque
from threading import Thread
from types import GeneratorType

import effects


def run_saga(saga, *args, **kwargs):
    generator = saga(*args, **kwargs)
    return _run(deque([generator]), deque([None]))


def _run(generator_stack, return_stack):
    while generator_stack and return_stack:
        generator = generator_stack.pop()
        run_result = return_stack.pop()
        try:
            effect = _send_value(generator, run_result)
            print("got effect", effect.type)
        except StopIteration as e:
            print("stopping generator", generator)
            return_stack.append(getattr(e, "value", None))
            continue

        try:
            run_result = _run_effect(effect)
        except Exception as e:
            generator_stack.append(generator)
            return_stack.append(e)
            continue

        if isinstance(effect, effects.Ret):
            return_stack.append(run_result)
            continue

        if isinstance(effect, effects.CallAsync):
            _queue_async_task(run_result, generator)
            return

        if isinstance(run_result, GeneratorType):
            generator_stack.append(generator)
            generator_stack.append(run_result)
            return_stack.append(None)
            continue

        generator_stack.append(generator)
        return_stack.append(run_result)

    return return_stack.pop()


def _queue_async_task(future, generator):
    def async_task():
        future_value = future()
        _run(deque([generator]), deque([future_value]))

    Thread(target=async_task).start()


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
