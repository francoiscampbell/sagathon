from __future__ import print_function

from sagathon import run_saga
from sagathon.effects import Call, Ret


def my_saga():
    print("yielding call to print")
    yield Call(print, "\nHello, World\n")
    text = yield Call(my_ret_saga)
    yield Call(my_sub_saga, text)
    yield Ret("Done saga")


def my_ret_saga():
    return "\nHello, World again\n"


def my_sub_saga(text):
    yield Call(print, text)


print(run_saga(my_saga))
