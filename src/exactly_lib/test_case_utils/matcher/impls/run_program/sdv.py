from typing import Callable, Generic

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.matcher.impls.run_program.runner import Runner, MODEL
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherAdv
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.util.symbol_table import SymbolTable


def sdv(mk_runner: Callable[[ApplicationEnvironment], Runner[MODEL]],
        program: ProgramSdv,
        ) -> MatcherSdv[MODEL]:
    def make_ddv(symbols: SymbolTable) -> MatcherSdv[MODEL]:
        return _Ddv(mk_runner, program.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        program.references,
        make_ddv,
    )


class _Ddv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 mk_runner: Callable[[ApplicationEnvironment], Runner[MODEL]],
                 program: ProgramDdv,
                 ):
        self._mk_runner = mk_runner
        self._program = program

    def structure(self) -> StructureRenderer:
        from . import adv
        return adv.Matcher.new_structure_tree(self._program.structure())

    @property
    def validator(self) -> DdvValidator:
        return self._program.validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        from . import adv
        return adv.Adv(self._mk_runner,
                       self._program.value_of_any_dependency(tcds)
                       )
