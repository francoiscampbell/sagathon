from __future__ import print_function

from sagathon import run_saga
from sagathon.effects import Call


def my_saga():
    print("yielding call to print")
    yield Call(print, "Hello, World")
    yield Call(my_sub_saga, "Hello, World again")


def my_sub_saga(text):
    yield Call(print, text)


run_saga(my_saga)
