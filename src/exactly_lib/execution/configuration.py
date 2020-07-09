from typing import Optional, Dict

from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.test_case.actor import AtcOsProcessExecutor
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value


class PredefinedProperties:
    """
    Properties that are forwarded to the right place in the execution.

    (worst doc ever???)
    """

    def __init__(self,
                 environ: Dict[str, str],
                 predefined_symbols: Optional[SymbolTable] = None):
        self.__environ = environ
        self.__predefined_symbols = predefined_symbols

    @staticmethod
    def new_empty():
        return PredefinedProperties({}, None)

    @property
    def environ(self) -> Dict[str, str]:
        return self.__environ

    @property
    def predefined_symbols(self) -> SymbolTable:
        return self.__predefined_symbols


class ExecutionConfiguration(tuple):
    """Configuration that is passed to full execution"""

    def __new__(cls,
                environ: Dict[str, str],
                act_phase_os_process_executor: AtcOsProcessExecutor,
                sandbox_root_dir_resolver: SandboxRootDirNameResolver,
                predefined_symbols: Optional[SymbolTable] = None,
                exe_atc_and_skip_assertions: Optional[StdOutputFiles] = None):
        return tuple.__new__(cls, (environ,
                                   act_phase_os_process_executor,
                                   sandbox_root_dir_resolver,
                                   symbol_table_from_none_or_value(predefined_symbols),
                                   exe_atc_and_skip_assertions))

    @property
    def environ(self) -> Dict[str, str]:
        """
        The set of environment variables available to instructions.
        These may be both read and written.
        """
        return self[0]

    @property
    def atc_os_process_executor(self) -> AtcOsProcessExecutor:
        return self[1]

    @property
    def sds_root_dir_resolver(self) -> SandboxRootDirNameResolver:
        return self[2]

    @property
    def predefined_symbols(self) -> SymbolTable:
        """
        Symbols that should be available in all steps.

        Should probably not be updated.
        """
        return self[3]

    @property
    def exe_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        """
        If not None, the output from the Action To Check should
        be executed with output directed to the given files,
        and assertions should be skipped.
        """
        return self[4]
