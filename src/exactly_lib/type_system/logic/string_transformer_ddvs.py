from typing import Callable

from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerAdv


class StringTransformerConstantDdv(StringTransformerDdv):
    """
    A :class:`StringTransformerResolver` that is a constant :class:`StringTransformer`
    """

    def __init__(self, value: StringTransformer):
        self._value = value

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return advs.ConstantAdv(self._value)


class DirDependentStringTransformerDdv(StringTransformerDdv):
    def __init__(self, constructor: Callable[[Tcds], StringTransformer]):
        self._constructor = constructor

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return advs.ConstantAdv(self._constructor(tcds))
