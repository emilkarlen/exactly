import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.test_case_utils.files_condition.test_resources.arguments_building import FilesConditionArg
from exactly_lib_test.test_case_utils.files_matcher.test_resources.files_condition import contains_and_equals_cases


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_parse_SHOULD_fail_WHEN_no_argument(self):
        _assert_parse_raises(self, fc_args.Missing())

    def test_parse_SHOULD_fail_WHEN_argument_is_not_a_files_condition(self):
        _assert_parse_raises(self, fc_args.InvalidSyntax())


def _assert_parse_raises(put: unittest.TestCase, files_condition: FilesConditionArg):
    for case in contains_and_equals_cases():
        source = case.value(files_condition).as_remaining_source
        with put.subTest(case.name):
            with put.assertRaises(SingleInstructionInvalidArgumentException):
                sut.files_matcher_parser().parse(source)
