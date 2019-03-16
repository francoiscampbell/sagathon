from __future__ import print_function

from sagathon import run_saga
from sagathon.effects import Call, Ret


def my_saga():
    print("yielding call to print")
    yield Call(print, "Hello, World")
    text = yield Call(my_ret_saga)
    yield Call(my_sub_saga, text)


def my_ret_saga():
    return "Hello, World again"


def my_sub_saga(text):
    yield Call(print, text)


run_saga(my_saga)
