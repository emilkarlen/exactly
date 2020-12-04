import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import abstract_syntax as abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import common_test_cases
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import integration_check
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.abstract_syntax import \
    ImplicitlyEmptyContentsVariantAbsStx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.defs import DISALLOWED_DST_RELATIVITIES, \
    ALLOWED_DST_FILE_RELATIVITIES
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.parse_check import just_parse, \
    check_invalid_syntax, check_invalid_syntax__abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.utils import \
    IS_SUCCESS
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.impls.types.parse.test_resources.relativity_arguments import args_with_rel_ops
from exactly_lib_test.impls.types.test_resources.relativity_options import conf_rel_any
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source
from exactly_lib_test.tcfs.test_resources.format_rel_option import format_rel_options
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File, Dir
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSuccessfulScenariosWithNoContents),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestFailingParse(unittest.TestCase):
    def test_path_is_mandatory__without_option(self):
        check_invalid_syntax(self, single_line_source(''))

    def test_path_is_mandatory__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option}')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(single_line_source(arguments))

    def test_disallowed_relativities(self):
        for relativity in DISALLOWED_DST_RELATIVITIES:
            with self.subTest(relativity=str(relativity)):
                relativity_conf = conf_rel_any(relativity)
                instruction_syntax = abs_stx.without_contents(relativity_conf.path_abs_stx_of_name('file-name'))
                check_invalid_syntax__abs_stx(self, instruction_syntax)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(single_line_source(arguments))

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = format_rel_options('{rel_act} expected-argument superfluous-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(single_line_source(arguments))


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
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        ),
                        Expectation(
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
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        ),
                        Expectation(
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
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                            non_hds_contents=rel_opt_conf.populator_for_relativity_option_root__non_hds(
                                fs.DirContents([Dir.empty(sub_dir_name)])
                            )
                        ),
                        Expectation(
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
                ImplicitlyEmptyContentsVariantAbsStx()
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            SymbolTable({}))
