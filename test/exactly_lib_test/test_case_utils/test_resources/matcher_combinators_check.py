import unittest

from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.type_system.logic.matcher_base_class import Matcher, MatcherWTrace, MatchingResult
from exactly_lib.type_system.trace.trace import Node
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NEA


class MatcherThatRegistersModelArgument(Matcher):
    def __init__(self, constant_result: bool):
        self._constant_result = constant_result
        self._registered_argument = None

    def register_argument(self, argument):
        self._registered_argument = argument

    @property
    def registered_argument(self):
        return self._registered_argument


class MatcherWTraceThatRegistersModelArgument(MatcherWTrace):
    def __init__(self, constant_result: bool):
        self._constant_result = constant_result
        self._registered_argument = None

    @property
    def option_description(self) -> str:
        return str(type(self)) + ': ' + str(self._constant_result)

    def register_argument(self, argument):
        self._registered_argument = argument

    @property
    def registered_argument(self):
        return self._registered_argument

    def matches_w_trace(self, model) -> MatchingResult:
        return self._new_tb().build_result(self.matches(model))

    def matches(self, model) -> bool:
        self.register_argument(model)
        return self._constant_result


class MatcherConfiguration:
    def matcher_with_constant_result(self, result: bool) -> Matcher:
        raise NotImplementedError('abstract method')

    def irrelevant_model(self):
        raise NotImplementedError('abstract method')

    def matcher_that_registers_model_argument_and_returns_constant(self,
                                                                   result: bool) -> MatcherThatRegistersModelArgument:
        raise NotImplementedError('abstract method')


class TestCaseBase(unittest.TestCase):
    @property
    def configuration(self) -> MatcherConfiguration:
        raise NotImplementedError('abstract method')

    def new_combinator_to_check(self, constructor_argument) -> Matcher:
        """
        Constructs the matcher that is tested ("and", "or", or "not").
        :param constructor_argument: Either a list of matchers (if "and", or "or" is tested),
        or a single matcher (if "not" is tested)
        """
        raise NotImplementedError('abstract method')

    def _check(self,
               case_name: str,
               constructor_argument,
               expected_result: bool):
        # ARRANGE #

        conf = self.configuration
        matcher_to_check = self.new_combinator_to_check(constructor_argument)
        model = conf.irrelevant_model()
        with self.subTest(case_name=case_name,
                          type='old style matcher'):
            # ACT #
            actual_result = matcher_to_check.matches(model)
            # ASSERT #
            self.assertEqual(expected_result,
                             actual_result,
                             'result')
            self.assertIsInstance(matcher_to_check.option_description,
                                  str,
                                  'option_description')

        if isinstance(matcher_to_check, MatcherWTrace):
            with self.subTest(case_name=case_name,
                              type='matcher w trace'):
                # ACT #
                actual_result = matcher_to_check.matches_w_trace(model)
                # ASSERT #
                self.assertIsInstance(actual_result, MatchingResult,
                                      'result object type')
                self.assertEqual(expected_result,
                                 actual_result.value,
                                 'result')
                self.assertIsInstance(matcher_to_check.name,
                                      str,
                                      'name')
                trace = actual_result.trace.render(_ARBITRARY_ERR_MSG_RESOLVING_ENV)

                self.assertIsInstance(trace,
                                      Node,
                                      'type of rendered trace')


class TestAndBase(TestCaseBase):
    def test_empty_list_of_matchers_SHOULD_evaluate_to_True(self):
        self._check('',
                    [],
                    True)

    def test_single_matcher_SHOULD_evaluate_to_value_of_the_single_matcher(self):
        cases = [
            NEA('false',
                False,
                [self.configuration.matcher_with_constant_result(False)],
                ),
            NEA('true',
                True,
                [self.configuration.matcher_with_constant_result(True)]
                ),
        ]
        for case in cases:
            self._check(case.name,
                        case.actual,
                        case.expected)

    def test_more_than_one_matcher_SHOULD_evaluate_to_True_WHEN_all_matchers_evaluate_to_True(self):
        cases = [
            NameAndValue('two matchers',
                         [self.configuration.matcher_with_constant_result(True),
                          self.configuration.matcher_with_constant_result(True)],
                         ),
            NameAndValue('three matchers',
                         [self.configuration.matcher_with_constant_result(True),
                          self.configuration.matcher_with_constant_result(True),
                          self.configuration.matcher_with_constant_result(True)],
                         ),
        ]
        for case in cases:
            anded_matchers = case.value
            self._check(case.name,
                        anded_matchers,
                        True)

    def test_more_than_one_matcher_SHOULD_evaluate_to_False_WHEN_any_matcher_evaluates_to_False(self):
        cases = [
            NameAndValue('two matchers/first is false',
                         [self.configuration.matcher_with_constant_result(False),
                          self.configuration.matcher_with_constant_result(True)],
                         ),
            NameAndValue('two matchers/second is false',
                         [self.configuration.matcher_with_constant_result(True),
                          self.configuration.matcher_with_constant_result(False)],
                         ),
            NameAndValue('three matchers',
                         [self.configuration.matcher_with_constant_result(True),
                          self.configuration.matcher_with_constant_result(False),
                          self.configuration.matcher_with_constant_result(True)],
                         ),
        ]
        for case in cases:
            self._check(case.name,
                        case.value,
                        False)

    def test_model_argument_SHOULD_be_given_as_argument_to_every_sub_matcher(self):
        # ARRANGE #
        conf = self.configuration
        model_that_should_be_registered = conf.irrelevant_model()
        first = conf.matcher_that_registers_model_argument_and_returns_constant(True)
        second = conf.matcher_that_registers_model_argument_and_returns_constant(True)

        matcher_to_check = self.new_combinator_to_check([first, second])

        # ACT #

        matcher_to_check.matches(model_that_should_be_registered)

        # ASSERT #

        self.assertIs(model_that_should_be_registered,
                      first.registered_argument,
                      'first matcher should have received the argument')
        self.assertIs(model_that_should_be_registered,
                      second.registered_argument,
                      'second matcher should have received the argument')


class TestOrBase(TestCaseBase):
    def test_empty_list_of_matchers_SHOULD_evaluate_to_False(self):
        self._check('',
                    [],
                    False)

    def test_single_matcher_SHOULD_evaluate_to_value_of_the_single_matcher(self):
        cases = [
            NameAndValue('false',
                         (
                             [self.configuration.matcher_with_constant_result(False)],
                             False,
                         )),
            NameAndValue('true',
                         (
                             [self.configuration.matcher_with_constant_result(True)],
                             True,
                         )),
        ]
        for case in cases:
            ored_matchers, expected_result = case.value
            self._check(case.name,
                        ored_matchers,
                        expected_result)

    def test_more_than_one_matcher_SHOULD_evaluate_to_True_WHEN_any_matchers_evaluate_to_True(self):
        cases = [
            NameAndValue('two matchers',
                         [self.configuration.matcher_with_constant_result(False),
                          self.configuration.matcher_with_constant_result(True)],
                         ),
            NameAndValue('three matchers',
                         [self.configuration.matcher_with_constant_result(False),
                          self.configuration.matcher_with_constant_result(True),
                          self.configuration.matcher_with_constant_result(False)],
                         ),
        ]
        for case in cases:
            ored_matchers = case.value
            self._check(case.name,
                        ored_matchers,
                        True)

    def test_more_than_one_matcher_SHOULD_evaluate_to_False_WHEN_all_matcher_evaluates_to_False(self):
        cases = [
            NameAndValue('two matchers',
                         [self.configuration.matcher_with_constant_result(False),
                          self.configuration.matcher_with_constant_result(False)],
                         ),
            NameAndValue('three matchers',
                         [self.configuration.matcher_with_constant_result(False),
                          self.configuration.matcher_with_constant_result(False),
                          self.configuration.matcher_with_constant_result(False)],
                         ),
        ]
        for case in cases:
            self._check(case.name,
                        case.value,
                        False)

    def test_model_argument_SHOULD_be_given_as_argument_to_every_sub_matcher(self):
        # ARRANGE #
        conf = self.configuration
        model_that_should_be_registered = conf.irrelevant_model()
        first = conf.matcher_that_registers_model_argument_and_returns_constant(False)
        second = conf.matcher_that_registers_model_argument_and_returns_constant(False)

        matcher_to_check = self.new_combinator_to_check([first, second])

        # ACT #

        matcher_to_check.matches(model_that_should_be_registered)

        # ASSERT #

        self.assertIs(model_that_should_be_registered,
                      first.registered_argument,
                      'first matcher should have received the argument')
        self.assertIs(model_that_should_be_registered,
                      second.registered_argument,
                      'second matcher should have received the argument')


class TestNotBase(TestCaseBase):
    def runTest(self):
        cases = [
            NameAndValue('negate to make negated matcher match',
                         (
                             self.configuration.matcher_with_constant_result(False),
                             True,
                         )),
            NameAndValue('negate to make negated matcher not match',
                         (
                             self.configuration.matcher_with_constant_result(True),
                             False,
                         )),
        ]
        for case in cases:
            matcher_to_negate, expected_result = case.value
            self._check(case.name,
                        matcher_to_negate,
                        expected_result)

    def test_model_argument_SHOULD_be_given_as_argument_to_every_sub_matcher(self):
        # ARRANGE #
        conf = self.configuration
        model_that_should_be_registered = conf.irrelevant_model()
        sub_matcher = conf.matcher_that_registers_model_argument_and_returns_constant(False)

        matcher_to_check = self.new_combinator_to_check(sub_matcher)

        # ACT #

        matcher_to_check.matches(model_that_should_be_registered)

        # ASSERT #

        self.assertIs(model_that_should_be_registered,
                      sub_matcher.registered_argument,
                      'sub_matcher matcher should have received the argument')


_ARBITRARY_ERR_MSG_RESOLVING_ENV = ErrorMessageResolvingEnvironment(
    fake_tcds(),
    None,
)
