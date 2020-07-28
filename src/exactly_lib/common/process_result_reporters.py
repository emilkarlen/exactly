from abc import ABC, abstractmethod
from typing import Callable

from exactly_lib.common import result_reporting
from exactly_lib.common.exit_value import ExitValue
from exactly_lib.common.process_result_reporter import ProcessResultReporter, Environment
from exactly_lib.util.file_printer import FilePrinter
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.render.renderer import SequenceRenderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock


class ProcessResultReporterWithInitialExitValueOutput(ProcessResultReporter):
    def __init__(self,
                 exit_value: ExitValue,
                 exit_value_printer: ProcOutputFile,
                 output_rest: Callable[[Environment], None],
                 ):
        self._exit_value = exit_value
        self._exit_value_printer = exit_value_printer
        self._output_rest = output_rest

    def report(self, environment: Environment) -> int:
        _output_exit_value(environment.std_file_printers.get(self._exit_value_printer),
                           self._exit_value)
        self._output_rest(environment)
        return self._exit_value.exit_code


class ProcessResultReporterOfMajorBlocksBase(ProcessResultReporter, ABC):
    def __init__(self,
                 exit_code: int,
                 output_printer: ProcOutputFile,
                 ):
        self._exit_code = exit_code
        self._output_printer = output_printer

    def report(self, environment: Environment) -> int:
        result_reporting.print_major_blocks(self._blocks(),
                                            environment.std_file_printers.get(self._output_printer))
        return self._exit_code

    @abstractmethod
    def _blocks(self) -> SequenceRenderer[MajorBlock]:
        pass


class ProcessResultReporterOfExitCodeAndMajorBlocksBase(ProcessResultReporter, ABC):
    def __init__(self,
                 exit_value_file: ProcOutputFile,
                 blocks_file: ProcOutputFile,
                 ):
        self._exit_value_file = exit_value_file
        self._blocks_file = blocks_file

    @abstractmethod
    def _exit_value(self) -> ExitValue:
        pass

    def report(self, environment: Environment) -> int:
        exit_value = self._exit_value()
        _output_exit_value(environment.std_file_printers.get(self._exit_value_file), exit_value)

        result_reporting.print_major_blocks(self._blocks(),
                                            environment.std_file_printers.get(self._blocks_file))

        return exit_value.exit_code

    @abstractmethod
    def _blocks(self) -> SequenceRenderer[MajorBlock]:
        pass


def _output_exit_value(printer: FilePrinter, exit_value: ExitValue):
    printer.write_colored_line(exit_value.exit_identifier,
                               exit_value.color)
    printer.flush()
