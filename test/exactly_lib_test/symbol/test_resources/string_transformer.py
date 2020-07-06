from typing import Sequence

from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv, \
    StringTransformerModel, StringTransformerAdv
from exactly_lib.type_system.logic.string_transformer_ddvs import StringTransformerConstantDdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.type_system.logic.string_transformer.test_resources import string_transformers


def arbitrary_sdv() -> StringTransformerSdv:
    return StringTransformerSdvConstantTestImpl(string_transformers.constant(()))


class StringTransformerDdvTestImpl(StringTransformerDdv):
    def __init__(self,
                 primitive_value: StringTransformer,
                 validator: DdvValidator = constant_success_validator(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        return advs.ConstantAdv(self._primitive_value)


class StringTransformerSdvConstantTestImpl(StringTransformerSdv):
    def __init__(self,
                 resolved_value: StringTransformer,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> StringTransformer:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return StringTransformerConstantDdv(self._resolved_value)


class StringTransformerSdvConstantValueTestImpl(StringTransformerSdv):
    def __init__(self,
                 resolved_value: StringTransformerDdv,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> StringTransformerDdv:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return self._resolved_value


def string_transformer_from_primitive_value(
        primitive_value: StringTransformer = string_transformers.identity_test_impl(),
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = constant_success_validator(),
) -> StringTransformerSdv:
    return StringTransformerSdvConstantValueTestImpl(
        StringTransformerDdvTestImpl(
            primitive_value,
            validator
        ),
        references=references,
    )


def model_with_num_lines(number_of_lines: int) -> StringTransformerModel:
    return iter(['line'] * number_of_lines)


def arbitrary_transformer() -> StringTransformer:
    return string_transformers.identity_test_impl()


def arbitrary_transformer_ddv() -> StringTransformerDdv:
    return StringTransformerDdvTestImpl(arbitrary_transformer())


def arbitrary_transformer_sdv() -> StringTransformerSdv:
    return string_transformer_from_primitive_value(arbitrary_transformer())
