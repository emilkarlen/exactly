import unittest
from typing import Generic, Callable, Any

from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib_test.impls.types.matcher.test_resources.matchers import MODEL, STRUCTURE_FOR_TEST, ACTUAL
from exactly_lib_test.test_resources.recording import SequenceRecordingMedia
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result


class MatcherWInitialAction(Generic[MODEL], MatcherWTrace[MODEL]):
    """A constant matcher that applies an action, before returning it's result."""

    def __init__(self,
                 initial_action: Callable[[MODEL], Any],
                 result: MatchingResult,
                 structure: StructureRenderer = STRUCTURE_FOR_TEST,
                 ):
        self._initial_action = initial_action
        self._result = result
        self._structure = structure

    @property
    def name(self) -> str:
        return str(type(self))

    def structure(self) -> StructureRenderer:
        return self._structure

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        self._initial_action(model)
        return self._result


def matcher_that_applies_assertion(put: unittest.TestCase,
                                   assertion: ValueAssertion[ACTUAL],
                                   get_actual: Callable[[MODEL], ACTUAL],
                                   message_builder: MessageBuilder,
                                   result: bool,
                                   structure: StructureRenderer = STRUCTURE_FOR_TEST,
                                   ) -> MatcherWTrace[MODEL]:
    return MatcherWInitialAction(
        ActionThatAppliesAssertion(put,
                                   assertion,
                                   get_actual,
                                   message_builder,
                                   ).action,
        matching_result.of(result),
        structure,
    )


class ActionThatAppliesAssertion(Generic[MODEL, ACTUAL]):
    def __init__(self,
                 put: unittest.TestCase,
                 assertion: ValueAssertion[ACTUAL],
                 get_actual: Callable[[MODEL], ACTUAL],
                 message_builder: MessageBuilder,
                 ):
        self.put = put
        self.assertion = assertion
        self.get_actual = get_actual
        self.message_builder = message_builder

    def action(self, model: MODEL):
        actual = self.get_actual(model)
        self.assertion.apply(
            self.put,
            actual,
            self.message_builder.for_sub_component('application'),
        )


class ActionThatAppliesAssertion2(Generic[MODEL]):
    def __init__(self,
                 put: unittest.TestCase,
                 assertion: ValueAssertion[MODEL],
                 message_builder: MessageBuilder,
                 ):
        self.put = put
        self.assertion = assertion
        self.message_builder = message_builder

    def action(self, model: MODEL):
        self.assertion.apply(
            self.put,
            model,
            self.message_builder.for_sub_component('application'),
        )


class IntSequence:
    def __init__(self, first: int):
        self._next = first

    def next(self) -> int:
        self._next += 1
        return self._next - 1


class IntSequenceRegistry:
    def __init__(self,
                 sequence_to_register_from: IntSequence,
                 recording_media: SequenceRecordingMedia[int],
                 ):
        self._sequence_to_register_from = sequence_to_register_from
        self._recording_media = recording_media

    def action(self, model):
        self._recording_media.record(self._sequence_to_register_from.next())
