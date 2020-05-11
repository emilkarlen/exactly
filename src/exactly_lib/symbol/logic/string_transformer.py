from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeStv, LogicWithStructureSdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer


class StringTransformerSdv(LogicWithStructureSdv[StringTransformer]):
    pass


class StringTransformerStv(LogicTypeStv[StringTransformer]):
    def __init__(self, sdv: StringTransformerSdv):
        self._sdv = sdv

    def value(self) -> StringTransformerSdv:
        return self._sdv
