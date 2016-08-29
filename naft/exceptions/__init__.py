"""
Exceptions for NAFT.

These are heavily abused to turn NAFT tracebacks into human readable tracebacks.
They effectively inspect the call stack, and generate a proper human-readable traceback.

For example, they turn this unreadable traceback:

.. code::

    Traceback (most recent call last):
      File "/home/eyes/dev/naft/aa/a.py", line 20, in <module>
        result = engine.run_function(something(1))
      File "/home/eyes/dev/naft/naft/engine.py", line 114, in run_function
        result = self._run_instruction(state, instruction)
      File "/home/eyes/dev/naft/naft/engine.py", line 64, in _run_instruction
        result = func(state, instruction)
      File "/home/eyes/dev/naft/naft/ops/call.py", line 43, in handle_op_131
        result = runnable()
      File "/home/eyes/dev/naft/naft/engine.py", line 114, in run_function
        result = self._run_instruction(state, instruction)
      File "/home/eyes/dev/naft/naft/engine.py", line 64, in _run_instruction
        result = func(state, instruction)
      File "/home/eyes/dev/naft/naft/ops/load.py", line 22, in handle_op_116
        raise NameError("name '{}' is not defined".format(val))
    NameError: name 'b' is not defined

Into this:

.. code::

    Traceback (most recent call last):
      File "/home/eyes/dev/naft/aa/a.py", line 20, in <module>
        result = engine.run_function(something(1))
      File "/home/eyes/dev/naft/aa/a.py", line 16, in something
        return _something()
      File "/home/eyes/dev/naft/aa/a.py", line 10 in _something
        return b
    NameError: name 'b' is not defined
"""
