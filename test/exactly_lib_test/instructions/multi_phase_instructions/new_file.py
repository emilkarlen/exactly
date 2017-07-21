import pathlib
import tempfile
import unittest

from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, specific_relative_relativity, \
    RelSdsOptionType
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.relativity_options import conf_rel_sds
from exactly_lib_test.instructions.utils.arg_parse.test_resources import args_with_rel_ops
from exactly_lib_test.test_case_file_structure.test_resources.path_relativity import equals_path_relativity
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly, SubDirOfSdsContainsExactly
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import contents_in
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.parse import argument_list_source, single_line_source, remaining_source
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import sds_test, sds_env_utils
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsActionFromSdsAction
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.sds_env_utils import \
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueIsNone, ValueIsNotNone
from exactly_lib_test.type_system_values.test_resources.concrete_path_part import equals_path_part_string


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseWithNoContents),
        unittest.makeSuite(TestSuccessfulParseWithContents),
        unittest.makeSuite(TestSuccessfulScenariosNoContent),
        unittest.makeSuite(TestSuccessfulScenariosWithContent),
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestParseWithContents),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestFailingParseWithNoContents(unittest.TestCase):
    def test_path_is_mandatory__without_option(self):
        arguments = ''
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _parse_and_get_file_info(single_line_source(arguments))

    def test_path_is_mandatory__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option}')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _parse_and_get_file_info(single_line_source(arguments))

    def test_disallowed_relativities(self):
        cases = [
            args_with_rel_ops('{rel_result_option} file'),
            args_with_rel_ops('{rel_home_option} file'),
        ]
        for arguments in cases:
            with self.subTest(source=arguments):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    _parse_and_get_file_info(single_line_source(arguments))

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _parse_and_get_file_info(single_line_source(arguments))

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = '--rel-act expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _parse_and_get_file_info(single_line_source(arguments))


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: embryo_check.ArrangementWithSds,
               expectation: embryo_check.Expectation,
               ):
        parser = sut.EmbryoParser()
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestSuccessfulParseWithContents(TestCaseBase):
    def test_when_no_option_path_should_be_relative_cwd(self):
        file_name = 'file-name.txt'
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File(file_name, expected_file_contents)
        source = remaining_source('{file_name} <<MARKER'.format(file_name=file_name),
                                  [here_doc_line,
                                   'MARKER'])
        arrangement = embryo_check.ArrangementWithSds(
            pre_contents_population_action=SETUP_CWD_ACTION,
        )
        expectation = embryo_check.Expectation(
            side_effects_on_home=f_asrt.dir_is_empty(),
            main_side_effects_on_sds=SubDirOfSdsContainsExactly(SETUP_CWD_REL_SDS_ACTION.resolve_dir_path,
                                                                fs.DirContents([expected_file])),
        )
        self._check(source, arrangement, expectation)

    def test_explicit_relativity_of_home(self):
        file_name = 'file-name.txt'
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File(file_name, expected_file_contents)
        source = remaining_source(args_with_rel_ops('{rel_cwd_option} {file_name} <<MARKER',
                                                    file_name=file_name),
                                  [here_doc_line,
                                   'MARKER'])
        arrangement = embryo_check.ArrangementWithSds(
            pre_contents_population_action=SETUP_CWD_ACTION,
        )
        expectation = embryo_check.Expectation(
            side_effects_on_home=f_asrt.dir_is_empty(),
            main_side_effects_on_sds=SubDirOfSdsContainsExactly(SETUP_CWD_REL_SDS_ACTION.resolve_dir_path,
                                                                fs.DirContents([expected_file])),
        )
        self._check(source, arrangement, expectation)

    def test_accepted_relativity_options_other_than_home(self):
        file_name = 'a-file-name.txt'
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File(file_name, expected_file_contents)
        accepted_relativity_options = {RelSdsOptionType.REL_ACT,
                                       RelSdsOptionType.REL_TMP}
        for relativity_option in accepted_relativity_options:
            with self.subTest(relativity_option=str(relativity_option)):
                rel_opt_conf = conf_rel_sds(relativity_option)
                source = remaining_source(
                    '{rel_opt} {file_name} <<THE_MARKER'.format(rel_opt=rel_opt_conf.option_string,
                                                                file_name=file_name),
                    [here_doc_line,
                     'THE_MARKER'])
                arrangement = embryo_check.ArrangementWithSds(
                    pre_contents_population_action=SETUP_CWD_ACTION,
                )
                expectation = embryo_check.Expectation(
                    side_effects_on_home=f_asrt.dir_is_empty(),
                    main_side_effects_on_sds=SubDirOfSdsContainsExactly(rel_opt_conf.root_dir__sds,
                                                                        fs.DirContents([expected_file])),
                )
                self._check(source, arrangement, expectation)


class TestParseWithContents(unittest.TestCase):
    def test_fail_when_superfluous_arguments(self):
        source = argument_list_source(['file name', '<<MARKER', 'superfluous argument'],
                                      ['single line',
                                       'MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _parse_and_get_file_info(source)

    def test_single_line(self):
        source = argument_list_source(['file name', '<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        actual = _parse_and_get_file_info(source)
        symbol_table = empty_symbol_table()
        relativity_assertion = equals_path_relativity(specific_relative_relativity(RelOptionType.REL_CWD))
        actual_file_ref = actual.file_ref.resolve(symbol_table)
        relativity_assertion.apply_with_message(self, actual_file_ref.relativity(),
                                                'relativity')
        equals_path_part_string('file name').apply_with_message(self, actual_file_ref.path_suffix(),
                                                                'destination_path/path_suffix')
        self.assertEqual(lines_content(['single line']),
                         actual.contents.resolve(symbol_table).value_when_no_dir_dependencies())
        self.assertFalse(source.has_current_line)

    def test_single_line__with_option(self):
        source = argument_list_source(['--rel-tmp', 'file name', '<<MARKER'],
                                      ['single line',
                                       'MARKER',
                                       'following line'])
        actual = _parse_and_get_file_info(source)
        symbol_table = empty_symbol_table()
        relativity_assertion = equals_path_relativity(specific_relative_relativity(RelOptionType.REL_TMP))
        actual_file_ref = actual.file_ref.resolve(symbol_table)
        relativity_assertion.apply_with_message(self, actual_file_ref.relativity(),
                                                'relativity')
        equals_path_part_string('file name').apply_with_message(self,
                                                                actual_file_ref.path_suffix(),
                                                                'destination_path/path_suffix')
        self.assertEqual(lines_content(['single line']),
                         actual.contents.resolve(symbol_table).value_when_no_dir_dependencies())
        self.assertTrue(source.has_current_line)
        self.assertEqual('following line',
                         source.current_line_text)


def _parse_and_get_file_info(source: ParseSource) -> sut.FileInfo:
    instruction_embryo = sut.EmbryoParser().parse(source)
    return instruction_embryo.file_info


class ParseAndCreateFileAction(sds_env_utils.SdsAction):
    def __init__(self,
                 source: ParseSource):
        self.source = source

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        file_info = _parse_and_get_file_info(self.source)
        with tempfile.TemporaryDirectory(prefix='exactly-testing-') as tmp_file_name:
            home_dir_path = pathlib.Path(tmp_file_name)
            home_and_sds = HomeAndSds(home_dir_path, environment.sds)
            env_pre_or_post_sds = PathResolvingEnvironmentPreOrPostSds(home_and_sds,
                                                                       environment.symbols)
            return sut.create_file(file_info, env_pre_or_post_sds)


class TestCaseBase(sds_test.TestCaseBase):
    def _check_argument(self,
                        source: ParseSource,
                        arrangement: sds_test.Arrangement,
                        expectation: sds_test.Expectation):
        action = ParseAndCreateFileAction(source)
        self._check(action,
                    arrangement,
                    expectation)


def is_success() -> ValueAssertion:
    return ValueIsNone()


def is_failure() -> ValueAssertion:
    return ValueIsNotNone()


class TestSuccessfulScenariosNoContent(TestCaseBase):
    def test_file_relative_cwd(self):
        self._check_argument(single_line_source('file-name.txt'),
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(fs.DirContents([
                                                      fs.empty_file('file-name.txt')
                                                  ])),
                                                  ))

    def test_file_in_sub_dir__sub_dir_exists(self):
        self._check_argument(single_line_source('existing-directory/file-name.txt'),
                             sds_test.Arrangement(sds_contents_before=contents_in(RelSdsOptionType.REL_ACT,
                                                                                  fs.DirContents([
                                                                                      fs.empty_dir('existing-directory')
                                                                                  ]))),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(fs.DirContents([
                                                      fs.Dir('existing-directory', [
                                                          fs.empty_file('file-name.txt')])
                                                  ])),
                                                  ))

    def test_file_in_sub_dir__sub_dir_does_not_exist(self):
        self._check_argument(single_line_source('existing-directory/file-name.txt'),
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(fs.DirContents([
                                                      fs.Dir('existing-directory', [
                                                          fs.empty_file('file-name.txt')])
                                                  ])),
                                                  ))

    def test_file_in_sub_dir__sub_dir_does_not_exist__rel_tmp(self):
        self._check_argument(single_line_source('--rel-tmp existing-directory/file-name.txt'),
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=tmp_user_dir_contains_exactly(
                                                      fs.DirContents([
                                                          fs.Dir('existing-directory', [
                                                              fs.empty_file('file-name.txt')])
                                                      ])),
                                                  ))


class TestSuccessfulScenariosWithContent(TestCaseBase):
    def test_file_relative_cwd(self):
        source = argument_list_source(['file-name.txt', '<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        self._check_argument(source,
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  expected_sds_contents_after=act_dir_contains_exactly(fs.DirContents([
                                                      fs.File('file-name.txt',
                                                              lines_content(['single line']))
                                                  ])),
                                                  ))


class TestFailingScenarios(TestCaseBase):
    def test_argument_is_existing_file(self):
        self._check_argument(single_line_source('existing-file'),
                             sds_test.Arrangement(
                                 sds_contents_before=contents_in(RelSdsOptionType.REL_ACT,
                                                                 fs.DirContents([
                                                                     fs.empty_file('existing-file')
                                                                 ]))),
                             sds_test.Expectation(expected_action_result=is_failure(),
                                                  ))

    def test_argument_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        self._check_argument(single_line_source('existing-directory/existing-file/directory/file-name.txt'),
                             sds_test.Arrangement(sds_contents_before=contents_in(
                                 RelSdsOptionType.REL_ACT,
                                 fs.DirContents([
                                     fs.Dir('existing-directory', [
                                         fs.empty_file('existing-file')
                                     ])
                                 ]))),
                             sds_test.Expectation(expected_action_result=is_failure(),
                                                  ))


SETUP_CWD_REL_SDS_ACTION = MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs()

SETUP_CWD_ACTION = HomeAndSdsActionFromSdsAction(
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
