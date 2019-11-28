from typing import TypeVar, Generic, Sequence, Optional, List

from exactly_lib.definitions.primitives import boolean
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation, MatchingResult, \
    Failure, T
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test
from exactly_lib_test.util.render.test_resources import renderers as renderers_tr

MODEL = TypeVar('MODEL')


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


def sdv_of_unconditionally_matching_matcher() -> MatcherSdv[MODEL]:
    return MatcherSdvOfConstantDdvTestImpl(ddv_of_unconditionally_matching_matcher())


def ddv_of_unconditionally_matching_matcher() -> MatcherDdv[MODEL]:
    return MatcherDdvOfConstantMatcherTestImpl(
        MatcherWithConstantResult(True)
    )


class MatcherDdvOfConstantMatcherTestImpl(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 primitive_value: MatcherWTraceAndNegation[MODEL],
                 validator: DdvValidator =
                 ddv_validation.constant_success_validator(),
                 ):
        self._primitive_value = primitive_value
        self._validator = validator

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherWTraceAndNegation[MODEL]:
        return self._primitive_value


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


class ConstantMatcherWithCustomName(Generic[MODEL], MatcherWTraceAndNegation[MODEL]):
    def __init__(self,
                 name: str,
                 result: bool,
                 ):
        self._name = name

        self._matching_result = MatchingResult(
            result,
            renderers.Constant(
                tree.Node(name, result,
                          (tree.StringDetail(boolean.BOOLEANS[result]),),
                          ())
            ),
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def option_description(self) -> str:
        return self.name

    @property
    def negation(self) -> 'MatcherWithConstantResult[MODEL]':
        return MatcherWithConstantResult(not self._matching_result.value)

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        return self._matching_result

    def matches_w_failure(self, model: MODEL) -> Optional[Failure[MODEL]]:
        raise NotImplementedError('deprecated')

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('deprecated')


class MatcherThatRegistersModelArgument(Generic[MODEL], MatcherWTraceAndNegation[MODEL]):
    def __init__(self,
                 registry: List[MODEL],
                 constant_result: bool):
        self._registry = registry
        self._constant_result = constant_result

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        raise NotImplementedError('this method should not be used')

    @property
    def negation(self) -> MatcherWTraceAndNegation[MODEL]:
        return MatcherThatRegistersModelArgument(self._registry, not self._constant_result)

    def matches(self, model: MODEL) -> bool:
        self._registry.append(model)
        return self._constant_result

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        self._registry.append(model)
        return MatchingResult(self._constant_result,
                              renderers.Constant(tree.Node(self.name,
                                                           self._constant_result,
                                                           (),
                                                           ())))


class MatcherThatReportsHardError(Generic[T], MatcherWTraceAndNegation[T]):
    def __init__(self, error_message: str = 'unconditional hard error'):
        super().__init__()
        self.error_message = error_message

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return 'unconditional HARD ERROR'

    def _structure(self) -> StructureRenderer:
        return renderers_tr.structure_renderer_for_arbitrary_object(self)

    @property
    def negation(self) -> MatcherWTraceAndNegation[T]:
        return self

    def matches_w_trace(self, model: T) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test(self.error_message))

    def matches(self, model: T) -> bool:
        raise HardErrorException(new_single_string_text_for_test(self.error_message))
