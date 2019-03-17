import inspect
import logging
from collections import deque
from types import GeneratorType

from . import effects


log = logging.getLogger(__name__)


class GeneratorWrapper:
    def __init__(self, generator):
        if not isinstance(generator, GeneratorType):
            raise ValueError(
                "Expected a generator object, instead got a {} with value {}".format(
                    type(generator), generator
                )
            )
        self.generator = generator

    def __str__(self):
        return self.generator.__name__

    def stack_frame_str(self):
        generator = self.generator
        filename = inspect.getsourcefile(generator.gi_code)
        source_lines, first_line_number = inspect.getsourcelines(generator.gi_code)
        if generator.gi_frame:
            current_line_number = inspect.getlineno(generator.gi_frame)
            current_line_number_str = str(current_line_number)
        else:
            current_line_number = first_line_number + 1
            current_line_number_str = "{} (approximate)".format(current_line_number)

        line_index = current_line_number - first_line_number
        source_at_line = source_lines[line_index]

        return 'File "{}", line {}, in {}\n{}'.format(
            filename, current_line_number_str, self, source_at_line.replace("\n", "")
        )

    def resume(self, value):
        if isinstance(value, Exception):
            log.debug("Throwing value %s into generator %s", value, self)
            return self.generator.throw(value)
        else:
            log.debug("Sending value %s into generator %s", value, self)
            return self.generator.send(value)


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
        current_value = self.current_value
        log.debug(
            "Executing generator %s with value %s", current_generator, current_value
        )
        return current_generator, current_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        return not (exc_type and exc_val and exc_tb)

    def _create_traceback(self):
        return "".join(
            "\n  {}".format(generator.stack_frame_str())
            for generator in self.generator_stack
        )

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
        log.debug(
            "Resuming execution of generator %s with value %s",
            self.current_generator,
            value,
        )
        self.current_value = value
        return self

    def ret(self, value):
        log.debug(
            "Returning from generator %s with value %s", self.current_generator, value
        )
        self.generator_stack.pop()
        self.current_value = value
        return self

    def call(self, generator):
        wrapped = GeneratorWrapper(generator)
        log.debug("Calling generator %s", wrapped)
        self.generator_stack.append(wrapped)
        self.push_value(None)
        return self


def run_execution_context(execution_context: ExecutionContext):
    try:
        while execution_context:
            with execution_context as (generator, current_value):
                try:
                    effect = generator.resume(current_value)
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


class SagaExecutionException(Exception):
    pass
