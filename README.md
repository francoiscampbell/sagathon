# sagathon
Redux-saga, without redux, for python

An experiment

```python
from __future__ import print_function  # if you're using python 2

from sagathon import run_saga
from sagathon.effects import call

def my_saga():
    yield call(print, 'Hello, World')

run_saga(my_saga)
```
