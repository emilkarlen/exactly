import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.w_depth_limits import cases
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.w_depth_limits.test_case_execution import \
    execute_single, execute_list, execute_multi
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestParseShouldFailWhenInvalidLimitOption(),
        TestValidationPreSdsShouldFailWhenLimitsAreNotExpressionsThatEvaluatesToAnInteger(),
        TestValidationPreSdsShouldFailWhenLimitsAreIntegerOutOfRange(),
        TestFilesOfModel(),
        TestSymbolReferencesShouldBeReported(),
        TestSelectorShouldBeApplied(),
    ])


class TestParseShouldFailWhenInvalidLimitOption(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            integration_check.CHECKER.parser.parse(
                fm_args.DirContentsRecursiveInvalidOptionArgs(
                    'invalid-option'
                )
                    .as_remaining_source
            )


class TestValidationPreSdsShouldFailWhenLimitsAreNotExpressionsThatEvaluatesToAnInteger(unittest.TestCase):
    def runTest(self):
        execute_list(
            self,
            cases.validation_pre_sds_should_fail_when_limits_are_not_expressions_that_evaluates_to_an_integer()
        )


class TestValidationPreSdsShouldFailWhenLimitsAreIntegerOutOfRange(unittest.TestCase):
    def runTest(self):
        execute_list(
            self,
            cases.validation_pre_sds_should_fail_when_limits_are_integer_out_of_range()
        )


class TestFilesOfModel(unittest.TestCase):
    def runTest(self):
        execute_list(
            self,
            cases.files_of_model()
        )


class TestSymbolReferencesShouldBeReported(unittest.TestCase):
    def runTest(self):
        execute_single(self, cases.SymbolReferencesShouldBeReported())


class TestSelectorShouldBeApplied(unittest.TestCase):
    def runTest(self):
        execute_multi(self, cases.SelectorShouldBeApplied())
