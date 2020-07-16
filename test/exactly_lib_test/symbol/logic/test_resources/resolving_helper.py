from typing import Optional

from exactly_lib.symbol.logic.resolving_helper import LogicTypeResolvingHelper
from exactly_lib.test_case import os_services
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.process_execution import execution_elements
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds


def resolving_helper(
        symbols: Optional[SymbolTable] = None,
        tcds: Tcds = fake_tcds(),
        file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        os_services_: OsServices = os_services.new_default(),
        process_execution_settings: ProcessExecutionSettings = execution_elements.with_no_timeout(),
) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        (symbols if symbols is not None else empty_symbol_table()),
        tcds,
        ApplicationEnvironment(os_services_,
                               process_execution_settings,
                               file_space),
    )


def resolving_helper__fake() -> LogicTypeResolvingHelper:
    return resolving_helper()
