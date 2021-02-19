from typing import Optional, Dict, Mapping

from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value


class PredefinedProperties:
    """
    Properties that are forwarded to the right place in the execution.

    (worst doc ever???)
    """

    def __init__(self,
                 default_environ_getter: DefaultEnvironGetter,
                 environ: Optional[Dict[str, str]],
                 timeout_in_seconds: Optional[int],
                 predefined_symbols: Optional[SymbolTable] = None,
                 ):
        self._default_environ_getter = default_environ_getter
        self._environ = environ
        self._timeout_in_seconds = timeout_in_seconds
        self._predefined_symbols = predefined_symbols

    @property
    def environ(self) -> Optional[Dict[str, str]]:
        return self._environ

    @property
    def default_environ_getter(self) -> DefaultEnvironGetter:
        """
        Each invokation of the returned function must give a new instance (since it may be modified)
        """
        return self._default_environ_getter

    @property
    def timeout_in_seconds(self) -> Optional[int]:
        return self._timeout_in_seconds

    @property
    def predefined_symbols(self) -> Optional[SymbolTable]:
        return self._predefined_symbols


class ExecutionConfiguration(tuple):
    """Configuration that is passed to full execution"""

    def __new__(cls,
                default_environ_getter: DefaultEnvironGetter,
                environ: Optional[Mapping[str, str]],
                timeout_in_seconds: Optional[int],
                os_services: OsServices,
                sandbox_root_dir_resolver: SandboxRootDirNameResolver,
                mem_buff_size: int,
                predefined_symbols: Optional[SymbolTable] = None,
                exe_atc_and_skip_assertions: Optional[StdOutputFiles] = None,
                ):
        return tuple.__new__(cls, (environ,
                                   sandbox_root_dir_resolver,
                                   symbol_table_from_none_or_value(predefined_symbols),
                                   exe_atc_and_skip_assertions,
                                   os_services,
                                   mem_buff_size,
                                   default_environ_getter,
                                   timeout_in_seconds))

    @property
    def environ(self) -> Optional[Mapping[str, str]]:
        """
        The set of environment variables available to instructions.
        """
        return self[0]

    @property
    def default_environ_getter(self) -> DefaultEnvironGetter:
        """
        The set of environment variables to use as default, when the environ is None.
        """
        return self[6]

    @property
    def timeout_in_seconds(self) -> Optional[int]:
        return self[7]

    @property
    def os_services(self) -> OsServices:
        return self[4]

    @property
    def sds_root_dir_resolver(self) -> SandboxRootDirNameResolver:
        return self[1]

    @property
    def predefined_symbols(self) -> SymbolTable:
        """
        Symbols that should be available in all steps.

        Should probably not be updated.
        """
        return self[2]

    @property
    def exe_atc_and_skip_assertions(self) -> Optional[StdOutputFiles]:
        """
        If not None, the output from the Action To Check should
        be executed with output directed to the given files,
        and assertions should be skipped.
        """
        return self[3]

    @property
    def mem_buff_size(self) -> int:
        return self[5]
