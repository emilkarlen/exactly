from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeStv, LogicWithStructureSdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.type_system.value_type import LogicValueType, ValueType


class StringTransformerSdv(LogicWithStructureSdv[StringTransformer]):
    pass


class StringTransformerStv(LogicTypeStv[StringTransformer]):
    def __init__(self, sdv: StringTransformerSdv):
        self._sdv = sdv

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.STRING_TRANSFORMER

    @property
    def value_type(self) -> ValueType:
        return ValueType.STRING_TRANSFORMER

    def value(self) -> StringTransformerSdv:
        return self._sdv
