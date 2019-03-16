from __future__ import print_function

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

            def async_task():
                future_value = run_result()
                generator_stack.append(generator)
                return_stack.append(future_value)
                _run(generator_stack, return_stack)

            Thread(target=async_task).start()  # todo threadpool or something
            return

        if isinstance(run_result, GeneratorType):
            generator_stack.append(generator)
            generator_stack.append(run_result)
            return_stack.append(None)
            continue

        generator_stack.append(generator)
        return_stack.append(run_result)

    return return_stack.pop()


def _send_value(generator, value):
    if isinstance(value, Exception):
        print("throwing value into generator")
        return generator.throw(value)
    else:
        print("sending value into generator")
        return generator.send(value)


def _run_effect(effect):
    try:
        print("running effect", effect.type)
        return effect.run()
    except AttributeError:
        raise effects.NotAnEffectException(effect)
