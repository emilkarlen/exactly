import unittest

from exactly_lib.instructions.assert_.utils.file_contents.parts import line_matches as sut
from exactly_lib.test_case.os_services import new_default
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.instructions.assert_.utils.file_contents.contents_checkers import \
    FilePropertyDescriptorConstructorTestImpl
from exactly_lib_test.instructions.assert_.utils.file_contents.test_resources import \
    destination_file_path_getter_that_gives_seq_of_unique_paths
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check as asrt_pfh
from exactly_lib_test.test_case.test_resources.instruction_environment import fake_post_sds_environment
from exactly_lib_test.test_resources.file_utils import tmp_file_containing


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestAnyLineMatches)


class Case:
    def __init__(self,
                 name: str,
                 file_contents: str,
                 expected: list):
        self.name = name
        self.file_contents = file_contents
        self.expected = expected


class TestAnyLineMatches(unittest.TestCase):
    def test_no_lines(self):
        empty_file_contents = ''

        environment = fake_post_sds_environment()
        checked_file_describer = FilePropertyDescriptorConstructorTestImpl()
        os_services = new_default()

        cases = [
            (ExpectationType.POSITIVE, asrt_pfh.is_fail()),
            (ExpectationType.NEGATIVE, asrt_pfh.is_pass()),
        ]

        unconditionally_true = LineMatcherConstantResolver(LineMatcherConstant(True))
        with destination_file_path_getter_that_gives_seq_of_unique_paths() as dst_file_path_getter:
            # This test is expected to not create files using the above object,
            # but to be sure, one is used that creates and destroys temporary files.
            with tmp_file_containing(empty_file_contents) as actual_file_path:
                for expectation_type, pfh_result_assertion in cases:
                    with self.subTest(expectation_type=expectation_type):
                        ftc = sut.FileToCheck(actual_file_path,
                                              checked_file_describer,
                                              environment,
                                              IdentityLinesTransformer(),
                                              dst_file_path_getter)
                        assertion_part = sut.assertion_part_for_any_line_matches(expectation_type,
                                                                                 unconditionally_true)
                        # ACT #
                        actual = assertion_part.check_and_return_pfh(environment, os_services, ftc)
                        # ASSERT #
                        pfh_result_assertion.apply_without_message(self, actual)


class LineMatcherThatMatchesIfIdentical(LineMatcher):
    def __init__(self,
                 expected_line_num: int,
                 expected_line_contents: str):
        self.expected_line_num = expected_line_num
        self.expected_line_contents = expected_line_contents

    def matches(self, line: tuple) -> bool:
        return self.expected_line_num == line[0] and \
               self.expected_line_contents == line[1]

    @property
    def option_description(self) -> str:
        return str(type(self))
