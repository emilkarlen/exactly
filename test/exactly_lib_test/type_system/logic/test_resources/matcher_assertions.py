import types
import unittest

from exactly_lib.type_system.logic.matcher_base_class import Matcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class ModelInfo:
    def __init__(self,
                 model,
                 mk_description_of_model: types.FunctionType = str):
        self.model = model
        self._mk_description_of_model = mk_description_of_model

    @property
    def description_of_model(self) -> str:
        return self._mk_description_of_model(self.model)


def is_equivalent_to(expected_equivalent: Matcher,
                     model_infos: list) -> asrt.ValueAssertion:
    return MatcherEquivalenceAssertion(expected_equivalent, model_infos)


class MatcherEquivalenceAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected_equivalent: Matcher,
                 model_infos: list):
        self.expected_equivalent = expected_equivalent
        self._model_infos = model_infos

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, Matcher)
        assert isinstance(value, Matcher)  # Type info for IDE

        # Check description

        actual_option_description = value.option_description
        expected_option_description = self.expected_equivalent.option_description

        put.assertEqual(expected_option_description,
                        actual_option_description,
                        message_builder.apply('actual_option_description'))

        # Check applications

        application_assertions = asrt.and_([
            MatcherEquivalenceOfCaseAssertion(self.expected_equivalent,
                                              model_info)
            for model_info in self._model_infos
        ])

        application_assertions.apply(put, value, message_builder.for_sub_component('application'))


class MatcherEquivalenceOfCaseAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected_equivalent: Matcher,
                 model_info: ModelInfo):
        self._expected_equivalent = expected_equivalent
        self._model_info = model_info

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, Matcher)
        assert isinstance(value, Matcher)  # Type info for IDE

        expected = self._expected_equivalent.matches(self._model_info.model)
        actual = value.matches(self._model_info.model)
        put.assertEqual(expected,
                        actual,
                        message_builder.apply('model=' + self._model_info.description_of_model))
