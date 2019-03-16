from __future__ import print_function

import time

from sagathon import run_saga
from sagathon.effects import Call, CallAsync, Ret


start = time.time()


def intercept_call_to_print(value):
    fn, args, kwargs = value
    if fn == print:
        return fn, (args[0] * 2, *args[1:]), kwargs
    return fn, args, kwargs


Call.add_pre_run_interceptor(intercept_call_to_print)


def intercept_io_return_value(_, return_value):
    if isinstance(return_value, int):
        return return_value * 2
    return return_value


CallAsync.add_post_run_interceptor(intercept_io_return_value)


def my_saga():
    print("yielding call to print")
    yield Call(print, "\nHello, World\n")
    text = yield Call(my_ret_saga)
    yield Call(my_sub_saga, text)
    yield Call(my_slow_saga, 5)
    yield Call(print, "\ngot async\n")
    yield Call(print, "\ngot async\n")
    yield Call(print, "\ngot async\n")
    yield Call(print, "\ngot async\n")
    yield Call(print, "\ngot async\n")
    yield Call(print, "\ngot async\n")
    yield Ret("\nDone saga\n")


def my_ret_saga():
    return "\nHello, World again\n"


def my_sub_saga(text):
    yield Call(print, text)
    yield Call(my_sub_saga_2, 20)


def my_sub_saga_2(val):
    yield Call(my_sub_saga_3, val + 2)


def my_sub_saga_3(val):
    pass
    # raise KeyError(val)


def my_slow_saga(sleep_time):
    async_value = yield CallAsync(my_io_function, sleep_time)
    yield Call(print, "\nasync value\n", async_value)


def my_io_function(sleep_time):
    time.sleep(sleep_time)
    print("app started {} seconds ago".format(time.time() - start))
    return sleep_time ** 2


print(run_saga(my_saga))
print(run_saga(my_slow_saga, 2))
print(run_saga(my_slow_saga, 4))
