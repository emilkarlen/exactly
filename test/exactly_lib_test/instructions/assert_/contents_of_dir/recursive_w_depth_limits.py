import unittest

from exactly_lib.instructions.assert_.contents_of_dir import parser as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import generated_case_execution
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case_file_structure.test_resources.path_arguments import RelOptPathArgument
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.cases import recursive_w_depth_limits
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_resources.arguments_building import SequenceOfArguments


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
            sut.Parser().parse(
                ARBITRARY_FS_LOCATION_INFO,
                SequenceOfArguments([
                    RelOptPathArgument('checked-dir',
                                       RelOptionType.REL_CWD,
                                       ),
                    fm_args.DirContentsRecursiveInvalidOptionArgs(
                        'invalid-option'
                    )
                    ,
                ]).as_remaining_source
            )


class TestValidationPreSdsShouldFailWhenLimitsAreNotExpressionsThatEvaluatesToAnInteger(unittest.TestCase):
    def runTest(self):
        _EXECUTOR.execute_list(
            self,
            recursive_w_depth_limits.validation_pre_sds_should_fail_when_limits_are_not_expressions_that_evaluates_to_an_integer()
        )


class TestValidationPreSdsShouldFailWhenLimitsAreIntegerOutOfRange(unittest.TestCase):
    def runTest(self):
        _EXECUTOR.execute_list(
            self,
            recursive_w_depth_limits.validation_pre_sds_should_fail_when_limits_are_integer_out_of_range()
        )


class TestFilesOfModel(unittest.TestCase):
    def runTest(self):
        _EXECUTOR.execute_list(
            self,
            recursive_w_depth_limits.files_of_model()
        )


class TestSymbolReferencesShouldBeReported(unittest.TestCase):
    def runTest(self):
        _EXECUTOR.execute_single(self, recursive_w_depth_limits.SymbolReferencesShouldBeReported())


class TestSelectorShouldBeApplied(unittest.TestCase):
    def runTest(self):
        _EXECUTOR.execute_multi(self, recursive_w_depth_limits.SelectorShouldBeApplied())


_EXECUTOR = generated_case_execution.ExecutorOfCaseGeneratorForDirContents()
