__author__ = 'emil'

from shelltest.exec_abs_syn.config import Configuration

from shelltest.phase_instr.line_source import Line


class PythonCommand:
    """
    Base class for commands implemented in Python.
    """

    def __init__(self):
        pass

    def apply(self,
              configuration: Configuration):
        raise NotImplementedError()
