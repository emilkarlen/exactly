from abc import ABC
from typing import Generic, Callable
from typing import TypeVar, Sequence, List

from exactly_lib.definitions.primitives import boolean
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.impls import advs
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation, MatcherAdv
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.test_case_file_structure.test_resources.application_environment import application_environment
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.util.render.test_resources import renderers as renderers_tr

MODEL = TypeVar('MODEL')


class MatcherTestImplBase(Generic[MODEL],
                          MatcherWTraceAndNegation[MODEL],
                          ABC):
    def structure(self) -> StructureRenderer:
        return renderers_tr.structure_renderer_for_arbitrary_object(self)


def sdv_from_primitive_value(
        primitive_value: MatcherWTraceAndNegation[MODEL] = MatcherWithConstantResult(True),
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


def ddv_of_unconditionally_matching_matcher() -> MatcherDdv[MODEL]:
    return MatcherDdvOfConstantMatcherTestImpl(
        MatcherWithConstantResult(True)
    )


class MatcherDdvOfConstantMatcherTestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 primitive_value: MatcherWTraceAndNegation[MODEL],
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
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
    APPLICATION_ENVIRONMENT = application_environment()

    def __init__(self,
                 make_primitive: Callable[[Tcds], MatcherWTraceAndNegation[MODEL]],
                 validator: DdvValidator = ddv_validation.constant_success_validator(),
                 ):
        self._make_primitive = make_primitive
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return (
            self.value_of_any_dependency(self.FAKE_TCDS)
                .applier(self.APPLICATION_ENVIRONMENT)
                .structure()
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return advs.ConstantMatcherAdv(
            self._make_primitive(tcds)
        )


class MatcherDdvFromParts2TestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 make_adv: Callable[[Tcds], MatcherAdv[MODEL]],
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

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return self._make_adv(tcds)


class ConstantMatcherWithCustomName(Generic[MODEL], MatcherWTraceAndNegation[MODEL]):
    def __init__(self,
                 name: str,
                 result: bool,
                 ):
        self._name = name

        self._trace_tree = tree.Node(name,
                                     result,
                                     (tree.StringDetail(boolean.BOOLEANS[result]),),
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

    @property
    def negation(self) -> 'MatcherWithConstantResult[MODEL]':
        return MatcherWithConstantResult(not self._matching_result.value)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result


T = TypeVar('T')


class ConstantMatcherWithCustomTrace(Generic[MODEL], MatcherWTraceAndNegation[MODEL]):
    def __init__(self,
                 mk_trace: Callable[[T], tree.Node[T]],
                 result: bool,
                 ):
        self._mk_trace = mk_trace

        self._matching_result = MatchingResult(
            result,
            renderers.Constant(mk_trace(result)),
        )

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return renderers.Constant(self._mk_trace(None))

    @property
    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return MatcherWithConstantResult(not self._matching_result.value)

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

    @property
    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return MatcherThatRegistersModelArgument(self._registry, not self._constant_result)

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

    @property
    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return self

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test(self.error_message))
