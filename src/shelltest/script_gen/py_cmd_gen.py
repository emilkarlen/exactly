__author__ = 'emil'

from shelltest.script_gen.config import Configuration

from shelltest.phase_instr.line_source import Line


class PythonCommand:
    """
    Base class for commands implemented in Python.
    """

    def __init__(self, source_line: Line):
        self.__source_line = source_line

    @property
    def source_line(self) -> Line:
        return self.__source_line

    def apply(self,
              configuration: Configuration):
        raise NotImplementedError()
