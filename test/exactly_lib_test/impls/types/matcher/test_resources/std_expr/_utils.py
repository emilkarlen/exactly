import itertools
import unittest
from abc import ABC, abstractmethod
from typing import Generic, List, Sequence, Tuple, TypeVar, Optional, Callable

from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import tree, renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, PrimAndExeExpectation
from exactly_lib_test.impls.types.matcher.test_resources import matchers
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.impls.types.matcher.test_resources.std_expr.configuration import MODEL, MatcherConfiguration
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments
from exactly_lib_test.test_resources.test_utils import NExArr, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.ddv.test_resources import ddv_validators
from exactly_lib_test.type_val_deps.test_resources.any_.restrictions_assertions import \
    is_reference_restrictions__value_type__single
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationActual, \
    failing_validation_cases, \
    ValidationAssertions
from exactly_lib_test.type_val_deps.types.test_resources.matcher_symbol_context import MatcherSymbolValueContext, \
    MatcherTypeSymbolContext
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree, \
    rendering_assertions as asrt_trace_rendering

MatcherNameAndResult = Tuple[str, bool]

T = TypeVar('T')


def get_mk_operand_trace(operand_name: str) -> Callable[[T], tree.Node[T]]:
    def ret_val(data: T) -> tree.Node[T]:
        return tree.Node.empty(operand_name, data)

    return ret_val


class MatcherBehaviour(ABC):
    @abstractmethod
    def accept(self, visitor: '_MatcherBehaviourVisitor[T]') -> T:
        raise NotImplementedError('abstract method')


class ConstantIncludedInTrace(MatcherBehaviour):
    def __init__(self, result: bool):
        self.result = result

    def accept(self, visitor: '_MatcherBehaviourVisitor[T]') -> T:
        return visitor.visit_constant(self)


class IgnoredDueToLaziness(MatcherBehaviour):
    def accept(self, visitor: '_MatcherBehaviourVisitor[T]') -> T:
        return visitor.visit_ignored(self)


class _MatcherBehaviourVisitor(Generic[T], ABC):
    @abstractmethod
    def visit_constant(self, x: ConstantIncludedInTrace) -> T:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def visit_ignored(self, x: IgnoredDueToLaziness) -> T:
        raise NotImplementedError('abstract method')


class Case:
    def __init__(self,
                 name: str,
                 expected_result: bool,
                 operands: List[MatcherBehaviour],
                 ):
        self.name = name
        self.expected_result = expected_result
        self.operands = operands


class AssertionsHelper(Generic[MODEL]):
    def __init__(self, configuration: MatcherConfiguration[MODEL]):
        self.conf = configuration

    def is_sym_ref_to(self, symbol_name: str) -> Assertion[SymbolReference]:
        restriction_expectation = is_reference_restrictions__value_type__single(
            self.conf.value_type()
        )

        return asrt_sym_usage.matches_reference__ref(asrt.equals(symbol_name),
                                                     restriction_expectation)

    def is_sym_refs_to(self, symbol_names: List[str]) -> Assertion[Sequence[SymbolReference]]:
        return asrt.matches_sequence([
            self.is_sym_ref_to(operand_symbol_name)
            for operand_symbol_name in symbol_names
        ])

    def sdv_with_validation(self, validation: ValidationActual) -> MatcherSdv[MODEL]:
        validator = ddv_validators.constant(validation)
        return sdv_ddv.sdv_from_bool(
            True,
            (),
            validator,
        )

    def logic_type_symbol_value_context_from_primitive(self,
                                                       primitive: MatcherWTrace[MODEL]
                                                       ) -> MatcherSymbolValueContext[MODEL]:
        return self.conf.mk_logic_type_value_context_of_primitive(primitive)

    def logic_type_symbol_context_from_primitive(self,
                                                 name: str,
                                                 primitive: MatcherWTrace[MODEL]
                                                 ) -> MatcherTypeSymbolContext[MODEL]:
        return self.conf.mk_logic_type_context_of_primitive(name, primitive)

    def execution_cases_for_constant_reference_expressions(
            self, symbol_name: str
    ) -> Sequence[NExArr[PrimAndExeExpectation[MatcherWTrace[MODEL],
                                               MatchingResult],
                         Arrangement]]:
        helper = AssertionsHelper(self.conf)

        mk_trace = get_mk_operand_trace('referred')

        def execution_case_for(result: bool) -> NExArr:
            referenced_matcher = matchers.ConstantMatcherWithCustomTrace(mk_trace, result)
            return NExArr(
                'matcher that gives ' + str(result),
                PrimAndExeExpectation.of_exe(
                    main_result=asrt_matching_result.matches(
                        value=asrt.equals(result),
                        trace=trace_equals(mk_trace(result))
                    )
                ),
                Arrangement(
                    symbols=helper.logic_type_symbol_context_from_primitive(symbol_name,
                                                                            referenced_matcher).symbol_table
                )
            )

        return [
            execution_case_for(result)
            for result in [False, True]
        ]

    def failing_validation_cases(self, symbol_name: str
                                 ) -> Sequence[NExArr[PrimAndExeExpectation[MatcherWTrace[MODEL],
                                                                            MatchingResult],
                                                      Arrangement]]:
        return [
            NExArr(
                validation_case.name,
                expected=PrimAndExeExpectation.of_exe(
                    validation=validation_case.expected,
                ),
                arrangement=Arrangement(
                    symbols=self.conf.mk_logic_type_context_of_sdv(
                        symbol_name,
                        self.sdv_with_validation(validation_case.actual)).symbol_table
                )
            )
            for validation_case in failing_validation_cases()
        ]


class BinaryOperatorValidationCheckHelper(Generic[MODEL]):
    def __init__(self,
                 operator: str,
                 operands: List[str],
                 configuration: MatcherConfiguration[MODEL],
                 ):
        self.operator = operator
        self.operands = operands
        self.helper = AssertionsHelper(configuration)

    def operand_expr_source(self) -> Arguments:
        op = ' ' + self.operator + ' '
        return Arguments(op.join(self.operands))

    def symbol_references_expectation(self) -> Assertion[Sequence[SymbolReference]]:
        return self.helper.is_sym_refs_to(self.operands)

    def failing_validation_cases(self) -> Sequence[NExArr[PrimAndExeExpectation[MatcherWTrace[MODEL],
                                                                                MatchingResult],
                                                          Arrangement]]:
        def cases_for(validation_case: NEA[ValidationAssertions, ValidationActual]
                      ) -> List[NExArr[PrimAndExeExpectation[MatcherWTrace[MODEL],
                                                             MatchingResult],
                                       Arrangement]]:
            validations = [validation_case.actual] + ([ValidationActual.passes()] * (len(self.operands) - 1))
            return [
                NExArr(
                    'validation={}, failing_symbol={}'.format(validation_case.name,
                                                              operand_name_validations[0]),
                    PrimAndExeExpectation.of_exe(
                        validation=validation_case.expected
                    ),
                    Arrangement(
                        symbols=SymbolContext.symbol_table_of_contexts([
                            self.helper.conf.mk_logic_type_context_of_sdv(
                                sym_and_validation[0],
                                self.helper.sdv_with_validation(sym_and_validation[1]))
                            for sym_and_validation in zip(operand_name_validations, validations)
                        ])
                    ),
                )
                for operand_name_validations in itertools.permutations(self.operands)
            ]

        return list(itertools.chain.from_iterable([
            cases_for(validation_case)
            for validation_case in failing_validation_cases()
        ]))


class BinaryOperatorApplicationCheckHelper(Generic[MODEL]):
    def __init__(self,
                 put: unittest.TestCase,
                 operator: str,
                 configuration: MatcherConfiguration[MODEL],
                 ):
        self.put = put
        self.conf = configuration
        self.operator = operator
        self.helper = AssertionsHelper(configuration)

    def check(self,
              cases_with_same_number_of_operands: List[Case],
              ):
        self._assert_cases_list_is_valid(cases_with_same_number_of_operands)

        operand_symbol_names = self._operand_symbol_names(cases_with_same_number_of_operands)

        source = Arguments(self._operator_in_source().join(operand_symbol_names))

        execution_cases = self._execution_cases(
            operand_symbol_names,
            cases_with_same_number_of_operands,
        )

        self.conf.checker_for_parser_of_full_expr().check_multi__w_source_variants(
            self.put,
            source,
            self.helper.is_sym_refs_to(operand_symbol_names),
            self.conf.arbitrary_model,
            execution_cases,
        )

    def _operator_in_source(self) -> str:
        return ' ' + self.operator + ' '

    def _assert_cases_list_is_valid(self,
                                    cases_with_same_number_of_operands: List[Case],
                                    ):
        if not cases_with_same_number_of_operands:
            self.put.fail('Test prerequisite: No cases given')

        num_operands_per_case = [
            len(case.operands)
            for case in cases_with_same_number_of_operands
        ]

        min_num_operands = min(num_operands_per_case)
        if min_num_operands != max(num_operands_per_case):
            self.put.fail('Test prerequisite: Every case must have same number of operands')

        if min_num_operands <= 1:
            self.put.fail('Test prerequisite: There must be at least 2 operands (for a binary operator)')

    @staticmethod
    def _operand_symbol_names(cases_with_same_number_of_operands: List[Case],
                              ) -> List[str]:
        num_operands = len(cases_with_same_number_of_operands[0].operands)

        return [
            '_operand{}_'.format(i)
            for i in range(1, num_operands + 1)
        ]

    def _execution_cases(
            self,
            operand_symbol_names: List[str],
            cases_with_same_number_of_operands: List[Case],
    ) -> Sequence[NExArr[PrimAndExeExpectation[MatcherWTrace[MODEL], MatchingResult],
                         Arrangement]]:
        return [
            self._execution_case(operand_symbol_names, case)
            for case in cases_with_same_number_of_operands
        ]

    def _execution_case(self,
                        operand_symbol_names: List[str],
                        case: Case,
                        ) -> NExArr[PrimAndExeExpectation[MatcherWTrace[MODEL], MatchingResult],
                                    Arrangement]:
        operands = [
            NameAndValue(sym_and_behaviour[0], sym_and_behaviour[1])
            for sym_and_behaviour in zip(operand_symbol_names, case.operands)
        ]

        return NExArr(
            case.name,
            PrimAndExeExpectation.of_exe(
                main_result=asrt_matching_result.matches(
                    value=asrt.equals(case.expected_result),
                    trace=trace_equals(self._expected_trace_for(case.expected_result, operands))
                )
            ),
            Arrangement(
                symbols=self._symbols_for(operands)
            ),
        )

    def _expected_trace_for(self,
                            expected_result: bool,
                            operands: List[NameAndValue[MatcherBehaviour]],
                            ) -> tree.Node[bool]:
        operand_nodes = filter(lambda x: x is not None,
                               [
                                   operand.value.accept(_ApplicationTraceConstructor(operand.name))
                                   for operand in operands
                               ])
        return tree.Node(self.operator,
                         expected_result,
                         (),
                         list(operand_nodes),
                         )

    def _symbols_for(self,
                     operands: List[NameAndValue[MatcherBehaviour]],
                     ) -> SymbolTable:
        return SymbolTable({
            operand.name: self._symbol_definition_for(operand)
            for operand in operands
        })

    def _symbol_definition_for(self, operand: NameAndValue[MatcherBehaviour]) -> SymbolContainer:
        return self.helper.logic_type_symbol_value_context_from_primitive(
            operand.value.accept(_OperandMatcherConstructor(self.put, operand.name))
        ).container


class _ApplicationTraceConstructor(_MatcherBehaviourVisitor[Optional[tree.Node[bool]]]):
    def __init__(self, operand_name: str):
        self._operand_name = operand_name

    def visit_constant(self, x: ConstantIncludedInTrace) -> Optional[tree.Node[bool]]:
        return get_mk_operand_trace(self._operand_name)(x.result)

    def visit_ignored(self, x: IgnoredDueToLaziness) -> Optional[tree.Node[bool]]:
        return None


class _OperandMatcherConstructor(Generic[MODEL], _MatcherBehaviourVisitor[MatcherWTrace[MODEL]]):
    def __init__(self,
                 put: unittest.TestCase,
                 operand_name: str,
                 ):
        self._put = put
        self._operand_name = operand_name

    def visit_constant(self, x: ConstantIncludedInTrace) -> MatcherWTrace[MODEL]:
        return matchers.ConstantMatcherWithCustomTrace(get_mk_operand_trace(self._operand_name),
                                                       x.result)

    def visit_ignored(self, x: IgnoredDueToLaziness) -> MatcherWTrace[MODEL]:
        return _MatcherThatShouldBeIgnoredDueToLaziness(self._put,
                                                        self._operand_name,
                                                        get_mk_operand_trace(self._operand_name))


class _MatcherThatShouldBeIgnoredDueToLaziness(Generic[MODEL], MatcherWTrace[MODEL]):
    def __init__(self,
                 put: unittest.TestCase,
                 name: str,
                 trace_renderer: Callable[[T], tree.Node[T]],
                 ):
        self._put = put
        self._name = name
        self._trace_renderer = trace_renderer

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return renderers.Constant(self._trace_renderer(None))

    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        self._put.fail(self._name + ': This matcher must not be applied, due to laziness')


def trace_equals(expected: Node[bool]) -> Assertion[NodeRenderer[bool]]:
    return asrt_trace_rendering.matches_node_renderer(asrt_d_tree.equals_node(expected))
