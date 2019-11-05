from typing import Sequence, Set, Optional

from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.line_matcher.impl.impl_base_classes import LineMatcherImplBase
from exactly_lib.test_case_utils.line_matcher.line_matcher_values import LineMatcherValueFromPrimitiveValue
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import ResolverSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.render.test_resources import renderers


def arbitrary_resolver() -> LineMatcherResolver:
    return LineMatcherResolverConstantTestImpl(
        LineMatcherConstantTestImpl(True)
    )


class LineMatcherConstantTestImpl(LineMatcherImplBase):
    """Matcher with constant result."""

    def __init__(self, result: bool):
        super().__init__()
        self._result = result

    @property
    def name(self) -> str:
        return self.option_description

    def _structure(self) -> StructureRenderer:
        return renderers.structure_renderer_for_arbitrary_object(self)

    @property
    def option_description(self) -> str:
        return 'any line' if self._result else 'no line'

    @property
    def result_constant(self) -> bool:
        return self._result

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        return self._new_tb().build_result(self._result)

    def matches(self, line: LineMatcherLine) -> bool:
        return self._result


class LineMatcherValueTestImpl(LineMatcherValue):
    def __init__(self,
                 primitive_value: LineMatcher,
                 validator: PreOrPostSdsValueValidator = constant_success_validator(),
                 resolving_dependencies: Optional[Set[DirectoryStructurePartition]] = None):
        self._primitive_value = primitive_value
        self._validator = validator
        self._resolving_dependencies = resolving_dependencies

    def structure(self) -> StructureRenderer:
        return self._primitive_value.structure()

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        return self._primitive_value

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> LineMatcher:
        return self._primitive_value


class LineMatcherResolverConstantTestImpl(LineMatcherResolver):
    def __init__(self,
                 resolved_value: LineMatcher,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> LineMatcher:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return LineMatcherValueTestImpl(self._resolved_value)


class LineMatcherResolverConstantValueTestImpl(LineMatcherResolver):
    def __init__(self,
                 resolved_value: LineMatcherValue,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> LineMatcher:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return self._resolved_value


IS_LINE_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.LINE_MATCHER)


def is_line_matcher_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_LINE_MATCHER_REFERENCE_RESTRICTION)


def is_line_matcher_reference_to__ref(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                         IS_LINE_MATCHER_REFERENCE_RESTRICTION)
    )


def successful_matcher_with_validation(validator: PreOrPostSdsValueValidator):
    return LineMatcherResolverConstantValueTestImpl(
        LineMatcherValueTestImpl(
            LineMatcherConstantTestImpl(True),
            validator
        )
    )


def line_matcher_from_primitive_value(resolved_value: LineMatcher = LineMatcherConstantTestImpl(True),
                                      references: Sequence[SymbolReference] = (),
                                      validator: PreOrPostSdsValueValidator = constant_success_validator(),
                                      ) -> LineMatcherResolver:
    return LineMatcherResolverConstantValueTestImpl(
        LineMatcherValueTestImpl(resolved_value,
                                 validator),
        references=references,
    )


def resolver_of_unconditionally_matching_matcher() -> LineMatcherResolver:
    return LineMatcherResolverConstantTestImpl(LineMatcherConstantTestImpl(True))


def value_of_unconditionally_matching_matcher() -> LineMatcherValue:
    return LineMatcherValueFromPrimitiveValue(
        LineMatcherConstantTestImpl(True)
    )


class LineMatcherSymbolContext(ResolverSymbolContext[LineMatcherResolver]):
    def __init__(self,
                 name: str,
                 resolver: LineMatcherResolver):
        super().__init__(name)
        self._resolver = resolver

    @property
    def resolver(self) -> LineMatcherResolver:
        return self._resolver

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_line_matcher_reference_to__ref(self.name)
