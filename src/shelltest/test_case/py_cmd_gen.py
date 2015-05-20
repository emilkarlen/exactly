from shelltest.test_case.config import Configuration


class PythonCommand:
    """
    Base class for commands implemented in Python.
    """

    def __init__(self):
        pass

    def apply(self,
              configuration: Configuration):
        raise NotImplementedError()
