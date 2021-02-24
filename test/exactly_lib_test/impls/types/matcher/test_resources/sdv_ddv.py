from typing import Sequence, Callable, Generic

from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.impls.types.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherDdv
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.matcher.test_resources.matchers import MODEL
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.type_val_deps.dep_variants.test_resources.application_environment import \
    application_environment_for_test


def sdv_from_primitive_value(
        primitive_value: MatcherWTrace[MODEL] = MatcherWithConstantResult(True),
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
) -> MatcherSdv[MODEL]:
    return MatcherSdvOfConstantDdvTestImpl(
        MatcherDdvOfConstantMatcherTestImpl(primitive_value,
                                            validator),
        references,
    )


def sdv_from_bool(
        unconditional_result: bool = True,
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
) -> MatcherSdv[MODEL]:
    return MatcherSdvOfConstantDdvTestImpl(
        MatcherDdvOfConstantMatcherTestImpl(MatcherWithConstantResult(unconditional_result),
                                            validator),
        references,
    )


def sdv_of_unconditionally_matching_matcher() -> MatcherSdv[MODEL]:
    return MatcherSdvOfConstantDdvTestImpl(ddv_of_unconditionally_matching_matcher())


def sdv_from_parts(references: Sequence[SymbolReference],
                   validator: DdvValidator,
                   matcher: Callable[[SymbolTable, TestCaseDs], MatcherWTrace[MODEL]],
                   ) -> MatcherSdv[MODEL]:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        def make_primitive(tcds: TestCaseDs) -> FileMatcher:
            return matcher(symbols, tcds)

        return MatcherDdvFromPartsTestImpl(
            make_primitive,
            validator,
        )

    return sdv_components.MatcherSdvFromParts(
        references,
        make_ddv,
    )


def ddv_of_unconditionally_matching_matcher() -> MatcherDdv[MODEL]:
    return MatcherDdvOfConstantMatcherTestImpl(
        MatcherWithConstantResult(True)
    )


class MatcherDdvOfConstantMatcherTestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 primitive_value: MatcherWTrace[MODEL],
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(self._primitive_value)


class MatcherSdvOfConstantDdvTestImpl(Generic[MODEL], MatcherSdv[MODEL]):
    def __init__(self,
                 resolved_value: MatcherDdv[MODEL],
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> MatcherDdv[MODEL]:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return self._resolved_value


class MatcherDdvFromPartsTestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    FAKE_TCDS = fake_tcds()
    APPLICATION_ENVIRONMENT = application_environment_for_test()

    def __init__(self,
                 make_primitive: Callable[[TestCaseDs], MatcherWTrace[MODEL]],
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
                 ):
        self._make_primitive = make_primitive
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return (
            self.value_of_any_dependency(self.FAKE_TCDS)
                .primitive(self.APPLICATION_ENVIRONMENT)
                .structure()
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            self._make_primitive(tcds)
        )


class MatcherDdvFromParts2TestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 make_adv: Callable[[TestCaseDs], MatcherAdv[MODEL]],
                 structure_renderer: StructureRenderer,
                 validator: DdvValidator = ddv_validation.ConstantDdvValidator.new_success(),
                 ):
        self._make_adv = make_adv
        self._validator = validator
        self._structure_renderer = structure_renderer

    def structure(self) -> StructureRenderer:
        return self._structure_renderer

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        return self._make_adv(tcds)
