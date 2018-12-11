from __future__ import print_function

from sagathon import run_saga
from sagathon.effects import call

def my_saga():
    print('yielding call to print')
    yield call(print, 'Hello, World')

run_saga(my_saga)