from typing import Optional, Dict

from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.test_case.act_phase_handling import ActPhaseOsProcessExecutor
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value


class PredefinedProperties:
    """Properties that are forwarded to the right place in the execution."""

    def __init__(self,
                 predefined_symbols: Optional[SymbolTable] = None):
        self.__predefined_symbols = predefined_symbols

    @property
    def predefined_symbols(self) -> SymbolTable:
        return self.__predefined_symbols


class FullExeInputConfiguration(tuple):
    """Configuration that is passed to full execution"""

    def __new__(cls,
                environ: Dict[str, str],
                act_phase_os_process_executor: ActPhaseOsProcessExecutor,
                sandbox_root_dir_resolver: SandboxRootDirNameResolver,
                predefined_symbols: Optional[SymbolTable] = None):
        return tuple.__new__(cls, (environ,
                                   act_phase_os_process_executor,
                                   sandbox_root_dir_resolver,
                                   symbol_table_from_none_or_value(predefined_symbols)))

    @property
    def environ(self) -> Dict[str, str]:
        """
        The set of environment variables available to instructions.
        These may be both read and written.
        """
        return self[0]

    @property
    def act_phase_os_process_executor(self) -> ActPhaseOsProcessExecutor:
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
