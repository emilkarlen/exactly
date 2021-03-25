import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import abstract_syntax as abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import common_test_cases
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import integration_check
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.defs import DISALLOWED_DST_RELATIVITIES, \
    ALLOWED_DST_FILE_RELATIVITIES
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.parse_check import \
    check_invalid_syntax__abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.utils import \
    IS_SUCCESS
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, \
    MultiSourceExpectation
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as fs_abs_stx
from exactly_lib_test.impls.types.test_resources.relativity_options import conf_rel_any
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File, Dir
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR__PLAIN
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import CustomPathAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import RelOptPathAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSuccessfulScenariosWithNoContents),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestFailingParse(unittest.TestCase):
    def test_missing_path(self):
        empty_path_argument = CustomPathAbsStx.empty()
        arguments_w_missing_path = abs_stx.without_contents(empty_path_argument)
        check_invalid_syntax__abs_stx(
            self,
            arguments_w_missing_path
        )

    def test_disallowed_relativities(self):
        # ARRANGE #
        for relativity in DISALLOWED_DST_RELATIVITIES:
            relativity_conf = conf_rel_any(relativity)
            instruction_syntax = abs_stx.without_contents(relativity_conf.path_abs_stx_of_name('file-name'))
            # ACT & ASSERT #
            check_invalid_syntax__abs_stx(
                self,
                instruction_syntax,
                sub_test_identifiers={
                    'relativity': relativity,
                }
            )

    def test_superfluous_arguments(self):
        # ARRANGE #
        valid_path = RelOptPathAbsStx(RelOptionType.REL_ACT, 'valid-file-name')
        valid_syntax = abs_stx.without_contents(valid_path)
        invalid_syntax = SequenceAbsStx.followed_by_superfluous(valid_syntax)
        # ACT & ASSERT #
        check_invalid_syntax__abs_stx(self, invalid_syntax)


class TestSuccessfulScenariosWithNoContents(unittest.TestCase):
    def test_single_file_in_root_dir(self):
        # ARRANGE #
        expected_file = File.empty('file-name.txt')
        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
                with self.subTest(relativity_option_string=rel_opt_conf.option_argument,
                                  phase_is_after_act=phase_is_after_act):
                    instruction_syntax = abs_stx.without_contents(
                        rel_opt_conf.path_abs_stx_of_name(expected_file.name)
                    )
                    # ACT & ASSERT #
                    checker.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        instruction_syntax,
                        Arrangement.phase_agnostic(
                            tcds=TcdsArrangement(
                                pre_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR__PLAIN,
                            ),
                        ),
                        MultiSourceExpectation.phase_agnostic(
                            main_result=IS_SUCCESS,
                            side_effects_on_hds=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.is_empty_sequence,
                            main_side_effects_on_sds=non_hds_dir_contains_exactly(
                                rel_opt_conf.root_dir__non_hds,
                                fs.DirContents([expected_file])),
                        )
                    )

    def test_single_file_in_non_existing_sub_dir(self):
        # ARRANGE #
        sub_dir_name = 'sub-dir'
        expected_file = File.empty('file-name.txt')
        dst_file_name = '/'.join([sub_dir_name, expected_file.name])
        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
                instruction_syntax = abs_stx.without_contents(
                    rel_opt_conf.path_abs_stx_of_name(dst_file_name)
                )
                with self.subTest(relativity_option_string=rel_opt_conf.option_argument,
                                  phase_is_after_act=phase_is_after_act):
                    # ACT & ASSERT #
                    checker.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        instruction_syntax,
                        Arrangement.phase_agnostic(
                            tcds=TcdsArrangement(
                                pre_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR__PLAIN,
                            ),
                        ),
                        MultiSourceExpectation.phase_agnostic(
                            main_result=IS_SUCCESS,
                            side_effects_on_hds=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.is_empty_sequence,
                            main_side_effects_on_sds=non_hds_dir_contains_exactly(
                                rel_opt_conf.root_dir__non_hds,
                                fs.DirContents([fs.Dir(sub_dir_name,
                                                       [expected_file])])),
                        )
                    )

    def test_single_file_in_existing_sub_dir(self):
        sub_dir_name = 'sub-dir'
        expected_file = File.empty('file-name.txt')
        dst_file_name = '/'.join([sub_dir_name, expected_file.name])
        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
                instruction_syntax = abs_stx.without_contents(
                    rel_opt_conf.path_abs_stx_of_name(dst_file_name)
                )
                with self.subTest(relativity_option_string=rel_opt_conf.option_argument):
                    checker.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        instruction_syntax,
                        Arrangement.phase_agnostic(
                            tcds=TcdsArrangement(
                                pre_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR__PLAIN,
                                non_hds_contents=rel_opt_conf.populator_for_relativity_option_root__non_hds(
                                    fs.DirContents([Dir.empty(sub_dir_name)])
                                ),
                            ),
                        ),
                        MultiSourceExpectation.phase_agnostic(
                            main_result=IS_SUCCESS,
                            side_effects_on_hds=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.is_empty_sequence,
                            main_side_effects_on_sds=non_hds_dir_contains_exactly(
                                rel_opt_conf.root_dir__non_hds,
                                fs.DirContents([fs.Dir(sub_dir_name,
                                                       [expected_file])])),
                        )
                    )


class TestCommonFailingScenariosDueToInvalidDestinationFile(
    common_test_cases.TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        file_contents_cases = [
            NameAndValue(
                'empty file',
                fs_abs_stx.FileContentsEmptyAbsStx()
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            SymbolTable({}))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
