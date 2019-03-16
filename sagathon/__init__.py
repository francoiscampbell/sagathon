from __future__ import print_function


from . import effects
from .execution import ExecutionContext, run_execution_context


def run_saga(saga, *args, **kwargs):
    generator = saga(*args, **kwargs)
    execution_context = ExecutionContext(generator)
    return run_execution_context(execution_context)
