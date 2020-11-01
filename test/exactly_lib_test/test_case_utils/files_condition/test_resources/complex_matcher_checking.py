import unittest
from pathlib import PurePosixPath
from typing import List, Sequence, Tuple, Mapping, Optional

from exactly_lib.test_case_utils.files_condition.structure import FilesCondition
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel, FileMatcher
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_case_utils.file_matcher.test_resources.file_matchers import FileMatcherTestImplBase
from exactly_lib_test.test_case_utils.files_condition.test_resources import primitive_assertions as asrt_primitive
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, T, MessageBuilder, \
    ValueAssertion
from exactly_lib_test.type_val_prims.matcher.test_resources import matching_result


class IntSequence:
    def __init__(self, first: int):
        self._next = first

    def next(self) -> int:
        self._next += 1
        return self._next - 1


class ConstantMatcherThatRegistersApplication(FileMatcherTestImplBase):
    def __init__(self,
                 name_for_err_msgs: str,
                 result: bool,
                 sequence_to_register_from: IntSequence,
                 ):
        super().__init__()
        self.name_for_err_msgs = name_for_err_msgs
        self._result = result
        self._sequence = sequence_to_register_from
        self.registrations = []

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        self.registrations.append(self._sequence.next())
        return matching_result.of(self._result)


class ApplicationSequenceFrom1Builder:
    def __init__(self):
        self._sequence = IntSequence(1)
        self._matchers_w_expected = []

    def add_applied(self,
                    name_and_result: NameAndValue[bool],
                    expected_order: int,
                    ) -> FileMatcherSdv:
        return self._registering_matcher_of(name_and_result, [expected_order])

    def add_un_applied(self, name_and_result: NameAndValue[bool]) -> FileMatcherSdv:
        return self._registering_matcher_of(name_and_result, [])

    def _registering_matcher_of(self,
                                name_and_result: NameAndValue[bool],
                                expected_applications: List[int],
                                ) -> FileMatcherSdv:
        matcher = ConstantMatcherThatRegistersApplication(
            name_and_result.name,
            name_and_result.value,
            self._sequence,
        )
        self._matchers_w_expected.append((matcher, expected_applications))

        return self._sdv(matcher)

    def expected_application_sequence(self) -> Sequence[Tuple[ConstantMatcherThatRegistersApplication, List[int]]]:
        return self._matchers_w_expected

    @staticmethod
    def _sdv(primitive: FileMatcher) -> FileMatcherSdv:
        return matchers.MatcherSdvOfConstantDdvTestImpl(
            matchers.MatcherDdvOfConstantMatcherTestImpl(primitive)
        )


class MatcherApplicationSequenceAssertion(ValueAssertionBase[T]):
    def __init__(self, matchers_and_expected_s: Sequence[Tuple[ConstantMatcherThatRegistersApplication, List[int]]]):
        self._matchers_and_expected_s = matchers_and_expected_s

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder,
               ):
        for matcher, expected in self._matchers_and_expected_s:
            asrt.equals(expected).apply_with_message(
                put,
                matcher.registrations,
                message_builder.apply(matcher.name_for_err_msgs)
            )


def matches_w_application_order(
        files_and_results: Mapping[PurePosixPath, ValueAssertion[Optional[FileMatcher]]],
        application_sequence: Sequence[Tuple[ConstantMatcherThatRegistersApplication, List[int]]],
) -> ValueAssertion[FilesCondition]:
    return asrt.and_([
        asrt_primitive.files_matches(files_and_results),
        asrt.named('application order',
                   MatcherApplicationSequenceAssertion(application_sequence))
    ])
