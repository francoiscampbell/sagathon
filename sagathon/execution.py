import itertools
import logging
from collections import deque
from types import GeneratorType

from . import effects


log = logging.getLogger(__name__)


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

    def __str__(self):
        return "\n\nSaga Traceback (most recent call last): {}".format(
            self._create_traceback()
        )

    def __enter__(self):
        current_generator = self.generator_stack[-1]
        return current_generator, self.current_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        return not (exc_type and exc_val and exc_tb)

    def _create_traceback(self):
        return "".join(
            "\n  {}\n    {}".format(generator, self._oneline(value))
            for generator, value in itertools.zip_longest(
                self.generator_stack, self.value_stack
            )
        )

    @staticmethod
    def _oneline(value):
        return str(value).replace("\n", "\\n")

    @property
    def current_generator(self):
        return self.generator_stack[-1]

    @property
    def current_value(self):
        return self.value_stack[-1]

    @current_value.setter
    def current_value(self, value):
        self.value_stack[-1] = value

    def pop_value(self):
        if self.value_stack:
            return self.value_stack.pop()
        return None

    def push_value(self, value):
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
        self.push_value(None)
        return self


def run_execution_context(execution_context: ExecutionContext):
    try:
        while execution_context:
            with execution_context as (generator, current_value):
                try:
                    effect = _send_value(generator, current_value)
                except StopIteration as e:
                    log.debug("Stopping generator %s", generator)
                    execution_context.ret(e.value)
                    continue

                if not isinstance(effect, effects.Effect):
                    raise effects.NotAnEffectException(effect)

                execution_context = effect(execution_context)
                pass  # for breakpoint

        return execution_context.pop_value()
    except Exception as e:
        message = str(execution_context)
        raise SagaExecutionException(message) from e


def _send_value(generator, value):
    if isinstance(value, Exception):
        # print("throwing value into generator")
        return generator.throw(value)
    else:
        # print("sending value into generator")
        return generator.send(value)


class SagaExecutionException(Exception):
    pass
