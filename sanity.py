from __future__ import print_function

import time

from sagathon import run_saga
from sagathon.effects import Call, CallAsync, Ret


start = time.time()


def my_saga():
    print("yielding call to print")
    yield Call(print, "\nHello, World\n")
    text = yield Call(my_ret_saga)
    yield Call(my_sub_saga, text)
    yield Ret("\nDone saga\n")


def my_ret_saga():
    return "\nHello, World again\n"


def my_sub_saga(text):
    yield Call(print, text)


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
