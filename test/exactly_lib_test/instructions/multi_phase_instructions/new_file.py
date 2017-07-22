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
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelNonHomeOptionType
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.relativity_options import conf_rel_any, \
    conf_rel_non_home, default_conf_rel_non_home
from exactly_lib_test.instructions.utils.arg_parse.test_resources import args_with_rel_ops
from exactly_lib_test.section_document.test_resources.parse_source import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_home_dir_contains_exactly
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.parse import single_line_source, remaining_source
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import sds_env_utils
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsActionFromSdsAction
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.sds_env_utils import \
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseWithNoContents),
        unittest.makeSuite(TestFailingParseWithContents),
        unittest.makeSuite(TestSuccessfulScenariosWithNoContents),
        unittest.makeSuite(TestSuccessfulScenariosWithContents),
        unittest.makeSuite(TestParserConsumptionOfSource),
        unittest.makeSuite(TestFailingScenariosDueToAlreadyExistingFiles),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


def is_success() -> asrt.ValueAssertion:
    return asrt.is_none


def is_failure() -> asrt.ValueAssertion:
    return asrt.is_instance(str)


DISALLOWED_RELATIVITIES = [
    RelOptionType.REL_RESULT,
    RelOptionType.REL_HOME,
]

ALLOWED_RELATIVITIES = [
    conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
    conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
    conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
    default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),

]


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
        for relativity in DISALLOWED_RELATIVITIES:
            for following_lines in [[], ['following line']]:
                with self.subTest(relativity=str(relativity),
                                  following_lines=repr(following_lines)):
                    option_conf = conf_rel_any(relativity)
                    source = remaining_source('{rel_opt} file-name'.format(rel_opt=option_conf.option_string),
                                              following_lines)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        _just_parse(source)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _parse_and_get_file_info(single_line_source(arguments))

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = '--rel-act expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _parse_and_get_file_info(single_line_source(arguments))


class TestFailingParseWithContents(unittest.TestCase):
    def test_path_is_mandatory__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option} <<MARKER superfluous ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments,
                                      ['MARKER'])
            _just_parse(source)

    def test_disallowed_relativities(self):
        for relativity in DISALLOWED_RELATIVITIES:
            for following_lines in [[], ['following line']]:
                with self.subTest(relativity=str(relativity),
                                  following_lines=repr(following_lines)):
                    option_conf = conf_rel_any(relativity)
                    source = remaining_source('{rel_opt} file-name <<MARKER'.format(rel_opt=option_conf.option_string),
                                              ['MARKER'] + following_lines)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        _just_parse(source)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument <<MARKER superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments,
                                      ['MARKER'])
            _just_parse(source)

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option}  expected-argument <<MARKER superfluous-argument')
        source = remaining_source(arguments,
                                  ['MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _just_parse(source)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation,
               ):
        parser = sut.EmbryoParser()
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestSuccessfulScenariosWithNoContents(TestCaseBase):
    def test_single_file_in_root_dir(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                file_name = 'file-name.txt'
                expected_file = fs.empty_file(file_name)
                self._check(
                    remaining_source('{relativity_option} {file_name}'.format(
                        relativity_option=rel_opt_conf.option_string,
                        file_name=file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_ACTION,
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                               fs.DirContents([expected_file])),
                    ))

    def test_single_file_in_non_existing_sub_dir(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                sub_dir_name = 'sub-dir'
                expected_file = fs.empty_file('file-name.txt')
                self._check(
                    remaining_source('{relativity_option} {sub_dir}/{file_name}'.format(
                        relativity_option=rel_opt_conf.option_string,
                        sub_dir=sub_dir_name,
                        file_name=expected_file.file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_ACTION,
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(
                            rel_opt_conf.root_dir__non_home,
                            fs.DirContents([fs.Dir(sub_dir_name,
                                                   [expected_file])])),
                    ))

    def test_single_file_in_existing_sub_dir(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                sub_dir_name = 'sub-dir'
                expected_file = fs.empty_file('file-name.txt')
                self._check(
                    remaining_source('{relativity_option} {sub_dir}/{file_name}'.format(
                        relativity_option=rel_opt_conf.option_string,
                        sub_dir=sub_dir_name,
                        file_name=expected_file.file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_ACTION,
                        non_home_contents=rel_opt_conf.populator_for_relativity_option_root__non_home(
                            fs.DirContents([fs.empty_dir(sub_dir_name)])
                        )
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(
                            rel_opt_conf.root_dir__non_home,
                            fs.DirContents([fs.Dir(sub_dir_name,
                                                   [expected_file])])),
                    ))


class TestSuccessfulScenariosWithContents(TestCaseBase):
    def test_accepted_relativity_options_other_than_home(self):
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                self._check(
                    remaining_source(
                        '{rel_opt} {file_name} <<THE_MARKER'.format(rel_opt=rel_opt_conf.option_string,
                                                                    file_name=expected_file.file_name),
                        [here_doc_line,
                         'THE_MARKER']),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_ACTION,
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                               fs.DirContents([expected_file])),
                    ))


class TestParserConsumptionOfSource(TestCaseBase):
    def test_last_line__no_contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name}'.format(file_name=expected_file.file_name),
            ),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_ACTION,
            ),
            Expectation(
                main_result=is_success(),
                source=source_is_at_end,
            ),
        )

    def test_not_last_line__no_contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name}'.format(file_name=expected_file.file_name),
                ['following line']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_ACTION,
            ),
            Expectation(
                main_result=is_success(),
                source=is_at_beginning_of_line(2),
            ),
        )

    def test_last_line__contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name} <<MARKER'.format(file_name=expected_file.file_name),
                ['MARKER']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_ACTION,
            ),
            Expectation(
                main_result=is_success(),
                source=source_is_at_end,
            ),
        )

    def test_not_last_line__contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name} <<MARKER'.format(file_name=expected_file.file_name),
                ['MARKER',
                 'following line']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_ACTION,
            ),
            Expectation(
                main_result=is_success(),
                source=is_at_beginning_of_line(3),
            ),
        )


def _just_parse(source: ParseSource):
    sut.EmbryoParser().parse(source)


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


class TestFailingScenariosDueToAlreadyExistingFiles(TestCaseBase):
    def test_argument_is_existing_file(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                self._check(
                    single_line_source('{relativity_option} existing-file'.format(
                        relativity_option=rel_opt_conf.option_string
                    )),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_ACTION,
                        non_home_contents=rel_opt_conf.populator_for_relativity_option_root__non_home(
                            fs.DirContents([
                                fs.empty_file('existing-file')
                            ]))),
                    Expectation(
                        main_result=is_failure(),
                    ))

    def test_argument_is_existing_dir(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                self._check(
                    single_line_source('{relativity_option} existing-dir'.format(
                        relativity_option=rel_opt_conf.option_string
                    )),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_ACTION,
                        non_home_contents=rel_opt_conf.populator_for_relativity_option_root__non_home(
                            fs.DirContents([
                                fs.empty_dir('existing-dir')
                            ]))),
                    Expectation(
                        main_result=is_failure(),
                    ))

    def test_argument_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                self._check(
                    single_line_source('{rel_opt} existing-directory/existing-file/directory/file-name.txt'.format(
                        rel_opt=rel_opt_conf.option_string
                    )),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_ACTION,
                        non_home_contents=rel_opt_conf.populator_for_relativity_option_root__non_home(
                            fs.DirContents([
                                fs.Dir('existing-directory', [
                                    fs.empty_file('existing-file')
                                ])
                            ]))),
                    Expectation(
                        main_result=is_failure(),
                    ))


SETUP_CWD_ACTION = HomeAndSdsActionFromSdsAction(
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
