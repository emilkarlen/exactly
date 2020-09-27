from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerAdv


class StringTransformerConstantDdv(StringTransformerDdv):
    """
    A :class:`StringTransformerResolver` that is a constant :class:`StringTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = value

    def structure(self) -> StructureRenderer:
        return self._value.structure()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
        return advs.ConstantAdv(self._value)
