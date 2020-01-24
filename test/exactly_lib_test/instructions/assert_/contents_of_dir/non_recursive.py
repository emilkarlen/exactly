import unittest

from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.instructions.assert_.contents_of_dir.test_resources import files_matcher_integration
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import SourceArrangement, \
    ExecutionExpectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher, \
    files_matcher_sdv_constant_test_impl
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh, pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import path_argument, \
    RelOptPathArgument
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import TcdsPopulatorForRelOptionType
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources import \
    files_matcher_integration as fm_tr
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources import model_contents_check
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_validator import DdvValidatorThat
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer, SequenceOfArguments
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, empty_dir, sym_link, Dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidSyntax(),
        TestReferencedMatcherShouldBeValidated(),
        TestHardError(),
        unittest.makeSuite(TestApplication),
        TestFilesOfModel(),
        TestMultiLineSyntax(),
    ])


SYMBOL_NAME = 'FILES_MATCHER_SYMBOL'
EXPECTED_REFERENCE = is_reference_to_files_matcher(SYMBOL_NAME)

PARSER = sut.parser.Parser()

INSTRUCTION_CHECKER = instruction_check.Checker(
    PARSER
)


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue('Missing arguments',
                         '',
                         ),
            NameAndValue('Missing matcher argument',
                         'file',
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

        err_msg_from_validator = 'error from validator'
        name_of_referenced_symbol = 'FILES_MATCHER_SYMBOL'

        expected_symbol_usages = asrt.matches_sequence(
            [is_reference_to_files_matcher(name_of_referenced_symbol)])

        arguments = _arguments(
            path_argument('actual-dir'),
            SymbolReferenceArgument(name_of_referenced_symbol),
        )

        def arrangement(validator: DdvValidator) -> ArrangementPostAct2:
            return ArrangementPostAct2(
                symbols=SymbolTable({
                    name_of_referenced_symbol:
                        container(files_matcher_sdv_constant_test_impl(
                            resolved_value=True,
                            validator=validator,
                        ))
                }),
            )

        execution_cases = [
            NExArr('pre sds validation',
                   ExecutionExpectation(
                       validation_pre_sds=asrt_svh.is_validation_error(
                           asrt_text_doc.is_string_for_test_that_equals(err_msg_from_validator)
                       ),
                   ),
                   arrangement(
                       DdvValidatorThat(
                           pre_sds_return_value=asrt_text_doc.new_single_string_text_for_test(err_msg_from_validator)
                       ))
                   ),
            NExArr('post sds validation',
                   ExecutionExpectation(
                       main_result=asrt_pfh.is_hard_error(
                           asrt_text_doc.is_string_for_test_that_equals(err_msg_from_validator)
                       ),
                   ),
                   arrangement(
                       DdvValidatorThat(
                           post_setup_return_value=asrt_text_doc.new_single_string_text_for_test(err_msg_from_validator)
                       )
                   )
                   ),
        ]

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(arguments.as_arguments),
            symbol_usages=expected_symbol_usages,
            execution=execution_cases,
        )


class TestHardError(unittest.TestCase):
    UNCONDITIONALLY_CONSTANT_TRUE = NameAndValue(
        'unconditionally_constant_true',
        FilesMatcherSdv(
            matchers.sdv_from_bool(True)
        )
    )

    def runTest(self):
        # ARRANGE #

        actual_file_name = 'checked-file'

        file_location = RelOptionType.REL_TMP

        arguments = _arguments(
            RelOptPathArgument(actual_file_name, file_location),
            SymbolReferenceArgument(self.UNCONDITIONALLY_CONSTANT_TRUE.name),
        )

        symbols = symbol_utils.symbol_table_from_name_and_sdvs([self.UNCONDITIONALLY_CONSTANT_TRUE])
        expectation = ExecutionExpectation(
            main_result=asrt_pfh.is_hard_error__with_arbitrary_message(),
        )

        def arrangement(tcds: TcdsArrangementPostAct) -> ArrangementPostAct2:
            return ArrangementPostAct2(
                symbols=symbols,
                tcds=tcds,
            )

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(arguments.as_arguments),
            symbol_usages=asrt.matches_singleton_sequence(is_reference_to_files_matcher(
                self.UNCONDITIONALLY_CONSTANT_TRUE.name)
            ),
            execution=[
                NExArr(
                    'file does not exist',
                    expectation,
                    arrangement(
                        TcdsArrangementPostAct(),
                    )
                ),
                NExArr(
                    'file is a regular file',
                    expectation,
                    arrangement(
                        TcdsArrangementPostAct(
                            tcds_contents=TcdsPopulatorForRelOptionType(
                                file_location,
                                DirContents([empty_file(actual_file_name)]),
                            )
                        ),
                    )
                ),
                NExArr(
                    'file broken sym-link',
                    expectation,
                    arrangement(
                        TcdsArrangementPostAct(
                            tcds_contents=TcdsPopulatorForRelOptionType(
                                file_location,
                                DirContents([sym_link(actual_file_name, 'non-existing-target')]),
                            )
                        ),
                    )
                ),
            ],
        )


class TestApplication(unittest.TestCase):
    def test_wo_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWoSelectionTestCaseHelper(
            fm_tr.MODEL_CONTENTS__NON_RECURSIVE,
            RelOptionType.REL_ACT,
            'checked-dir',
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(helper.argument__non_recursive().as_arguments),
            symbol_usages=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )

    def test_w_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWFileTypeSelectionTestCaseHelper(
            fm_tr.MODEL_CONTENTS__NON_RECURSIVE__SELECTION_TYPE_FILE,
            RelOptionType.REL_ACT,
            'checked-dir',
        )
        # ACT & ASSERT #
        INSTRUCTION_CHECKER.check_multi__with_source_variants(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(helper.argument__non_recursive().as_arguments),
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

        arguments = _arguments(
            RelOptPathArgument(checked_dir_name, checked_dir_location),
            SymbolReferenceArgument(model_checker_symbol_name),
        )

        contents_cases = [
            model_contents_check.expected_is_actual_with_empty_dirs(case.name, case.value)
            for case in model_contents_check.cases()
        ]

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check_multi(
            self,
            SourceArrangement.new_w_arbitrary_fs_location(arguments.as_arguments),
            symbol_usages=asrt.matches_singleton_sequence(
                is_reference_to_files_matcher(model_checker_symbol_name)
            ),
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
                        symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                            model_checker_symbol_name:
                                model_contents_check.checker(self, checked_dir_path, contents_case.expected)
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
                'Dir on first line, matcher on following line',
                Arguments(checked_dir.name,
                          [matcher_argument]
                          ),
            ),
            NameAndValue(
                'Empty lines between arguments',
                Arguments(checked_dir.name,
                          [
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
                    symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                        files_matcher_name:
                            FilesMatcherSdv(matchers.sdv_from_bool(matcher_result))
                    })
                )
            )
            for matcher_result in [False, True]
        ]
        # ACT & ASSERT #

        for source_case in source_cases:
            with self.subTest(source_case=source_case):
                INSTRUCTION_CHECKER.check_multi__with_source_variants(
                    self,
                    SourceArrangement.new_w_arbitrary_fs_location(source_case.value),
                    symbol_usages=asrt.matches_singleton_sequence(is_reference_to_files_matcher(
                        files_matcher_name)
                    ),
                    execution=execution_cases,
                )


def _arguments(path: ArgumentElementsRenderer,
               files_matcher: ArgumentElementsRenderer) -> ArgumentElementsRenderer:
    return SequenceOfArguments([path, files_matcher])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
