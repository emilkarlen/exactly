import unittest
from pathlib import PurePosixPath
from typing import Optional, Set, Mapping

from exactly_lib.type_val_prims.files_condition import FilesCondition
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase, \
    MessageBuilder
from exactly_lib_test.type_val_prims.matcher.test_resources.file_matcher import FileMatcherModelThatMustNotBeAccessed
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result


def file_names_equals(expected: Set[PurePosixPath]
                      ) -> Assertion[Mapping[PurePosixPath, Optional[FileMatcher]]]:
    return asrt.on_transformed(
        lambda d: d.keys(),
        asrt.equals(expected)
    )


def files_matches(expected: Mapping[PurePosixPath, Assertion[Optional[FileMatcher]]]
                  ) -> Assertion[FilesCondition]:
    return assert_files(asrt.matches_mapping(expected))


def assert_files(expected: Assertion[Mapping[PurePosixPath, Optional[FileMatcher]]]
                 ) -> Assertion[FilesCondition]:
    return asrt.sub_component(
        'files',
        _get_files,
        expected
    )


def is_matcher_that_gives(expected: bool) -> Assertion[Optional[FileMatcher]]:
    return asrt.is_not_none_and_instance_with(
        MatcherWTrace,
        _MatcherGives(expected),
    )


class _MatcherGives(AssertionBase[FileMatcher]):
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


def _get_files(x: FilesCondition) -> Mapping[PurePosixPath, Optional[FileMatcher]]:
    return x.files
