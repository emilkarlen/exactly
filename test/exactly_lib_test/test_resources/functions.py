from typing import Callable, List


class Sequence:
    """
    A callable that invokes every callable in a given list of callables.

    Return value is None     
    """

    def __init__(self, list_of_callable: List[Callable]):
        self.list_of_callable = list_of_callable

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def call(self, *args, **kwargs):
        for fun in self.list_of_callable:
            fun(*args, **kwargs)


def sequence_of_actions(list_of_callable: List[Callable]) -> Callable:
    def ret_val(*args, **kwargs):
        for fun in list_of_callable:
            fun(*args, **kwargs)

    return ret_val
