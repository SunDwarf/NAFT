"""
Contains the wrapper that turns a function into one that we execute.
"""
import inspect
import typing


class _NRunnableObject:
    """
    The actual runnable object.

    This is created by ``DFunction.__call__()`` which is actually passed to the engine.
    """

    def __init__(self, fun, args, kwargs):
        self.func = fun
        self.args = args
        # TODO: Add proper kwargs support.
        self.kwargs = kwargs

    def run_natively(self):
        """
        Runs a function natively.

        Used when you wish to override the NAFT engine from a non-NAFT function.

        .. warning::

            If this is called inside a NAFT function, it is functionally equivalent to just calling the function,
            due to how the engine processes function calls recursively.

        :return: The result of the function.
        """
        return self.func(*self.args, **self.kwargs)

    def get_data(self) -> typing.Tuple[tuple, tuple, tuple]:
        """
        :return: Data about the function, like consts, names, and varnames.
        """
        code = self.func.__code__
        return code.co_consts, code.co_names, code.co_varnames

    def get_varnames_filled_in(self):
        """
        Gets the filled in varnames.

        This uses the args, and kwargs, to fill in varnames.
        :return: A tuple of varnames, which are filled with the arguments.
        """
        # TODO: Add proper kwargs support.
        # This is a temporary raise until I add proper keyword argument filling in.
        if self.kwargs:
            raise NotImplementedError("Keyword arguments are not implemented yet")
        # Calculate the number of arguments.
        if not self.func.__defaults__:
            n_defaults = 0
        else:
            n_defaults = len(self.func.__defaults__)
        no_of_args = self.func.__code__.co_argcount - n_defaults
        if no_of_args != len(self.args):
            raise TypeError("{}() takes {} positional arguments but {} were given".format(self.func.__qualname__,
                                                                                          no_of_args, len(self.args)))

    def __repr__(self):
        # construct the qualname
        name = inspect.getmodule(self.func).__name__ + "." + self.func.__qualname__
        return "<_DRunnableObject for {}>".format(name)


class NFunction:
    """
    Class returned by ``with_engine``.

    :param callable_: The function to call.
    """

    def __init__(self, callable_):
        if not callable(callable_):
            raise TypeError("Object must be a callable")
        self._callable = callable_

    def __call__(self, *args, **kwargs) -> _NRunnableObject:
        """
        Returns a _DRunnableObject which is actually ran by the engine loop.

        :param args: Arguments to pass into the function.
        :param kwargs: Keyword arguments to pass into the function.

        :return: A :class:`_DRunnableObject` which can be sent into the object for executing.
        """
        return _NRunnableObject(self._callable, args, kwargs)


def with_engine(function: typing.Callable) -> NFunction:
    """
    Decorator that marks a function as running with the NAFT engine.

    This returns a wrapper which, when run with ``engine.run_function(func(*args, **kwargs))``, will be executed by
    NAFT.

    :param function: The function to wrap.
    :return: A :class:`naft.wrapper.DFunction`, which is then used by the engine.
    """
    return NFunction(function)
