class Sequence:
    """
    A callable that invokes every callable in a given list of callables.

    Return value is None     
    """

    def __init__(self, list_of_callable: list):
        self.list_of_callable = list_of_callable

    def __call__(self, *args, **kwargs):
        for fun in self.list_of_callable:
            fun(*args, **kwargs)
