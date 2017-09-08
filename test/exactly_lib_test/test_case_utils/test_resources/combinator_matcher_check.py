import unittest

from exactly_lib_test.test_resources.name_and_value import NameAndValue


class MatcherThatRegistersModelArgument:
    def __init__(self, constant_result: bool):
        self._constant_result = constant_result
        self._registered_argument = None

    def matches(self, line: str) -> bool:
        self._registered_argument = line
        return self._constant_result

    def register_argument(self, argument):
        self._registered_argument = argument

    @property
    def registered_argument(self):
        return self._registered_argument


class MatcherConfiguration:
    def constant(self, result: bool):
        raise NotImplementedError('abstract method')

    def irrelevant_model(self):
        raise NotImplementedError('abstract method')

    def apply(self, matcher_to_check, model):
        raise NotImplementedError('abstract method')

    def matcher_that_registers_model_argument_and_returns_constant(self,
                                                                   result: bool) -> MatcherThatRegistersModelArgument:
        raise NotImplementedError('abstract method')


class TestCaseBase(unittest.TestCase):
    @property
    def configuration(self) -> MatcherConfiguration:
        raise NotImplementedError('abstract method')


class TestAndBase(TestCaseBase):
    def mk_and(self, sub_matchers: list):
        raise NotImplementedError('abstract method')

    def _check(self,
               case_name: str,
               sub_matchers: list,
               expected_result: bool):
        # ARRANGE #
        conf = self.configuration
        with self.subTest(case_name=case_name):
            matcher_to_check = self.mk_and(sub_matchers)
            model = conf.irrelevant_model()
            # ACT #
            actual_result = conf.apply(matcher_to_check, model)

            # ASSERT #

            self.assertEqual(expected_result,
                             actual_result,
                             'result')

    def test_empty_list_of_matchers_SHOULD_evaluate_to_True(self):
        self._check('',
                    [],
                    True)

    def test_single_matcher_SHOULD_evaluate_to_value_of_the_single_matcher(self):
        cases = [
            NameAndValue('false',
                         (
                             [self.configuration.constant(False)],
                             False,
                         )),
            NameAndValue('true',
                         (
                             [self.configuration.constant(True)],
                             True,
                         )),
        ]
        for case in cases:
            anded_matchers, expected_result = case.value
            self._check(case.name,
                        anded_matchers,
                        expected_result)

    def test_more_than_one_matcher_SHOULD_evaluate_to_True_WHEN_all_matchers_evaluate_to_True(self):
        cases = [
            NameAndValue('two matchers',
                         [self.configuration.constant(True),
                          self.configuration.constant(True)],
                         ),
            NameAndValue('three matchers',
                         [self.configuration.constant(True),
                          self.configuration.constant(True),
                          self.configuration.constant(True)],
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
                         [self.configuration.constant(False),
                          self.configuration.constant(True)],
                         ),
            NameAndValue('two matchers/second is false',
                         [self.configuration.constant(True),
                          self.configuration.constant(False)],
                         ),
            NameAndValue('three matchers',
                         [self.configuration.constant(True),
                          self.configuration.constant(False),
                          self.configuration.constant(True)],
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
        matcher_to_check = self.mk_and([first, second])
        # ACT #
        conf.apply(matcher_to_check, model_that_should_be_registered)
        # ASSERT #
        self.assertIs(model_that_should_be_registered,
                      first.registered_argument,
                      'first matcher should have received the argument')
        self.assertIs(model_that_should_be_registered,
                      second.registered_argument,
                      'second matcher should have received the argument')
