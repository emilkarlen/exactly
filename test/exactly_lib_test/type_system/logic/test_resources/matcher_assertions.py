import unittest
from typing import List, Generic, TypeVar, Callable

from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase

MODEL = TypeVar('MODEL')


class ModelInfo(Generic[MODEL]):
    def __init__(self,
                 model: MODEL,
                 mk_description_of_model: Callable[[MODEL], str] = str):
        self.model = model
        self._mk_description_of_model = mk_description_of_model

    @property
    def description_of_model(self) -> str:
        return self._mk_description_of_model(self.model)


def is_equivalent_to(expected_equivalent: MatcherWTrace[MODEL],
                     model_infos: List[ModelInfo[MODEL]]) -> ValueAssertion[MatcherWTrace[MODEL]]:
    return MatcherEquivalenceAssertion(expected_equivalent, model_infos)


class MatcherEquivalenceAssertion(Generic[MODEL], ValueAssertionBase[MatcherWTrace[MODEL]]):
    def __init__(self,
                 expected_equivalent: MatcherWTrace[MODEL],
                 model_infos: List[ModelInfo[MODEL]]):
        self.expected_equivalent = expected_equivalent
        self._model_infos = model_infos

    def _apply(self,
               put: unittest.TestCase,
               value: MatcherWTrace[MODEL],
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, MatcherWTrace)
        assert isinstance(value, MatcherWTrace)  # Type info for IDE

        # Check description

        actual_structure = value.structure().render()
        expected_structure = self.expected_equivalent.structure().render()

        put.assertEqual(expected_structure.header,
                        actual_structure.header,
                        message_builder.apply('header'))

        # Check applications

        application_assertions = asrt.and_([
            MatcherEquivalenceOfCaseAssertion(self.expected_equivalent,
                                              model_info)
            for model_info in self._model_infos
        ])

        application_assertions.apply(put, value, message_builder.for_sub_component('application'))


class MatcherEquivalenceOfCaseAssertion(Generic[MODEL], ValueAssertionBase[MatcherWTrace[MODEL]]):
    def __init__(self,
                 expected_equivalent: MatcherWTrace[MODEL],
                 model_info: ModelInfo[MODEL]):
        self._expected_equivalent = expected_equivalent
        self._model_info = model_info

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, MatcherWTrace)
        assert isinstance(value, MatcherWTrace)  # Type info for IDE

        expected = self._expected_equivalent.matches_w_trace(self._model_info.model)
        actual = value.matches_w_trace(self._model_info.model)
        put.assertEqual(expected.value,
                        actual.value,
                        message_builder.apply('model=' + self._model_info.description_of_model))
