import unittest
from pathlib import PurePosixPath
from typing import Optional, Set, Mapping

from exactly_lib.test_case_utils.files_condition.structure import FilesCondition
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.type_system.logic.test_resources.file_matcher import FileMatcherModelThatMustNotBeAccessed
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def file_names_equals(expected: Set[PurePosixPath]
                      ) -> ValueAssertion[Mapping[PurePosixPath, Optional[FileMatcher]]]:
    return asrt.on_transformed(
        lambda d: d.keys(),
        asrt.equals(expected)
    )


def files_matches(expected: Mapping[PurePosixPath, ValueAssertion[Optional[FileMatcher]]]
                  ) -> ValueAssertion[FilesCondition]:
    return asrt.sub_component(
        'files',
        FilesCondition.files.fget,
        asrt.matches_mapping(expected)
    )


def assert_files(expected: ValueAssertion[Mapping[PurePosixPath, Optional[FileMatcher]]]
                 ) -> ValueAssertion[FilesCondition]:
    return asrt.sub_component(
        'files',
        FilesCondition.files.fget,
        expected
    )


def is_matcher_that_gives(expected: bool) -> ValueAssertion[Optional[FileMatcher]]:
    return asrt.is_not_none_and_instance_with(
        FileMatcher,
        _MatcherGives(expected),
    )


class _MatcherGives(ValueAssertionBase[FileMatcher]):
    MODEL = FileMatcherModelThatMustNotBeAccessed()

    def __init__(self, expected: bool):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: FileMatcher,
               message_builder: MessageBuilder,
               ):
        actual = value.matches_w_trace(self.MODEL)
        asrt_matching_result.matches_value(self.expected).apply(
            put,
            actual,
            message_builder.for_sub_component('application result')
        )
