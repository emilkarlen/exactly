from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.impl.base_class import FileMatcherDdvImplBase
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.file_matcher import FileMatcherSdv, FileMatcherDdv, FileMatcherAdv
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.util.symbol_table import SymbolTable


def sdv(program: ProgramSdv) -> FileMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        return _Ddv(program.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        program.references,
        make_ddv,
    )


class _Ddv(FileMatcherDdvImplBase):
    def __init__(self, program: ProgramDdv):
        self._program = program

    def structure(self) -> StructureRenderer:
        from . import adv
        return adv.Matcher.new_structure_tree(self._program.structure())

    @property
    def validator(self) -> DdvValidator:
        return self._program.validator

    def value_of_any_dependency(self, tcds: Tcds) -> FileMatcherAdv:
        from . import adv
        return adv.Adv(self._program.value_of_any_dependency(tcds))
