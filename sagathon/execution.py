from collections import deque
from types import GeneratorType

from . import effects


class ExecutionContext:
    def __init__(self, root_generator=None):
        self.generator_stack = deque()
        self.value_stack = deque()
        if root_generator:
            self.call(root_generator)

    def __bool__(self):
        return bool(self.generator_stack and self.value_stack)

    def __iter__(self):
        yield self.generator_stack
        yield self.value_stack

    def __repr__(self):
        return "ExecutionContext({}, {})".format(self.generator_stack, self.value_stack)

    @property
    def current_generator(self):
        if self.generator_stack:
            return self.generator_stack[-1]
        return None

    @property
    def current_value(self):
        if self.value_stack:
            return self.value_stack[-1]
        return None

    @current_value.setter
    def current_value(self, value):
        if self.value_stack:
            self.value_stack[-1] = value
        else:
            self.value_stack.append(value)

    def resume(self, value):
        self.current_value = value
        return self

    def ret(self, value):
        self.generator_stack.pop()
        self.current_value = value
        return self

    def call(self, generator):
        if not isinstance(generator, GeneratorType):
            raise ValueError(
                "Expected a generator object, instead got a {} with value {}".format(
                    type(generator), generator
                )
            )
        self.generator_stack.append(generator)
        self.current_value = None
        return self


def run_execution_context(execution_context: ExecutionContext):
    while execution_context:
        generator = execution_context.current_generator
        current_value = execution_context.current_value

        try:
            effect = _send_value(generator, current_value)
        except StopIteration as e:
            print("stopping generator", generator)
            execution_context.ret(e.value)
            continue

        if not isinstance(effect, effects.Effect):
            raise effects.NotAnEffectException(effect)

        execution_context = effect(execution_context)
        pass

    return execution_context.current_value


def _send_value(generator, value):
    if isinstance(value, Exception):
        print("throwing value into generator")
        return generator.throw(value)
    else:
        print("sending value into generator")
        return generator.send(value)
