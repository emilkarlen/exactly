import unittest
from typing import Sequence

from exactly_lib.impls.instructions.multi_phase import new_dir as sut
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources.abstract_syntax import NewDirArguments
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources.assertions import is_success, is_failure
from exactly_lib_test.impls.instructions.multi_phase.new_dir.test_resources.path_config import RELATIVITY_OPTIONS, \
    SETUP_CWD_TO_NON_TCDS_DIR_ACTION
from exactly_lib_test.impls.instructions.multi_phase.test_resources import embryo_arr_exp
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import TcdsExpectation
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.test_resources.test_utils import NInpArr
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import PathStringAbsStx, \
    RelOptPathAbsStx, FileNameComponents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestFailingScenarios),
        TestCreationOfDirectoryWithSinglePathComponent(),
        TestCreationOfDirectoryWithMultiplePathComponents(),
        TestWholeArgumentExistsAsDirectory(),
        TestInitialComponentOfArgumentExistsAsDirectory(),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        PARSE_CHECKER.check_invalid_syntax__abs_stx(self, CustomAbsStx.empty())

    def test_fail_when_superfluous_arguments(self):
        invalid_syntax = SequenceAbsStx.followed_by_superfluous(
            NewDirArguments.implicitly_empty(PathStringAbsStx.of_plain_str('valid_file_name'))
        )
        PARSE_CHECKER.check_invalid_syntax__abs_stx(self, invalid_syntax)

    def test_rel_result_option_is_not_allowed(self):
        invalid_syntax = RelOptPathAbsStx(RelOptionType.REL_RESULT, 'valid_file_name')
        PARSE_CHECKER.check_invalid_syntax__abs_stx(self, invalid_syntax)


class TestCreationOfDirectoryWithSinglePathComponent(unittest.TestCase):
    def runTest(self):
        expected_created_dir = fs.Dir.empty('dir-that-should-be-constructed')

        for rel_conf in RELATIVITY_OPTIONS:
            dst_path = rel_conf.path_abs_stx_of_name(expected_created_dir.name)
            instruction_syntax = NewDirArguments.implicitly_empty(dst_path)
            # ACT & ASSERT #
            _CHECKER.check__abs_stx__std_layouts_and_source_variants(
                self,
                instruction_syntax,
                embryo_arr_exp.Arrangement.phase_agnostic(
                    symbols=rel_conf.symbols.in_arrangement(),
                    tcds=TcdsArrangement(
                        pre_population_action=SETUP_CWD_TO_NON_TCDS_DIR_ACTION
                    )
                ),
                embryo_arr_exp.MultiSourceExpectation.phase_agnostic_2(
                    symbol_usages=rel_conf.symbols.usages_expectation(),
                    main_result=is_success(),
                    main_side_effects_on_files=TcdsExpectation(
                        sds=rel_conf.assert_root_dir_contains_exactly__p([
                            expected_created_dir
                        ])
                    )
                ),
                sub_test_identifiers={
                    'relativity': rel_conf.name,
                }
            )


class TestCreationOfDirectoryWithMultiplePathComponents(unittest.TestCase):
    def runTest(self):
        sub_dir = fs.Dir.empty('sub-dir')
        top_dir = fs.Dir('top-dir', [sub_dir])

        for rel_conf in RELATIVITY_OPTIONS:
            dst_path = rel_conf.path_abs_stx_of_name__c([top_dir.name, sub_dir.name])
            instruction_syntax = NewDirArguments.implicitly_empty(dst_path)
            with self.subTest(relativity=rel_conf.name):
                # ACT & ASSERT #
                _CHECKER.check__abs_stx(
                    self,
                    instruction_syntax,
                    embryo_arr_exp.Arrangement.phase_agnostic(
                        symbols=rel_conf.symbols.in_arrangement(),
                        tcds=TcdsArrangement(
                            pre_population_action=SETUP_CWD_TO_NON_TCDS_DIR_ACTION
                        )
                    ),
                    embryo_arr_exp.Expectation.phase_agnostic_3(
                        symbol_usages=rel_conf.symbols.usages_expectation(),
                        main_result=is_success(),
                        main_side_effects_on_files=TcdsExpectation(
                            sds=rel_conf.assert_root_dir_contains_exactly__p([
                                top_dir
                            ])
                        )
                    ),
                )


class TestWholeArgumentExistsAsDirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        an_empty_dir = fs.Dir.empty('an-empty-dir')
        top_dir_with_sub_dir = fs.Dir('top-dir', [an_empty_dir])

        path_cases: Sequence[NInpArr[FileNameComponents, FileSystemElement]] = [
            NInpArr(
                'direct',
                [an_empty_dir.name],
                an_empty_dir,
            ),
            NInpArr(
                'dir in dir',
                [top_dir_with_sub_dir.name, an_empty_dir.name],
                top_dir_with_sub_dir,
            ),
        ]
        for path_case in path_cases:
            for rel_conf in RELATIVITY_OPTIONS:
                dst_path = rel_conf.path_abs_stx_of_name__c(path_case.input)
                instruction_syntax = NewDirArguments.implicitly_empty(dst_path)
                # ACT & ASSERT #
                with self.subTest(relativity=rel_conf.name,
                                  path=path_case.name):
                    _CHECKER.check__abs_stx(
                        self,
                        instruction_syntax,
                        embryo_arr_exp.Arrangement.phase_agnostic(
                            symbols=rel_conf.symbols.in_arrangement(),
                            tcds=TcdsArrangement(
                                pre_population_action=SETUP_CWD_TO_NON_TCDS_DIR_ACTION,
                                tcds_contents=rel_conf.populator_for_relativity_option_root__s([path_case.arrangement]),
                            )
                        ),
                        embryo_arr_exp.Expectation.phase_agnostic_3(
                            symbol_usages=rel_conf.symbols.usages_expectation(),
                            main_result=is_failure(),
                        ),
                    )


class TestInitialComponentOfArgumentExistsAsDirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        non_existing_leaf = fs.Dir.empty('leaf-dir')
        existing_top_dir__name = 'top-dir'
        for rel_conf in RELATIVITY_OPTIONS:
            dst_path = rel_conf.path_abs_stx_of_name__c([existing_top_dir__name, non_existing_leaf.name])
            instruction_syntax = NewDirArguments.implicitly_empty(dst_path)
            # ACT & ASSERT #
            with self.subTest(relativity=rel_conf.name):
                _CHECKER.check__abs_stx(
                    self,
                    instruction_syntax,
                    embryo_arr_exp.Arrangement.phase_agnostic(
                        symbols=rel_conf.symbols.in_arrangement(),
                        tcds=TcdsArrangement(
                            pre_population_action=SETUP_CWD_TO_NON_TCDS_DIR_ACTION,
                            tcds_contents=rel_conf.populator_for_relativity_option_root__s([
                                fs.Dir.empty(existing_top_dir__name)
                            ]),
                        )
                    ),
                    embryo_arr_exp.Expectation.phase_agnostic_3(
                        symbol_usages=rel_conf.symbols.usages_expectation(),
                        main_result=is_success(),
                        main_side_effects_on_files=TcdsExpectation(
                            sds=rel_conf.assert_root_dir_contains_exactly__p([
                                fs.Dir(existing_top_dir__name, [non_existing_leaf])
                            ])
                        )
                    ),
                )


class TestFailingScenarios(unittest.TestCase):
    def test_invalid_path(self):
        # ARRANGE #
        existing_file = fs.File.empty('existing-file')
        existing_dir_with_file = fs.Dir('existing-dir', [existing_file])
        path_cases: Sequence[NInpArr[FileNameComponents, FileSystemElement]] = [
            NInpArr(
                'file (direct)',
                [existing_file.name],
                existing_file,
            ),
            NInpArr(
                'file in dir',
                [existing_dir_with_file.name, existing_file.name],
                existing_dir_with_file,
            ),
            NInpArr(
                'middle component is regular file',
                [existing_file.name, 'non-existing'],
                existing_file,
            ),
        ]
        for path_case in path_cases:
            for rel_conf in RELATIVITY_OPTIONS:
                syntax_of_existing_file = NewDirArguments.implicitly_empty(
                    rel_conf.path_abs_stx_of_name__c(path_case.input)
                )
                with self.subTest(relativity=rel_conf.name,
                                  path=path_case.name):
                    # ACT & ASSERT #
                    _CHECKER.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        syntax_of_existing_file,
                        embryo_arr_exp.Arrangement.phase_agnostic(
                            symbols=rel_conf.symbols.in_arrangement(),
                            tcds=TcdsArrangement(
                                pre_population_action=SETUP_CWD_TO_NON_TCDS_DIR_ACTION,
                                tcds_contents=rel_conf.populator_for_relativity_option_root__s([path_case.arrangement])
                            )
                        ),
                        embryo_arr_exp.MultiSourceExpectation.phase_agnostic_2(
                            symbol_usages=rel_conf.symbols.usages_expectation(),
                            main_result=is_failure(),
                        ),
                        sub_test_identifiers={
                            'relativity': rel_conf.name,
                            'path': path_case.name
                        }
                    )


_CHECKER = embryo_check.Checker(sut.EmbryoParser())

PARSE_CHECKER = parse_checker.Checker(sut.EmbryoParser())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
