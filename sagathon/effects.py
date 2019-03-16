from __future__ import print_function

from threading import Thread
from types import GeneratorType

from .execution import ExecutionContext, run_execution_context


class EffectMetaclass(type):
    def __init__(cls, *args, **kwargs):
        super(EffectMetaclass, cls).__init__(*args, **kwargs)
        cls._pre_run_interceptors = []
        cls._post_run_interceptors = []

    def add_pre_run_interceptor(cls, interceptor):
        cls._pre_run_interceptors.append(interceptor)

    def remove_pre_run_interceptor(cls, interceptor):
        cls._pre_run_interceptors.remove(interceptor)

    def add_post_run_interceptor(cls, interceptor):
        cls._post_run_interceptors.append(interceptor)

    def remove_post_run_interceptor(cls, interceptor):
        cls._post_run_interceptors.remove(interceptor)


class Effect(object, metaclass=EffectMetaclass):
    def __init__(self, value):
        self.type = type(self).__name__
        self.value = value
        # print("making {} effect with value {}".format(self.type, value))

    def __call__(self, execution_context: ExecutionContext):
        value = self._get_intercepted_input_value()
        try:
            return self.run(execution_context, value)
        except Exception as e:
            return execution_context.resume(e)

    def run(self, execution_context, value):
        raise NotImplemented("Effect {} does not override run()".format(self.type))

    def _get_intercepted_input_value(self):
        value = self.value
        for interceptor in self._pre_run_interceptors:
            value = interceptor(value)
        return value

    def _get_intercepted_return_value(self, return_value):
        for interceptor in self._post_run_interceptors:
            return_value = interceptor(self.value, return_value)
        return return_value

    def _resume_execution(self, execution_context, return_value):
        return_value = self._get_intercepted_return_value(return_value)
        if isinstance(return_value, GeneratorType):
            return execution_context.call(return_value)
        return execution_context.resume(return_value)


class Call(Effect):
    def __init__(self, fn, *args, **kwargs):
        super(Call, self).__init__((fn, args, kwargs))

    def run(self, execution_context, value):
        fn, args, kwargs = value
        # print("running call effect for fn ", fn)
        return_value = fn(*args, **kwargs)
        return self._resume_execution(execution_context, return_value)


class CallAsync(Call):
    def run(self, execution_context, value):
        def async_task():
            new_execution_context = super(CallAsync, self).run(execution_context, value)
            run_execution_context(new_execution_context)

        Thread(target=async_task).start()  # todo threadpool or something
        return ExecutionContext()


class Ret(Effect):
    def run(self, execution_context, value):
        # print("running ret effect with value", value)
        return execution_context.ret(value)


class NotAnEffectException(Exception):
    def __init__(self, actual):
        super(NotAnEffectException, self).__init__(
            "Yielded value was not an Effect, it was a {} with value {}".format(
                type(actual), actual
            )
        )
