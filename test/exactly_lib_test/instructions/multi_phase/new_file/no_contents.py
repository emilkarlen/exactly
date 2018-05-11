import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    TestCaseBase
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.utils import \
    DISALLOWED_RELATIVITIES, ALLOWED_DST_FILE_RELATIVITIES, IS_SUCCESS, just_parse
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.utils.parse.parse_file_maker.test_resources.arguments import \
    empty_file_contents_arguments
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.test_case_file_structure.test_resources.format_rel_option import format_rel_options
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_home_dir_contains_exactly
from exactly_lib_test.test_case_utils.parse.test_resources.relativity_arguments import args_with_rel_ops
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseWithNoContents),
        unittest.makeSuite(TestSuccessfulScenariosWithNoContents),
        unittest.makeSuite(TestParserConsumptionOfSource),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestFailingParseWithNoContents(unittest.TestCase):
    def test_path_is_mandatory__without_option(self):
        arguments = ''
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(single_line_source(arguments))

    def test_path_is_mandatory__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option}')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(single_line_source(arguments))

    def test_disallowed_relativities(self):
        for relativity in DISALLOWED_RELATIVITIES:
            for following_lines in [[], ['following line']]:
                with self.subTest(relativity=str(relativity),
                                  following_lines=repr(following_lines)):
                    option_conf = conf_rel_any(relativity)
                    source = remaining_source('{rel_opt} file-name'.format(rel_opt=option_conf.option_argument),
                                              following_lines)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        just_parse(source)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(single_line_source(arguments))

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = format_rel_options('{rel_act} expected-argument superfluous-argument')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            just_parse(single_line_source(arguments))


class TestSuccessfulScenariosWithNoContents(TestCaseBase):
    def test_single_file_in_root_dir(self):
        for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_argument):
                file_name = 'file-name.txt'
                expected_file = fs.empty_file(file_name)
                self._check(
                    remaining_source('{relativity_option} {file_name}'.format(
                        relativity_option=rel_opt_conf.option_argument,
                        file_name=file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_sequence,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                               fs.DirContents([expected_file])),
                    ))

    def test_single_file_in_non_existing_sub_dir(self):
        for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_argument):
                sub_dir_name = 'sub-dir'
                expected_file = fs.empty_file('file-name.txt')
                self._check(
                    remaining_source('{relativity_option} {sub_dir}/{file_name}'.format(
                        relativity_option=rel_opt_conf.option_argument,
                        sub_dir=sub_dir_name,
                        file_name=expected_file.file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_sequence,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(
                            rel_opt_conf.root_dir__non_home,
                            fs.DirContents([fs.Dir(sub_dir_name,
                                                   [expected_file])])),
                    ))

    def test_single_file_in_existing_sub_dir(self):
        for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_argument):
                sub_dir_name = 'sub-dir'
                expected_file = fs.empty_file('file-name.txt')
                self._check(
                    remaining_source('{relativity_option} {sub_dir}/{file_name}'.format(
                        relativity_option=rel_opt_conf.option_argument,
                        sub_dir=sub_dir_name,
                        file_name=expected_file.file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                        non_home_contents=rel_opt_conf.populator_for_relativity_option_root__non_home(
                            fs.DirContents([fs.empty_dir(sub_dir_name)])
                        )
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_sequence,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(
                            rel_opt_conf.root_dir__non_home,
                            fs.DirContents([fs.Dir(sub_dir_name,
                                                   [expected_file])])),
                    ))


class TestParserConsumptionOfSource(TestCaseBase):
    def test_last_line(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name}'.format(file_name=expected_file.file_name),
            ),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
            ),
            Expectation(
                main_result=IS_SUCCESS,
                source=source_is_at_end,
            ),
        )

    def test_not_last_line(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name}'.format(file_name=expected_file.file_name),
                ['following line']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
            ),
            Expectation(
                main_result=IS_SUCCESS,
                source=is_at_beginning_of_line(2),
            ),
        )


class TestCommonFailingScenariosDueToInvalidDestinationFile(TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        file_contents_cases = [
            NameAndValue(
                'empty file',
                empty_file_contents_arguments()
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            SymbolTable({}))
