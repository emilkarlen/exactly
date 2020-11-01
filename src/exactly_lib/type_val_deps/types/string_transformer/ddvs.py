from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_transformer import StringTransformer


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
