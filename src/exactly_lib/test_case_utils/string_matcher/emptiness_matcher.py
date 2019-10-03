from typing import Optional

from exactly_lib.definitions.actual_file_attributes import CONTENTS_ATTRIBUTE
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.test_case_utils.description_tree import details
from exactly_lib.test_case_utils.err_msg import diff_msg
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTINESS_CHECK_EXPECTED_VALUE
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.type_system.logic.string_matcher import StringMatcher
from exactly_lib.util.logic_types import ExpectationType


class EmptinessStringMatcher(StringMatcher):
    def __init__(self, expectation_type: ExpectationType):
        super().__init__()
        self.expectation_type = expectation_type

    @property
    def name(self) -> str:
        return file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

    @property
    def option_description(self) -> str:
        return diff_msg.negation_str(self.expectation_type) + 'empty'

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        first_line = self._first_line(model)
        if self.expectation_type is ExpectationType.POSITIVE:
            if first_line != '':
                return _ErrorMessageResolver(self.expectation_type,
                                             model.describer,
                                             repr(first_line) + '...')
        else:
            if first_line == '':
                return _ErrorMessageResolver(self.expectation_type,
                                             model.describer,
                                             EMPTINESS_CHECK_EXPECTED_VALUE)
        return None

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        if self.expectation_type is ExpectationType.NEGATIVE:
            return combinator_matchers.Negation(EmptinessStringMatcher(ExpectationType.POSITIVE)).matches_w_trace(model)
        else:
            return self._matches_positive(model)

    def _matches_positive(self, model: FileToCheck) -> MatchingResult:
        first_line = self._first_line(model)
        if first_line != '':
            return (
                self._new_tb()
                    .append_details(
                    details.Actual(details.String(repr(first_line) + '...'))
                )
                    .build_result(False)
            )
        else:
            return self._new_tb().build_result(True)

    @staticmethod
    def _first_line(file_to_check: FileToCheck) -> str:
        with file_to_check.lines() as lines:
            for line in lines:
                return line
        return ''


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 expectation_type: ExpectationType,
                 actual_file_prop_descriptor_constructor: FilePropertyDescriptorConstructor,
                 actual: str,
                 ):
        self._expectation_type = expectation_type
        self._actual_file_prop_descriptor_constructor = actual_file_prop_descriptor_constructor
        self._actual = actual

    def resolve(self) -> str:
        diff_failure_info_resolver = self._failure_info_resolver(self._actual_file_prop_descriptor_constructor)
        failure_info = diff_failure_info_resolver.resolve(diff_msg.actual_with_single_line_value(self._actual))
        return failure_info.error_message()

    def _failure_info_resolver(self,
                               actual_file_prop_descriptor_constructor: FilePropertyDescriptorConstructor
                               ) -> diff_msg_utils.DiffFailureInfoResolver:
        return diff_msg_utils.DiffFailureInfoResolver(
            actual_file_prop_descriptor_constructor.construct_for_contents_attribute(CONTENTS_ATTRIBUTE),
            self._expectation_type,
            diff_msg_utils.expected_constant(EMPTINESS_CHECK_EXPECTED_VALUE),
        )
