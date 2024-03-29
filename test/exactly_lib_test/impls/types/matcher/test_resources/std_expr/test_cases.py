import unittest
from abc import ABC, abstractmethod
from typing import List, Generic, Sequence

from exactly_lib.definitions import logic
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.description_tree import tree
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.expression.test_resources.syntax_cases import TestCaseGeneratorForParentheses
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_wo_tcds, \
    ParseExpectation, ExecutionExpectation, PrimAndExeExpectation, Expectation
from exactly_lib_test.impls.types.logic.test_resources.symbol_ref_syntax import symbol_ref_syntax_cases
from exactly_lib_test.impls.types.matcher.test_resources import matchers
from exactly_lib_test.impls.types.matcher.test_resources.std_expr import _utils
from exactly_lib_test.impls.types.matcher.test_resources.std_expr._utils import AssertionsHelper, \
    trace_equals, ConstantIncludedInTrace, IgnoredDueToLaziness, \
    Case, BinaryOperatorApplicationCheckHelper, get_mk_operand_trace, BinaryOperatorValidationCheckHelper
from exactly_lib_test.impls.types.matcher.test_resources.std_expr.configuration import MODEL, \
    MatcherConfiguration
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


class _TestCaseBase(Generic[MODEL], unittest.TestCase, ABC):
    @property
    @abstractmethod
    def configuration(self) -> MatcherConfiguration[MODEL]:
        raise NotImplementedError('abstract method')

    @property
    def _asrt_helper(self) -> AssertionsHelper[MODEL]:
        return AssertionsHelper(self.configuration)


class TestParenthesesBase(Generic[MODEL], _TestCaseBase[MODEL], ABC):
    def test_parse_SHOULD_fail_WHEN_syntax_is_invalid(self):
        # ARRANGE #
        conf = self.configuration
        case_generator = TestCaseGeneratorForParentheses(
            conf.valid_symbol_name_and_not_valid_primitive_or_operator(),
            conf.not_a_valid_symbol_name_nor_valid_primitive_or_operator(),
        )
        for case in case_generator.parse_should_fail_when_syntax_is_invalid():
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    conf.parsers_for_expr_on_any_line().full.parse(case.value)

    def test_expression_inside_parentheses_SHOULD_be_validated(self):
        # ARRANGE #

        conf = self.configuration
        helper = self._asrt_helper

        symbol_name = conf.valid_symbol_name_and_not_valid_primitive_or_operator()

        # ACT & ASSERT #

        conf.checker_for_parser_of_full_expr().check_multi__w_source_variants(
            self,
            arguments=ArgumentElements(['(', symbol_name, ')']).as_arguments,
            symbol_references=asrt.matches_singleton_sequence(helper.is_sym_ref_to(symbol_name)),
            input_=conf.arbitrary_model,
            execution=helper.failing_validation_cases(symbol_name),
        )

    def test_expression_inside_parentheses_SHOULD_be_equal_to_expression_inside_parentheses(self):
        # ARRANGE #

        conf = self.configuration
        helper = self._asrt_helper

        symbol_name = conf.valid_symbol_name_and_not_valid_primitive_or_operator()

        source_cases = [
            NameAndValue(
                'expression on single line',
                ArgumentElements(['(', symbol_name, ')'])
            ),
            NameAndValue(
                'expression on multiple lines',
                ArgumentElements(
                    first_line=['('],
                    following_lines=[
                        [symbol_name],
                        [')'],
                    ])
            ),
        ]

        # ACT & ASSERT #

        for source_case in source_cases:
            with self.subTest(source_case.name):
                conf.checker_for_parser_of_full_expr().check_multi__w_source_variants(
                    self,
                    arguments=source_case.value.as_arguments,
                    symbol_references=asrt.matches_singleton_sequence(helper.is_sym_ref_to(symbol_name)),
                    input_=conf.arbitrary_model,
                    execution=helper.execution_cases_for_constant_reference_expressions(symbol_name),
                )


class TestConstantBase(Generic[MODEL], _TestCaseBase[MODEL], ABC):
    def test_parse_SHOULD_fail_WHEN_operand_is_missing(self):
        source = remaining_source(logic.CONSTANT_MATCHER)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.parsers_for_expr_on_any_line().full.parse(source)

    def test_application(self):
        conf = self.configuration
        for value in [False, True]:
            conf.checker_for_parser_of_full_expr().check__w_source_variants(
                self,
                arguments=matcher_argument.Constant(value).as_arguments,
                input_=conf.arbitrary_model,
                arrangement=arrangement_wo_tcds(),
                expectation=Expectation(
                    execution=ExecutionExpectation(
                        main_result=asrt_matching_result.matches(
                            asrt.equals(value),
                            trace=_utils.trace_equals(
                                tree.Node.leaf(
                                    logic.CONSTANT_MATCHER,
                                    value,
                                    (tree.StringDetail(logic.BOOLEANS[value]),)
                                )
                            )
                        )
                    )
                )
            )


class TestSymbolReferenceBase(Generic[MODEL], _TestCaseBase[MODEL], ABC):
    def test_parse_SHOULD_fail_WHEN_initial_token_is_neither_valid_sym_ref_nor_primitive(self):
        source = remaining_source(self.configuration.not_a_valid_symbol_name_nor_valid_primitive_or_operator())
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.parsers_for_expr_on_any_line().full.parse(source)

    def test_referenced_symbol_SHOULD_be_validated(self):
        # ARRANGE #

        conf = self.configuration
        helper = self._asrt_helper

        symbol_name = conf.valid_symbol_name_and_not_valid_primitive_or_operator()

        # ACT & ASSERT #

        for symbol_ref_syntax in symbol_ref_syntax_cases(symbol_name):
            with self.subTest(symbol_ref_syntax=symbol_ref_syntax.name):
                conf.checker_for_parser_of_full_expr().check_multi__w_source_variants(
                    self,
                    arguments=Arguments(symbol_ref_syntax.value),
                    symbol_references=asrt.matches_singleton_sequence(helper.is_sym_ref_to(symbol_name)),
                    input_=conf.arbitrary_model,
                    execution=helper.failing_validation_cases(symbol_name),
                )

    def test_reference_SHOULD_apply_referenced_matcher(self):
        # ARRANGE #

        conf = self.configuration
        helper = self._asrt_helper

        symbol_name = conf.valid_symbol_name_and_not_valid_primitive_or_operator()

        # ACT & ASSERT #

        for symbol_ref_syntax in symbol_ref_syntax_cases(symbol_name):
            with self.subTest(symbol_ref_syntax=symbol_ref_syntax.name):
                conf.checker_for_parser_of_full_expr().check_multi__w_source_variants(
                    self,
                    arguments=Arguments(symbol_ref_syntax.value),
                    symbol_references=asrt.matches_singleton_sequence(helper.is_sym_ref_to(symbol_name)),
                    input_=conf.arbitrary_model,
                    execution=helper.execution_cases_for_constant_reference_expressions(symbol_name),
                )


class TestNegationBase(Generic[MODEL], _TestCaseBase[MODEL], ABC):
    def test_parse_SHOULD_fail_WHEN_operand_is_missing(self):
        source = remaining_source(logic.NOT_OPERATOR_NAME)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.parsers_for_expr_on_any_line().full.parse(source)

    def test_validation_SHOULD_fail_WHEN_validation_of_negated_expr_fails(self):
        # ARRANGE #

        conf = self.configuration
        helper = self._asrt_helper

        symbol_name = conf.valid_symbol_name_and_not_valid_primitive_or_operator()

        # ACT & ASSERT #

        conf.checker_for_parser_of_full_expr().check_multi__w_source_variants(
            self,
            arguments=ArgumentElements([logic.NOT_OPERATOR_NAME, symbol_name]).as_arguments,
            symbol_references=asrt.matches_singleton_sequence(helper.is_sym_ref_to(symbol_name)),
            input_=conf.arbitrary_model,
            execution=helper.failing_validation_cases(symbol_name),
        )

    def test_result_of_execution_SHOULD_be_negation_of_negated_expr(self):
        # ARRANGE #
        conf = self.configuration
        helper = self._asrt_helper
        symbol_name = conf.valid_symbol_name_and_not_valid_primitive_or_operator()

        mk_operand_trace = get_mk_operand_trace('the_operand')

        def execution_case_for(operand_result: bool) -> NExArr[PrimAndExeExpectation[MatcherWTrace[MODEL],
                                                                                     MatchingResult],
                                                               Arrangement]:
            operand_matcher = helper.logic_type_symbol_context_from_primitive(
                symbol_name,
                matchers.ConstantMatcherWithCustomTrace(mk_operand_trace, operand_result)
            )
            trace = tree.Node(logic.NOT_OPERATOR_NAME,
                              not operand_result,
                              (),
                              [mk_operand_trace(operand_result)]
                              )
            return NExArr(
                'operand that gives ' + str(operand_result),
                PrimAndExeExpectation.of_exe(
                    main_result=asrt_matching_result.matches(
                        value=asrt.equals(not operand_result),
                        trace=trace_equals(trace)
                    )
                ),
                Arrangement(
                    symbols=operand_matcher.symbol_table
                )
            )

        execution_cases = [
            execution_case_for(operand_result)
            for operand_result in [False, True]
        ]

        source_cases = [
            NameAndValue(
                'operand on same line',
                ArgumentElements(
                    [logic.NOT_OPERATOR_NAME, symbol_name],
                )
            ),
            NameAndValue(
                'operand on following line',
                ArgumentElements(
                    [logic.NOT_OPERATOR_NAME],
                    [
                        [symbol_name],
                    ])
            ),
        ]

        # ACT & ASSERT #

        for source_case in source_cases:
            with self.subTest(source_case.name):
                conf.checker_for_parser_of_full_expr().check_multi__w_source_variants(
                    self,
                    arguments=source_case.value.as_arguments,
                    symbol_references=asrt.matches_singleton_sequence(helper.is_sym_ref_to(symbol_name)),
                    input_=conf.arbitrary_model,
                    execution=execution_cases,
                )


class _TestBinaryOperatorBase(Generic[MODEL], _TestCaseBase[MODEL], ABC):
    @property
    @abstractmethod
    def operator_name(self) -> str:
        raise NotImplementedError('abstract method')

    def _check_bin_op(self,
                      cases_with_same_number_of_operands: List[Case],
                      ):
        checker = BinaryOperatorApplicationCheckHelper(self,
                                                       self.operator_name,
                                                       self.configuration)

        checker.check(cases_with_same_number_of_operands)

    def test_parse_SHOULD_fail_WHEN_operand_is_missing(self):
        arguments = ArgumentElements([self.configuration.valid_symbol_name_and_not_valid_primitive_or_operator(),
                                      self.operator_name])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.parsers_for_expr_on_any_line().full.parse(arguments.as_remaining_source)

    def test_validation_SHOULD_fail_WHEN_validation_of_any_of_2_operands_fails(self):
        helper = BinaryOperatorValidationCheckHelper(self.operator_name,
                                                     ['_op1_', '_op2_'],
                                                     self.configuration)

        self.configuration.checker_for_parser_of_full_expr().check_multi__w_source_variants(
            self,
            helper.operand_expr_source(),
            symbol_references=helper.symbol_references_expectation(),
            input_=self.configuration.arbitrary_model,
            execution=helper.failing_validation_cases()
        )

    def test_validation_SHOULD_fail_WHEN_validation_of_any_of_3_operands_fails(self):
        helper = BinaryOperatorValidationCheckHelper(self.operator_name,
                                                     ['_op1_', '_op2_', '_op3_'],
                                                     self.configuration)

        self.configuration.checker_for_parser_of_full_expr().check_multi__w_source_variants(
            self,
            helper.operand_expr_source(),
            symbol_references=helper.symbol_references_expectation(),
            input_=self.configuration.arbitrary_model,
            execution=helper.failing_validation_cases()
        )


class TestConjunctionBase(_TestBinaryOperatorBase[MODEL], ABC):
    @property
    def operator_name(self) -> str:
        return logic.AND_OPERATOR_NAME

    def test_application_of_2_operands(self):
        # ARRANGE #
        cases = [
            Case(
                'F & ?',
                expected_result=False,
                operands=[
                    ConstantIncludedInTrace(False),
                    IgnoredDueToLaziness(),
                ]
            ),
            Case(
                'T & F',
                expected_result=False,
                operands=[
                    ConstantIncludedInTrace(True),
                    ConstantIncludedInTrace(False),
                ]
            ),
            Case(
                'T & T',
                expected_result=True,
                operands=[
                    ConstantIncludedInTrace(True),
                    ConstantIncludedInTrace(True),
                ]
            ),
        ]
        # ACT & ASSERT #
        self._check_bin_op(cases)

    def test_application_of_3_operands(self):
        # ARRANGE #
        cases = [
            Case(
                'F & ? & ?',
                expected_result=False,
                operands=[
                    ConstantIncludedInTrace(False),
                    IgnoredDueToLaziness(),
                    IgnoredDueToLaziness(),
                ]
            ),
            Case(
                'T & F & ?',
                expected_result=False,
                operands=[
                    ConstantIncludedInTrace(True),
                    ConstantIncludedInTrace(False),
                    IgnoredDueToLaziness(),
                ]
            ),
            Case(
                'T & T & F',
                expected_result=False,
                operands=[
                    ConstantIncludedInTrace(True),
                    ConstantIncludedInTrace(True),
                    ConstantIncludedInTrace(False),
                ]
            ),
            Case(
                'T & T & T',
                expected_result=True,
                operands=[
                    ConstantIncludedInTrace(True),
                    ConstantIncludedInTrace(True),
                    ConstantIncludedInTrace(True),
                ]
            ),
        ]
        # ACT & ASSERT #
        self._check_bin_op(cases)


class TestDisjunctionBase(_TestBinaryOperatorBase[MODEL], ABC):
    @property
    def operator_name(self) -> str:
        return logic.OR_OPERATOR_NAME

    def test_application_of_2_operands(self):
        # ARRANGE #
        cases = [
            Case(
                'F | F',
                expected_result=False,
                operands=[
                    ConstantIncludedInTrace(False),
                    ConstantIncludedInTrace(False),
                ]
            ),
            Case(
                'F & T',
                expected_result=True,
                operands=[
                    ConstantIncludedInTrace(False),
                    ConstantIncludedInTrace(True),
                ]
            ),
            Case(
                'T | ?',
                expected_result=True,
                operands=[
                    ConstantIncludedInTrace(True),
                    IgnoredDueToLaziness(),
                ]
            ),
        ]
        # ACT & ASSERT #
        self._check_bin_op(cases)

    def test_application_of_3_operands(self):
        # ARRANGE #
        cases = [
            Case(
                'F | F | F',
                expected_result=False,
                operands=[
                    ConstantIncludedInTrace(False),
                    ConstantIncludedInTrace(False),
                    ConstantIncludedInTrace(False),
                ]
            ),
            Case(
                'F | F | T',
                expected_result=True,
                operands=[
                    ConstantIncludedInTrace(False),
                    ConstantIncludedInTrace(False),
                    ConstantIncludedInTrace(True),
                ]
            ),
            Case(
                'F | T | ?',
                expected_result=True,
                operands=[
                    ConstantIncludedInTrace(False),
                    ConstantIncludedInTrace(True),
                    IgnoredDueToLaziness(),
                ]
            ),
            Case(
                'T | ? | ?',
                expected_result=True,
                operands=[
                    ConstantIncludedInTrace(True),
                    IgnoredDueToLaziness(),
                    IgnoredDueToLaziness(),
                ]
            ),
        ]
        # ACT & ASSERT #
        self._check_bin_op(cases)


class TestPrecedence(Generic[MODEL], _TestCaseBase[MODEL], ABC):
    def test_conjunction_followed_by_disjunction(self):
        # ARRANGEMENT #

        sym_a = NameAndValue('_a_', matchers.ConstantMatcherWithCustomName('a', True))
        sym_b = NameAndValue('_b_', matchers.ConstantMatcherWithCustomName('b', False))
        sym_c = NameAndValue('_c_', matchers.ConstantMatcherWithCustomName('c', True))

        all_symbols = [sym_a, sym_b, sym_c]

        arguments = ArgumentElements([
            sym_a.name,
            logic.AND_OPERATOR_NAME,
            sym_b.name,
            logic.OR_OPERATOR_NAME,
            sym_c.name,
        ])

        expected_trace = tree.Node(
            logic.OR_OPERATOR_NAME, True, (),
            [
                tree.Node(
                    logic.AND_OPERATOR_NAME, False, (),
                    [
                        sym_a.value.trace_tree,
                        sym_b.value.trace_tree,
                    ]),
                sym_c.value.trace_tree,
            ]
        )

        # ACT & ASSERT #

        self._check(
            arguments,
            True,
            all_symbols,
            expected_trace,
        )

    def test_conjunction_followed_by_disjunction__with_negation(self):
        # ARRANGEMENT #

        sym_a = NameAndValue('_a_', matchers.ConstantMatcherWithCustomName('a', False))
        sym_b = NameAndValue('_b_', matchers.ConstantMatcherWithCustomName('b', True))
        sym_c = NameAndValue('_c_', matchers.ConstantMatcherWithCustomName('c', False))

        all_symbols = [sym_a, sym_b, sym_c]

        arguments = ArgumentElements([
            logic.NOT_OPERATOR_NAME,
            sym_a.name,
            logic.AND_OPERATOR_NAME,
            logic.NOT_OPERATOR_NAME,
            sym_b.name,
            logic.OR_OPERATOR_NAME,
            logic.NOT_OPERATOR_NAME,
            sym_c.name,
        ])

        expected_trace = tree.Node(
            logic.OR_OPERATOR_NAME, True, (),
            [
                tree.Node(
                    logic.AND_OPERATOR_NAME, False, (),
                    [
                        tree.Node(logic.NOT_OPERATOR_NAME, True, (), [sym_a.value.trace_tree]),
                        tree.Node(logic.NOT_OPERATOR_NAME, False, (), [sym_b.value.trace_tree]),
                    ]),
                tree.Node(logic.NOT_OPERATOR_NAME, True, (), [sym_c.value.trace_tree]),
            ]
        )

        # ACT & ASSERT #

        self._check(
            arguments,
            True,
            all_symbols,
            expected_trace,
        )

    def test_disjunction_followed_by_conjunction(self):
        # ARRANGEMENT #

        sym_a = NameAndValue('_a_', matchers.ConstantMatcherWithCustomName('a', False))
        sym_b = NameAndValue('_b_', matchers.ConstantMatcherWithCustomName('b', True))
        sym_c = NameAndValue('_c_', matchers.ConstantMatcherWithCustomName('c', False))

        all_symbols = [sym_a, sym_b, sym_c]

        arguments = ArgumentElements([
            sym_a.name,
            logic.OR_OPERATOR_NAME,
            sym_b.name,
            logic.AND_OPERATOR_NAME,
            sym_c.name,
        ])

        expected_trace = tree.Node(
            logic.OR_OPERATOR_NAME, False, (),
            [
                sym_a.value.trace_tree,
                tree.Node(
                    logic.AND_OPERATOR_NAME, False, (),
                    [
                        sym_b.value.trace_tree,
                        sym_c.value.trace_tree,
                    ]),
            ]
        )

        # ACT & ASSERT #

        self._check(
            arguments,
            False,
            all_symbols,
            expected_trace,
        )

    def test_disjunction_followed_by_conjunction__with_negation(self):
        # ARRANGEMENT #

        sym_a = NameAndValue('_a_', matchers.ConstantMatcherWithCustomName('a', True))
        sym_b = NameAndValue('_b_', matchers.ConstantMatcherWithCustomName('b', False))
        sym_c = NameAndValue('_c_', matchers.ConstantMatcherWithCustomName('c', True))

        all_symbols = [sym_a, sym_b, sym_c]

        arguments = ArgumentElements([
            logic.NOT_OPERATOR_NAME, sym_a.name,
            logic.OR_OPERATOR_NAME,
            logic.NOT_OPERATOR_NAME, sym_b.name,
            logic.AND_OPERATOR_NAME,
            logic.NOT_OPERATOR_NAME, sym_c.name,
        ])

        expected_trace = tree.Node(
            logic.OR_OPERATOR_NAME, False, (),
            [
                tree.Node(logic.NOT_OPERATOR_NAME, False, (), [sym_a.value.trace_tree]),
                tree.Node(
                    logic.AND_OPERATOR_NAME, False, (),
                    [
                        tree.Node(logic.NOT_OPERATOR_NAME, True, (), [sym_b.value.trace_tree]),
                        tree.Node(logic.NOT_OPERATOR_NAME, False, (), [sym_c.value.trace_tree]),
                    ]),
            ]
        )

        # ACT & ASSERT #

        self._check(
            arguments,
            False,
            all_symbols,
            expected_trace,
        )

    def _check(self,
               arguments: ArgumentElements,
               expected_result: bool,
               all_symbols: Sequence[NameAndValue[MatcherWTrace[MODEL]]],
               expected_trace: tree.Node[bool],
               ):
        conf = self.configuration
        helper = self._asrt_helper

        conf.checker_for_parser_of_full_expr().check__w_source_variants(
            self,
            arguments.as_arguments,
            conf.arbitrary_model,
            Arrangement(
                symbols=SymbolContext.symbol_table_of_contexts([
                    conf.mk_logic_type_context_of_primitive(sym.name, sym.value)
                    for sym in all_symbols
                ]),
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=helper.is_sym_refs_to([sym.name for sym in all_symbols]),
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches(
                        value=asrt.equals(expected_result),
                        trace=trace_equals(expected_trace)
                    )
                )
            ),
        )
