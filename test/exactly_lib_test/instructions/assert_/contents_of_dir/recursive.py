import unittest

from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import files_matcher_integration
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import generated_case_execution
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.hard_error import \
    HardErrorDueToInvalidPathArgumentHelper, HardErrorDueToHardErrorFromFilesMatcherHelper
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources.validation import ValidationHelper
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import SourceArrangement, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import RelOptPathArgument
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import TcdsPopulatorForRelOptionType
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources import \
    files_matcher_integration as fm_tr
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.cases import file_type
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import test_data, model_checker
from exactly_lib_test.test_case_utils.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_resources.arguments_building import SequenceOfArguments, \
    OptionArgument
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, Dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidSyntax(),
        TestReferencedMatcherShouldBeValidated(),
        TestHardErrorDueToInvalidPathArgument(),
        TestErrorDueToHardErrorFromFilesMatcher(),
        unittest.makeSuite(TestApplication),
        TestFilesOfModel(),
        unittest.makeSuite(TestDetectionOfFileType),
        TestMultiLineSyntax(),
    ])


SYMBOL_NAME = 'FILES_MATCHER_SYMBOL'
EXPECTED_REFERENCE = is_reference_to_files_matcher(SYMBOL_NAME)

PARSER = sut.parser.Parser()

INSTRUCTION_CHECKER = instruction_check.Checker(
    PARSER
)

RECURSION_OPTION_ARG = OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name)
RECURSION_OPTION_STR = str(RECURSION_OPTION_ARG)


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('Missing arguments',
                         RECURSION_OPTION_STR,
                         ),
            NameAndValue('Missing matcher argument',
                         ' '.join([RECURSION_OPTION_STR,
                                   'file']),
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    PARSER.parse(ARBITRARY_FS_LOCATION_INFO,
                                 remaining_source(case.value))


class TestReferencedMatcherShouldBeValidated(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        helper = ValidationHelper()

        arguments = SequenceOfArguments([
            helper.path_argument(),
            RECURSION_OPTION_ARG,
            helper.files_matcher_reference_argument(),
        ])

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(arguments.as_arguments),
            symbol_usages=helper.expected_symbol_usages(),
            execution=helper.execution_cases(),
        )


class TestHardErrorDueToInvalidPathArgument(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        helper = HardErrorDueToInvalidPathArgumentHelper()

        arguments = SequenceOfArguments([
            helper.path_argument(),
            RECURSION_OPTION_ARG,
            helper.files_matcher_reference_argument(),
        ])

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(arguments.as_arguments),
            symbol_usages=helper.expected_symbol_usages(),
            execution=helper.execution_cases(),
        )


class TestErrorDueToHardErrorFromFilesMatcher(unittest.TestCase):
    def runTest(self):
        helper = HardErrorDueToHardErrorFromFilesMatcherHelper()

        arguments = SequenceOfArguments([
            helper.path_argument(),
            RECURSION_OPTION_ARG,
            helper.files_matcher_reference_argument(),
        ])

        INSTRUCTION_CHECKER.check(
            self,
            arguments.as_remaining_source,
            helper.arrangement(),
            helper.expectation(),
        )


class TestApplication(unittest.TestCase):
    def test_wo_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWoSelectionTestCaseHelper(
            fm_tr.MODEL_CONTENTS__RECURSIVE,
            RelOptionType.REL_ACT,
            'checked-dir',
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(helper.argument__recursive().as_arguments),
            symbol_usages=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )

    def test_w_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWFileTypeSelectionTestCaseHelper(
            fm_tr.MODEL_CONTENTS__RECURSIVE__SELECTION_TYPE_FILE,
            RelOptionType.REL_ACT,
            'checked-dir',
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(helper.argument__recursive().as_arguments),
            symbol_usages=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )


class TestFilesOfModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        checked_dir_location = RelOptionType.REL_TMP
        checked_dir_name = 'the-model-dir'
        checked_dir_path = path_sdvs.of_rel_option_with_const_file_name(checked_dir_location, checked_dir_name)

        model_checker_symbol_name = 'symbol_that_checks_model'

        arguments = SequenceOfArguments([
            RelOptPathArgument(checked_dir_name, checked_dir_location),
            RECURSION_OPTION_ARG,
            SymbolReferenceArgument(model_checker_symbol_name),
        ]
        )

        contents_cases = test_data.strip_file_type_info_s(
            [
                test_data.identical_expected_and_actual(case.name, case.value)
                for case in test_data.cases()
            ]
        )

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check_multi(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(arguments.as_arguments),
            ParseExpectation(
                symbol_usages=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher(model_checker_symbol_name)
                )),
            execution=[
                NExArr(
                    contents_case.name,
                    ExecutionExpectation(),
                    ArrangementPostAct2(
                        tcds=TcdsArrangementPostAct(
                            tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                                checked_dir_location,
                                DirContents([
                                    Dir(checked_dir_name, contents_case.actual)
                                ])
                            )
                        ),
                        symbols=SymbolTable({
                            model_checker_symbol_name:
                                model_checker.matcher__sym_tbl_container(self, checked_dir_path, contents_case.expected)
                        })
                    ),
                )
                for contents_case in contents_cases
            ],
        )


class TestMultiLineSyntax(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        files_matcher_name = 'the_files_matcher'
        checked_dir_location = RelOptionType.REL_ACT
        checked_dir = empty_dir('checked-dir')

        matcher_argument = SymbolReferenceArgument(files_matcher_name).as_str

        tcds = TcdsArrangementPostAct(
            TcdsPopulatorForRelOptionType(
                checked_dir_location,
                DirContents([checked_dir])
            ))

        source_cases = [
            NameAndValue(
                'All arguments on separate lines',
                Arguments(checked_dir.name,
                          [
                              RECURSION_OPTION_STR,
                              matcher_argument
                          ]
                          ),
            ),
            NameAndValue(
                'Empty lines between arguments',
                Arguments(checked_dir.name,
                          [
                              '',
                              RECURSION_OPTION_STR,
                              '',
                              matcher_argument,
                          ]),
            ),
        ]

        execution_cases = [
            NExArr(
                'matcher gives ' + str(matcher_result),
                ExecutionExpectation(
                    main_result=asrt_pfh.is_non_hard_error(matcher_result)
                ),
                ArrangementPostAct2(
                    tcds,
                    symbols=FilesMatcherSymbolContext.of_primitive_constant(files_matcher_name,
                                                                            matcher_result
                                                                            ).symbol_table
                )
            )
            for matcher_result in [False, True]
        ]
        # ACT & ASSERT #

        for source_case in source_cases:
            with self.subTest(source_case=source_case.name):
                INSTRUCTION_CHECKER.check_multi__with_source_variants(
                    self,
                    SourceArrangement.new_w_arbitrary_fs_location(source_case.value),
                    symbol_usages=asrt.matches_singleton_sequence(is_reference_to_files_matcher(
                        files_matcher_name)
                    ),
                    execution=execution_cases,
                )


class TestDetectionOfFileType(unittest.TestCase):
    def test_depth_0(self):
        _EXECUTOR.execute_list(
            self,
            file_type.file_type_detection__recursive__depth_0()
        )

    def test_depth_1(self):
        _EXECUTOR.execute_list(
            self,
            file_type.file_type_detection__recursive__depth_1()
        )


_EXECUTOR = generated_case_execution.ExecutorOfCaseGeneratorForDirContents()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
