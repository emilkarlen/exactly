from typing import Optional

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.resolving_helper import LogicTypeResolvingHelper
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.process_execution import execution_elements
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds


def resolving_helper(
        symbols: Optional[SymbolTable] = None,
        tcds: TestCaseDs = fake_tcds(),
        file_space: DirFileSpace = DirFileSpaceThatMustNoBeUsed(),
        os_services_: OsServices = os_services_access.new_for_current_os(),
        process_execution_settings: ProcessExecutionSettings = execution_elements.with_no_timeout(),
        mem_buff_size: int = 2 ** 10,
) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        (symbols if symbols is not None else empty_symbol_table()),
        tcds,
        ApplicationEnvironment(os_services_,
                               process_execution_settings,
                               file_space,
                               mem_buff_size),
    )


def resolving_helper__fake() -> LogicTypeResolvingHelper:
    return resolving_helper()
