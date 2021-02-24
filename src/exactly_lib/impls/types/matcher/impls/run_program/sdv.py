from typing import Generic

from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.impls.types.matcher.impls.run_program.run_conf import RunConfiguration, MODEL
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.symbol_table import SymbolTable


def sdv(run_conf: RunConfiguration[MODEL],
        program: ProgramSdv,
        ) -> MatcherSdv[MODEL]:
    def make_ddv(symbols: SymbolTable) -> MatcherSdv[MODEL]:
        return _Ddv(run_conf, program.resolve(symbols))

    return sdv_components.MatcherSdvFromParts(
        program.references,
        make_ddv,
    )


class _Ddv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 run_conf: RunConfiguration[MODEL],
                 program: ProgramDdv,
                 ):
        self._run_conf = run_conf
        self._program = program

    def structure(self) -> StructureRenderer:
        from . import trace
        return trace.TheStructureRenderer(self._program.structure())

    @property
    def validator(self) -> DdvValidator:
        return self._program.validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        from . import adv
        return adv.Adv(self._run_conf,
                       self._program.value_of_any_dependency(tcds)
                       )
