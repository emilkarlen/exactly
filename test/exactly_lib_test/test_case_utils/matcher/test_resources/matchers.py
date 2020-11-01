from abc import ABC
from typing import Generic, Callable
from typing import TypeVar, Sequence, List

from exactly_lib.definitions import logic
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs import ddv_validation
from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_deps.dep_variants.ddv.matcher_ddv import MatcherDdv
from exactly_lib.type_val_deps.dep_variants.sdv.matcher_sdv import MatcherSdv
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherDdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace, MatcherStdTypeVisitor
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.tcfs.test_resources.application_environment import \
    application_environment_for_test
from exactly_lib_test.tcfs.test_resources.paths import fake_tcds
from exactly_lib_test.util.render.test_resources import renderers as renderers_tr

MODEL = TypeVar('MODEL')

T = TypeVar('T')


class MatcherTestImplBase(Generic[MODEL],
                          MatcherWTrace[MODEL],
                          ABC):
    def structure(self) -> StructureRenderer:
        return renderers_tr.structure_renderer_for_arbitrary_object(self)


def sdv_from_primitive_value(
        primitive_value: MatcherWTrace[MODEL] = MatcherWithConstantResult(True),
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = ddv_validation.constant_success_validator(),
) -> MatcherSdv[MODEL]:
    return MatcherSdvOfConstantDdvTestImpl(
        MatcherDdvOfConstantMatcherTestImpl(primitive_value,
                                            validator),
        references,
    )


def sdv_from_bool(
        unconditional_result: bool = True,
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = ddv_validation.constant_success_validator(),
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
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
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
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
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
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
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


class ConstantMatcherTestImplBase(Generic[MODEL], MatcherWTrace[MODEL], ABC):
    def __init__(self, result: bool):
        self._result = result

    def accept(self, visitor: MatcherStdTypeVisitor[MODEL, T]) -> T:
        return visitor.visit_constant(self._result)


class ConstantMatcherWithCustomName(Generic[MODEL], ConstantMatcherTestImplBase[MODEL]):
    def __init__(self,
                 name: str,
                 result: bool,
                 ):
        super().__init__(result)
        self._name = name

        self._trace_tree = tree.Node(name,
                                     result,
                                     (tree.StringDetail(logic.BOOLEANS[result]),),
                                     ())
        self._matching_result = MatchingResult(
            result,
            renderers.Constant(
                self._trace_tree
            ),
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def trace_tree(self) -> tree.Node[bool]:
        return self._trace_tree

    def structure(self) -> StructureRenderer:
        return renderers.header_only(self._name)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result


class ConstantMatcherWithCustomTrace(Generic[MODEL], ConstantMatcherTestImplBase[MODEL]):
    def __init__(self,
                 mk_trace: Callable[[T], tree.Node[T]],
                 result: bool,
                 ):
        super().__init__(result)
        self._mk_trace = mk_trace

        self._matching_result = MatchingResult(
            result,
            renderers.Constant(mk_trace(result)),
        )

    @property
    def name(self) -> str:
        raise NotImplementedError('name: unsupported')

    def structure(self) -> StructureRenderer:
        return renderers.Constant(self._mk_trace(None))

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result


class MatcherThatRegistersModelArgument(Generic[MODEL], MatcherTestImplBase[MODEL]):
    def __init__(self,
                 registry: List[MODEL],
                 constant_result: bool):
        self._registry = registry
        self._constant_result = constant_result

    @property
    def name(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        self._registry.append(model)
        return MatchingResult(self._constant_result,
                              renderers.Constant(tree.Node(self.name,
                                                           self._constant_result,
                                                           (),
                                                           ())))


class MatcherThatReportsHardError(Generic[MODEL], MatcherTestImplBase[MODEL]):
    def __init__(self, error_message: str = 'unconditional hard error'):
        super().__init__()
        self.error_message = error_message

    @property
    def name(self) -> str:
        return str(type(self))

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test(self.error_message))
