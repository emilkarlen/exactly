import difflib
from typing import List

import pathlib

from exactly_lib.definitions.actual_file_attributes import CONTENTS_ATTRIBUTE
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.err_msg.diff_msg import ActualInfo
from exactly_lib.test_case_utils.err_msg.diff_msg_utils import DiffFailureInfoResolver
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, FilePropertyDescriptorConstructor, \
    ErrorMessageResolver
from exactly_lib.util import file_utils
from exactly_lib.util.logic_types import ExpectationType


class ExpectedValueResolver(diff_msg_utils.ExpectedValueResolver):
    def __init__(self,
                 prefix: str,
                 expected_contents: RegexResolver):
        self._prefix = prefix
        self.expected_contents = expected_contents

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        prefix = ''
        if self._prefix:
            prefix = self._prefix + ' '
        return prefix + self._expected_obj_description(environment)

    def _expected_obj_description(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return 'todo'

    def _string_fragment(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        return 'todo'


class ErrorMessageResolverConstructor:
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_value: diff_msg_utils.ExpectedValueResolver,
                 ):
        self._expectation_type = expectation_type
        self._expected_value = expected_value

    def construct(self,
                  checked_file: FilePropertyDescriptorConstructor,
                  actual_info: ActualInfo) -> ErrorMessageResolver:
        return _ErrorMessageResolver(self._expectation_type,
                                     self._expected_value,
                                     checked_file,
                                     actual_info)


def _file_diff_description(actual_file_path: pathlib.Path,
                           expected_file_path: pathlib.Path) -> List[str]:
    expected_lines = file_utils.lines_of(expected_file_path)
    actual_lines = file_utils.lines_of(actual_file_path)
    diff = difflib.unified_diff(expected_lines,
                                actual_lines,
                                fromfile='Expected',
                                tofile='Actual')
    return list(diff)


class _ErrorMessageResolver(ErrorMessageResolver):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected_value: ExpectedValueResolver,
                 checked_file_describer: FilePropertyDescriptorConstructor,
                 actual_info: ActualInfo
                 ):
        self._expected_value = expected_value
        self._expectation_type = expectation_type
        self._checked_file_describer = checked_file_describer
        self._actual_info = actual_info

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        description_of_actual_file = self._checked_file_describer.construct_for_contents_attribute(CONTENTS_ATTRIBUTE)
        failure_info_resolver = DiffFailureInfoResolver(
            description_of_actual_file,
            self._expectation_type,
            self._expected_value,
        )
        failure_info = failure_info_resolver.resolve(environment, self._actual_info)
        return failure_info.error_message()