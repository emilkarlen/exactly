from typing import Sequence, Iterator

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator, \
    ConstantDdvValidator
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.ddvs import StringTransformerConstantDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def arbitrary_sdv() -> StringTransformerSdv:
    return StringTransformerSdvConstantTestImpl(string_transformers.arbitrary())


class StringTransformerDdvTestImpl(StringTransformerDdv):
    def __init__(self,
                 primitive_value: StringTransformer,
                 validator: DdvValidator = ConstantDdvValidator.new_success(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> StringTransformerAdv:
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
        validator: DdvValidator = ConstantDdvValidator.new_success(),
) -> StringTransformerSdv:
    return StringTransformerSdvConstantValueTestImpl(
        StringTransformerDdvTestImpl(
            primitive_value,
            validator
        ),
        references=references,
    )


def model_with_num_lines(number_of_lines: int) -> Iterator[str]:
    return iter(['line'] * number_of_lines)


def arbitrary_transformer_ddv() -> StringTransformerDdv:
    return StringTransformerDdvTestImpl(string_transformers.arbitrary())


def arbitrary_transformer_sdv() -> StringTransformerSdv:
    return string_transformer_from_primitive_value(string_transformers.arbitrary())
