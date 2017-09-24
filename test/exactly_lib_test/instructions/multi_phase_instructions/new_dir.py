import unittest

from exactly_lib.instructions.multi_phase_instructions import new_dir as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    SubDirOfSdsContainsExactly
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import cwd_contents
from exactly_lib_test.test_case_utils.parse.test_resources.relativity_arguments import args_with_rel_ops
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_case_utils.test_resources.relativity_options import \
    RelativityOptionConfigurationForRelSds, RelativityOptionConfigurationForRelNonHome
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import sds_test
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.sds_env_utils import SdsAction, \
    MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.sds_test import Arrangement, Expectation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.path_part_assertions import equals_path_part_string


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestFailingScenarios),
        suite_for_relativity_options(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def _parse_arguments(self, arguments: str) -> sut.TheInstructionEmbryo:
        return sut.EmbryoParser().parse(remaining_source(arguments))

    def test_fail_when_there_is_no_arguments(self):
        arguments = ''
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._parse_arguments(arguments)

    def test_fail_when_superfluous_arguments(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._parse_arguments(arguments)

    def test_rel_result_option_is_not_allowed(self):
        arguments = args_with_rel_ops('{rel_result_option} file')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._parse_arguments(arguments)

    def test_strip_trailing_space(self):
        arguments = '  expected-argument  '
        instruction_embryo = self._parse_arguments(arguments)
        symbols = empty_symbol_table()
        file_ref = instruction_embryo.dir_path_resolver.resolve(symbols)
        equals_path_part_string('expected-argument').apply_with_message(self,
                                                                        file_ref.path_suffix(),
                                                                        'path_suffix')

    def test_success_when_correct_number_of_arguments(self):
        arguments = 'expected-argument'
        instruction_embryo = self._parse_arguments(arguments)
        symbols = empty_symbol_table()
        file_ref = instruction_embryo.dir_path_resolver.resolve(symbols)
        equals_path_part_string('expected-argument').apply_with_message(self,
                                                                        file_ref.path_suffix(),
                                                                        'path_suffix')

    def test_success_when_correct_number_of_arguments__escaped(self):
        arguments = '"expected argument"'
        instruction_embryo = self._parse_arguments(arguments)
        symbols = empty_symbol_table()
        file_ref = instruction_embryo.dir_path_resolver.resolve(symbols)
        equals_path_part_string('expected argument').apply_with_message(self,
                                                                        file_ref.path_suffix(),
                                                                        'path_suffix')


class ParseAndMkDirAction(SdsAction):
    parser = sut.EmbryoParser()

    def __init__(self, arguments: str):
        self.arguments = arguments

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        instruction_embryo = self.parser.parse(remaining_source(self.arguments))
        assert isinstance(instruction_embryo, sut.TheInstructionEmbryo)
        return instruction_embryo.custom_main(environment)


class TestCaseForCheckOfArgumentBase(sds_test.TestCaseBase):
    def _check_argument(self,
                        arguments: str,
                        arrangement: Arrangement,
                        expectation: Expectation):
        action = ParseAndMkDirAction(arguments)
        self._check(action,
                    arrangement,
                    expectation)


def is_success() -> asrt.ValueAssertion:
    return asrt.ValueIsNone()


def is_failure() -> asrt.ValueAssertion:
    return asrt.ValueIsNotNone()


class TestWithRelativityOptionBase(TestCaseForCheckOfArgumentBase):
    def __init__(self, relativity_option: RelativityOptionConfigurationForRelSds):
        super().__init__()
        self.relativity_option = relativity_option

    def shortDescription(self):
        return '{}\n / {}'.format(type(self),
                                  type(self.relativity_option))

    def _check_argument_with_relativity_option(self,
                                               arguments: str,
                                               arrangement: Arrangement,
                                               expectation: Expectation):
        argument_with_rel_option_replaced = arguments.format(relativity_option=self.relativity_option.option_string)
        action = ParseAndMkDirAction(argument_with_rel_option_replaced)
        self._check(action,
                    arrangement,
                    expectation)

    def runTest(self):
        raise NotImplementedError()


RELATIVITY_OPTIONS = [
    rel_opt.default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
    rel_opt.conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
    rel_opt.conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
    rel_opt.symbol_conf_rel_non_home(RelNonHomeOptionType.REL_TMP,
                                     'DIR_PATH_SYMBOL',
                                     sut.RELATIVITY_VARIANTS.options.accepted_relativity_variants),
]


def suite_for_relativity_options() -> unittest.TestSuite:
    return unittest.TestSuite([suite_for_relativity_option(relativity_option)
                               for relativity_option in RELATIVITY_OPTIONS])


def suite_for_relativity_option(relativity_option: RelativityOptionConfigurationForRelNonHome) -> unittest.TestSuite:
    test_cases = [
        test_creation_of_directory_with_single_path_component,
        test_creation_of_directory_with_multiple_path_components,
        test_whole_argument_exists_as_directory__single_path_component,
        test_whole_argument_exists_as_directory__multiple_path_components,
        test_initial_component_of_argument_exists_as_directory__multiple_path_components,
    ]
    return unittest.TestSuite([tc(relativity_option) for tc in test_cases])


class test_creation_of_directory_with_single_path_component(TestWithRelativityOptionBase):
    def runTest(self):
        self._check_argument_with_relativity_option(
            '{relativity_option} dir-that-should-be-constructed',
            arrangement_with_cwd_as_none_of_the_relativity_roots(
                symbols=self.relativity_option.symbols.in_arrangement()),
            Expectation(expected_action_result=is_success(),
                        expected_sds_contents_after=SubDirOfSdsContainsExactly(
                            self.relativity_option.root_dir__sds,
                            DirContents([
                                empty_dir('dir-that-should-be-constructed')
                            ]))
                        ))


class test_creation_of_directory_with_multiple_path_components(TestWithRelativityOptionBase):
    def runTest(self):
        self._check_argument_with_relativity_option(
            '{relativity_option} first-component/second-component',
            arrangement_with_cwd_as_none_of_the_relativity_roots(
                symbols=self.relativity_option.symbols.in_arrangement()),
            Expectation(expected_action_result=is_success(),
                        expected_sds_contents_after=SubDirOfSdsContainsExactly(
                            self.relativity_option.root_dir__sds,
                            DirContents([
                                Dir('first-component', [
                                    empty_dir('second-component')
                                ])
                            ]))
                        ))


class test_whole_argument_exists_as_directory__single_path_component(TestWithRelativityOptionBase):
    def runTest(self):
        self._check_argument_with_relativity_option(
            '{relativity_option} existing-directory',
            arrangement_with_cwd_as_none_of_the_relativity_roots(
                sds_contents_before=self.relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([
                        empty_dir('existing-directory')
                    ])),
                symbols=self.relativity_option.symbols.in_arrangement(),
            ),
            Expectation(
                expected_action_result=is_success(),
                expected_sds_contents_after=SubDirOfSdsContainsExactly(
                    self.relativity_option.root_dir__sds,
                    DirContents([
                        empty_dir('existing-directory')
                    ]))
            ))


class test_whole_argument_exists_as_directory__multiple_path_components(TestWithRelativityOptionBase):
    def runTest(self):
        self._check_argument_with_relativity_option(
            '{relativity_option} first-component/second-component',
            arrangement_with_cwd_as_none_of_the_relativity_roots(
                sds_contents_before=self.relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([
                        Dir('first-component', [
                            empty_dir('second-component')
                        ])])),
                symbols=self.relativity_option.symbols.in_arrangement(),
            ),
            Expectation(
                expected_action_result=is_success(),
                expected_sds_contents_after=SubDirOfSdsContainsExactly(
                    self.relativity_option.root_dir__sds,
                    DirContents([
                        Dir('first-component', [
                            empty_dir('second-component')
                        ])
                    ]))
            ))


class test_initial_component_of_argument_exists_as_directory__multiple_path_components(TestWithRelativityOptionBase):
    def runTest(self):
        self._check_argument_with_relativity_option(
            '{relativity_option} first-component-that-exists/second-component',
            arrangement_with_cwd_as_none_of_the_relativity_roots(
                sds_contents_before=self.relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([
                        Dir('first-component-that-exists', [
                            empty_dir('second-component')])
                    ])),
                symbols=self.relativity_option.symbols.in_arrangement(),
            ),
            Expectation(
                expected_action_result=is_success(),
                expected_sds_contents_after=SubDirOfSdsContainsExactly(
                    self.relativity_option.root_dir__sds,
                    DirContents([
                        Dir('first-component-that-exists', [
                            empty_dir('second-component')
                        ])
                    ]))
            ))


class TestFailingScenarios(TestCaseForCheckOfArgumentBase):
    def test_argument_exists_as_non_directory__single_path_component(self):
        self._check_argument('file',
                             arrangement_with_cwd_as_none_of_the_relativity_roots(
                                 sds_contents_before=cwd_contents(DirContents([
                                     empty_file('file')
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))

    def test_argument_exists_as_non_directory__multiple_path_components(self):
        self._check_argument('existing-dir/existing-file',
                             arrangement_with_cwd_as_none_of_the_relativity_roots(
                                 sds_contents_before=cwd_contents(DirContents([
                                     Dir('existing-dir', [
                                         empty_file('existing-file')
                                     ])
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))

    def test_multi_path_component_with_middle_component_is_a_file(self):
        self._check_argument('existing-dir/existing-file/leaf-dir',
                             arrangement_with_cwd_as_none_of_the_relativity_roots(
                                 sds_contents_before=cwd_contents(DirContents([
                                     Dir('existing-dir', [
                                         empty_file('existing-file')
                                     ])
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))


def arrangement_with_cwd_as_none_of_the_relativity_roots(
        sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty(),
        symbols: SymbolTable = None) -> Arrangement:
    return Arrangement(pre_contents_population_action=SETUP_CWD_ACTION,
                       sds_contents_before=sds_contents_before,
                       symbols=symbols)


SETUP_CWD_ACTION = MkDirAndChangeToItInsideOfSdsButOutsideOfAnyOfTheRelativityOptionDirs()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
