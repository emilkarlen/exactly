from typing import Optional

from exactly_lib.symbol.logic.resolving_helper import LogicTypeResolvingHelper
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed, TmpDirFileSpace
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds


def resolving_helper(
        symbols: Optional[SymbolTable] = None,
        tcds: Tcds = fake_tcds(),
        file_space: TmpDirFileSpace = TmpDirFileSpaceThatMustNoBeUsed(),
) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        (symbols if symbols is not None else empty_symbol_table()),
        tcds,
        ApplicationEnvironment(file_space),
    )


def resolving_helper__fake() -> LogicTypeResolvingHelper:
    return resolving_helper()
