from shelltest.exec_abs_syn.config import Configuration


class PythonCommand:
    """
    Base class for commands implemented in Python.
    """

    def __init__(self):
        pass

    def apply(self,
              configuration: Configuration):
        raise NotImplementedError()
