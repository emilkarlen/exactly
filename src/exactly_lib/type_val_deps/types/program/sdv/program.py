from abc import ABC, abstractmethod

from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithNodeDescriptionSdv
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdv(FullDepsWithNodeDescriptionSdv[Program], ABC):
    @abstractmethod
    def new_accumulated(self, additional: AccumulatedComponents) -> 'ProgramSdv':
        pass

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        pass
