"""
Contains the wrapper that turns a function into one that we execute.
"""
import inspect
import typing


class _DRunnableObject:
    """
    The actual runnable object.

    This is created by ``DFunction.__call__()`` which is actually passed to the engine.
    """

    def __init__(self, fun, args, kwargs):
        self.func = fun
        self.args = args
        self.kwargs = kwargs

    def run_natively(self):
        """
        Runs a function natively.

        Used when you wish to override the Danny engine from a non-Danny function.

        .. warning::

            If this is called inside a Danny function, it is functionally equivalent to just calling the function,
            due to how the engine processes function calls recursively.

        :return: The result of the function.
        """
        return self.func(*self.args, **self.kwargs)

    def __repr__(self):
        # construct the qualname
        name = inspect.getmodule(self.func).__name__ + "." + self.func.__qualname__
        return "<_DRunnableObject for {}>".format(name)


class DFunction:
    """
    Class returned by ``with_engine``.

    :param callable_: The function to call.
    """

    def __init__(self, callable_):
        if not callable(callable_):
            raise TypeError("Object must be a callable")
        self._callable = callable_

    def __call__(self, *args, **kwargs) -> _DRunnableObject:
        """
        Returns a _DRunnableObject which is actually ran by the engine loop.

        :param args: Arguments to pass into the function.
        :param kwargs: Keyword arguments to pass into the function.

        :return: A :class:`_DRunnableObject` which can be sent into the object for executing.
        """
        return _DRunnableObject(self._callable, args, kwargs)


def with_engine(function: typing.Callable) -> DFunction:
    """
    Decorator that marks a function as running with the Danny engine.

    This returns a wrapper which, when run with ``engine.run_function(func(*args, **kwargs))``, will be executed by
    Danny.

    :param function: The function to wrap.
    :return: A :class:`danny.wrapper.DFunction`, which is then used by the engine.
    """
    return DFunction(function)
