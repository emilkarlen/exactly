import unittest
from abc import ABC
from typing import List, Tuple

from exactly_lib.definitions import expression
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.util.description_tree.tree import Node
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.type_system.trace.test_resources import trace_rendering_assertions as asrt_trace_rendering
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class MatcherConfiguration:
    def matcher_with_constant_result(self,
                                     name: str,
                                     result: bool) -> MatcherWTrace:
        """
        :param name: The name of the matcher in the trace
        :param result: Constant result
        """
        raise NotImplementedError('abstract method')

    def irrelevant_model(self):
        raise NotImplementedError('abstract method')

    def matcher_that_registers_model_argument_and_returns_constant(self,
                                                                   registry: List,
                                                                   result: bool) -> MatcherWTrace:
        raise NotImplementedError('abstract method')


MatcherNameAndResult = Tuple[str, bool]


class Case:
    def __init__(self,
                 name: str,
                 expected_result: bool,
                 constructor_argument,
                 expected_trace: ValueAssertion[Node[bool]]
                 ):
        self.name = name
        self.expected_result = expected_result
        self.constructor_argument = constructor_argument
        self.expected_trace = expected_trace


class TestCaseBase(unittest.TestCase):
    @property
    def configuration(self) -> MatcherConfiguration:
        raise NotImplementedError('abstract method')

    @property
    def trace_operator_name(self) -> str:
        raise NotImplementedError('abstract method')

    def new_combinator_to_check(self, constructor_argument) -> MatcherWTrace:
        """
        Constructs the matcher that is tested ("and", "or", or "not").
        :param constructor_argument: Either a list of matchers (if "and", or "or" is tested),
        or a single matcher (if "not" is tested)
        """
        raise NotImplementedError('abstract method')

    def _check(self,
               case_name: str,
               constructor_argument,
               expected_result: bool,
               expected_trace: ValueAssertion[Node[bool]] = asrt.anything_goes()):
        # ARRANGE #

        conf = self.configuration
        matcher_to_check = self.new_combinator_to_check(constructor_argument)
        model = conf.irrelevant_model()

        expectation = asrt_matching_result.matches(
            asrt.equals(expected_result),
            trace=asrt_trace_rendering.matches_node_renderer(
                expected_trace
            )
        )
        # ACT #
        actual_result = matcher_to_check.matches_w_trace(model)
        # ASSERT #
        expectation.apply_without_message(self,
                                          actual_result)

    def _check_model_argument_SHOULD_be_given_as_argument_to_both_matcher(self,
                                                                          result_of_1st: bool,
                                                                          result_of_2nd: bool):
        # ARRANGE #
        conf = self.configuration
        model_that_should_be_registered = conf.irrelevant_model()
        first__registry = []
        first = conf.matcher_that_registers_model_argument_and_returns_constant(first__registry, result_of_1st)
        second__registry = []
        second = conf.matcher_that_registers_model_argument_and_returns_constant(second__registry, result_of_2nd)

        matcher_to_check = self.new_combinator_to_check([first, second])

        # ACT #

        matcher_to_check.matches_w_trace(model_that_should_be_registered)

        # ASSERT #

        expected_registered_models = asrt.matches_sequence([asrt.is_(model_that_should_be_registered)])

        expected_registered_models.apply_with_message(self, first__registry,
                                                      'first matcher should have received the argument')

        expected_registered_models.apply_with_message(self, second__registry,
                                                      'second matcher should have received the argument')

    def _check_evaluation_SHOULD_be_lazy_so_that_only_first_operand_is_applied(self,
                                                                               result_of_1st: bool,
                                                                               result_of_2nd: bool):
        # ARRANGE #
        conf = self.configuration
        model_that_should_be_registered = conf.irrelevant_model()
        first__registry = []
        first = conf.matcher_that_registers_model_argument_and_returns_constant(first__registry, result_of_1st)
        second__registry = []
        second = conf.matcher_that_registers_model_argument_and_returns_constant(second__registry, result_of_2nd)

        matcher_to_check = self.new_combinator_to_check([first, second])

        # ACT #

        matcher_to_check.matches_w_trace(model_that_should_be_registered)

        # ASSERT #

        expected_registered_models_of_applied_operand = asrt.matches_sequence(
            [asrt.is_(model_that_should_be_registered)])
        expected_registered_models_of_non_applied_operand = asrt.is_empty_sequence

        expected_registered_models_of_applied_operand.apply_with_message(
            self,
            first__registry,
            'first matcher should have received the argument',
        )

        expected_registered_models_of_non_applied_operand.apply_with_message(
            self,
            second__registry,
            'second matcher should not have been invoked',
        )

    def _check_case(self, case: Case):
        self._check(case.name,
                    case.constructor_argument,
                    case.expected_result,
                    case.expected_trace)

    def _multi_case(self,
                    name: str,
                    expected_result: bool,
                    child_matchers: List[MatcherNameAndResult],
                    trace_child_nodes: List[MatcherNameAndResult],
                    ) -> Case:
        return Case(name,
                    expected_result,
                    [self.configuration.matcher_with_constant_result(child_name,
                                                                     child_result)
                     for child_name, child_result in child_matchers
                     ],
                    self._trace(expected_result, trace_child_nodes)
                    )

    def _single_case(self,
                     name: str,
                     expected_result: bool,
                     child_matcher: MatcherNameAndResult,
                     trace_child_node: MatcherNameAndResult,
                     ) -> Case:
        return Case(name,
                    expected_result,
                    self.configuration.matcher_with_constant_result(child_matcher[0],
                                                                    child_matcher[1]),
                    self._trace(expected_result, [trace_child_node])
                    )

    def _trace(self,
               expected_result: bool,
               child_nodes: List[MatcherNameAndResult],
               ) -> ValueAssertion[Node[bool]]:
        return asrt_d_tree.matches_node(
            header=asrt.equals(self.trace_operator_name),
            data=asrt.equals(expected_result),
            details=asrt.anything_goes(),
            children=asrt.matches_sequence([
                asrt_d_tree.matches_node(
                    header=asrt.equals(child_name),
                    data=asrt.equals(child_result),
                    details=asrt.anything_goes(),
                    children=asrt.is_empty_sequence,
                )
                for child_name, child_result in child_nodes
            ])
        )


class TestAndBase(TestCaseBase, ABC):
    @property
    def trace_operator_name(self) -> str:
        return expression.AND_OPERATOR_NAME

    def test_empty_list_of_matchers_SHOULD_evaluate_to_True(self):
        self._check_case(
            self._multi_case('empty',
                             True,
                             child_matchers=[],
                             trace_child_nodes=[]))

    def test_single_matcher_SHOULD_evaluate_to_value_of_the_single_matcher(self):
        cases = [
            self._multi_case('false',
                             False,
                             child_matchers=child_1_to_n([False]),
                             trace_child_nodes=child_1_to_n([False]),
                             ),
            self._multi_case('true',
                             True,
                             child_matchers=child_1_to_n([True]),
                             trace_child_nodes=child_1_to_n([True]),
                             ),
        ]
        for case in cases:
            self._check_case(case)

    def test_more_than_one_matcher_SHOULD_evaluate_to_True_WHEN_all_matchers_evaluate_to_True(self):
        cases = [
            self._multi_case('two matchers',
                             True,
                             child_matchers=child_1_to_n([True, True]),
                             trace_child_nodes=child_1_to_n([True, True]),
                             ),
            self._multi_case('three matchers',
                             True,
                             child_matchers=child_1_to_n([True, True, True]),
                             trace_child_nodes=child_1_to_n([True, True, True]),
                             ),
        ]
        for case in cases:
            self._check_case(case)

    def test_more_than_one_matcher_SHOULD_evaluate_to_False_WHEN_any_matcher_evaluates_to_False(self):
        cases = [
            self._multi_case('two matchers/first is false',
                             False,
                             child_matchers=child_1_to_n([False, True]),
                             trace_child_nodes=child_1_to_n([False]),
                             ),
            self._multi_case('two matchers/second is false',
                             False,
                             child_matchers=child_1_to_n([True, False]),
                             trace_child_nodes=child_1_to_n([True, False]),
                             ),
            self._multi_case('three matchers',
                             False,
                             child_matchers=child_1_to_n([True, False, True]),
                             trace_child_nodes=child_1_to_n([True, False]),
                             ),
        ]
        for case in cases:
            self._check_case(case)

    def test_model_argument_SHOULD_be_given_as_argument_to_every_operand(self):
        self._check_model_argument_SHOULD_be_given_as_argument_to_both_matcher(True, True)

    def test_evaluation_SHOULD_be_lazy(self):
        self._check_evaluation_SHOULD_be_lazy_so_that_only_first_operand_is_applied(False, True)


class TestOrBase(TestCaseBase, ABC):
    @property
    def trace_operator_name(self) -> str:
        return expression.OR_OPERATOR_NAME

    def test_empty_list_of_matchers_SHOULD_evaluate_to_False(self):
        self._check_case(
            self._multi_case(
                'empty',
                False,
                child_matchers=[],
                trace_child_nodes=[])
        )

    def test_single_matcher_SHOULD_evaluate_to_value_of_the_single_matcher(self):
        cases = [
            self._multi_case('false',
                             False,
                             child_matchers=child_1_to_n([False]),
                             trace_child_nodes=child_1_to_n([False]),
                             ),
            self._multi_case('true',
                             True,
                             child_matchers=child_1_to_n([True]),
                             trace_child_nodes=child_1_to_n([True]),
                             ),
        ]
        for case in cases:
            self._check_case(case)

    def test_more_than_one_matcher_SHOULD_evaluate_to_True_WHEN_any_matchers_evaluate_to_True(self):
        cases = [
            self._multi_case('two matchers',
                             True,
                             child_matchers=child_1_to_n([False, True]),
                             trace_child_nodes=child_1_to_n([False, True]),
                             ),
            self._multi_case('three matchers',
                             True,
                             child_matchers=child_1_to_n([False, True, False]),
                             trace_child_nodes=child_1_to_n([False, True]),
                             ),
        ]
        for case in cases:
            self._check_case(case)

    def test_more_than_one_matcher_SHOULD_evaluate_to_False_WHEN_all_matcher_evaluates_to_False(self):
        cases = [
            self._multi_case('two matchers',
                             False,
                             child_matchers=child_1_to_n([False, False]),
                             trace_child_nodes=child_1_to_n([False, False]),
                             ),
            self._multi_case('three matchers',
                             False,
                             child_matchers=child_1_to_n([False, False, False]),
                             trace_child_nodes=child_1_to_n([False, False, False]),
                             ),
        ]
        for case in cases:
            self._check_case(case)

    def test_model_argument_SHOULD_be_given_as_argument_to_every_operand(self):
        self._check_model_argument_SHOULD_be_given_as_argument_to_both_matcher(False, False)

    def test_evaluation_SHOULD_be_lazy(self):
        self._check_evaluation_SHOULD_be_lazy_so_that_only_first_operand_is_applied(True, False)


class TestNotBase(TestCaseBase):
    @property
    def trace_operator_name(self) -> str:
        return expression.NOT_OPERATOR_NAME

    def test_result_SHOULD_be_negation_of_child_matcher(self):
        cases = [
            self._single_case('child gives false',
                              True,
                              child_matcher=('child_false', False),
                              trace_child_node=('child_false', False),
                              ),
            self._single_case('child gives true',
                              False,
                              child_matcher=('child_true', True),
                              trace_child_node=('child_true', True),
                              ),
        ]
        for case in cases:
            self._check_case(case)

    def test_model_argument_SHOULD_be_given_as_argument_to_every_operand(self):
        # ARRANGE #
        conf = self.configuration
        model_that_should_be_registered = conf.irrelevant_model()
        operand_model_registry = []
        sub_matcher = conf.matcher_that_registers_model_argument_and_returns_constant(operand_model_registry, False)

        matcher_to_check = self.new_combinator_to_check(sub_matcher)

        # ACT #

        matcher_to_check.matches_w_trace(model_that_should_be_registered)

        # ASSERT #
        expected_registered_models = asrt.matches_sequence([asrt.is_(model_that_should_be_registered)])

        expected_registered_models.apply_with_message(self, operand_model_registry,
                                                      'operand matcher should have received the argument')


def child_1_to_n(child_results: List[bool]) -> List[MatcherNameAndResult]:
    """Gives unique names to children: child1, child2, ..."""
    return [
        ('child' + str(n),
         result)
        for n, result in enumerate(child_results, start=1)
    ]
