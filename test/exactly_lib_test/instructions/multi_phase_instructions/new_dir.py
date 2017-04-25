import os
import pathlib
import unittest

from exactly_lib.instructions.multi_phase_instructions import new_dir as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.relativity_options import \
    RelativityOptionConfigurationForRelSds, RelativityOptionConfigurationForRelAct, \
    RelativityOptionConfigurationForRelTmp
from exactly_lib_test.instructions.utils.arg_parse.test_resources import args_with_rel_ops
from exactly_lib_test.test_case_file_structure.test_resources.concrete_path_part import equals_path_part_string
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator, sds_test
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    SubDirOfSdsContainsExactly
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import cwd_contents, SdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_test import Arrangement, Expectation
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import SdsAction
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as va

_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD = 'cwd-dir'


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        arguments = ''
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(arguments)

    def test_fail_when_superfluous_arguments(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(arguments)

    def test_rel_result_option_is_not_allowed(self):
        arguments = args_with_rel_ops('{rel_result_option} file')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(arguments)

    def test_strip_trailing_space(self):
        arguments = '  expected-argument  '
        result = sut.parse(arguments)
        symbols = empty_symbol_table()
        file_ref = result.resolve(symbols)
        equals_path_part_string('expected-argument').apply_with_message(self,
                                                                        file_ref.path_suffix(),
                                                                        'path_suffix')

    def test_success_when_correct_number_of_arguments(self):
        arguments = 'expected-argument'
        result = sut.parse(arguments)
        symbols = empty_symbol_table()
        file_ref = result.resolve(symbols)
        equals_path_part_string('expected-argument').apply_with_message(self,
                                                                        file_ref.path_suffix(),
                                                                        'path_suffix')

    def test_success_when_correct_number_of_arguments__escaped(self):
        arguments = '"expected argument"'
        result = sut.parse(arguments)
        symbols = empty_symbol_table()
        file_ref = result.resolve(symbols)
        equals_path_part_string('expected argument').apply_with_message(self,
                                                                        file_ref.path_suffix(),
                                                                        'path_suffix')


class ParseAndMkDirAction(SdsAction):
    def __init__(self,
                 arguments: str):
        self.arguments = arguments

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        destination_path = sut.parse(self.arguments)
        return sut.make_dir_in_current_dir(environment, destination_path)


class TestCaseForCheckOfArgumentBase(sds_test.TestCaseBase):
    def _check_argument(self,
                        arguments: str,
                        arrangement: Arrangement,
                        expectation: Expectation):
        action = ParseAndMkDirAction(arguments)
        self._check(action,
                    arrangement,
                    expectation)


def is_success() -> va.ValueAssertion:
    return va.ValueIsNone()


def is_failure() -> va.ValueAssertion:
    return va.ValueIsNotNone()


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


class RelativityOptionConfigurationForDefaultRelativity(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__('')

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path().cwd()

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return cwd_contents(contents)


RELATIVITY_OPTIONS = [
    RelativityOptionConfigurationForDefaultRelativity(),
    RelativityOptionConfigurationForRelAct(),
    RelativityOptionConfigurationForRelTmp(),
]


def suite_for_relativity_options() -> unittest.TestSuite:
    return unittest.TestSuite([suite_for_relativity_option(relativity_option)
                               for relativity_option in RELATIVITY_OPTIONS])


def suite_for_relativity_option(relativity_option: RelativityOptionConfigurationForRelSds) -> unittest.TestSuite:
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
            arrangement_with_sub_dir_of_act_as_cwd(),
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
            arrangement_with_sub_dir_of_act_as_cwd(),
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
            arrangement_with_sub_dir_of_act_as_cwd(
                sds_contents_before=self.relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([
                        empty_dir('existing-directory')
                    ]))),
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
            arrangement_with_sub_dir_of_act_as_cwd(
                sds_contents_before=self.relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([
                        Dir('first-component', [
                            empty_dir('second-component')
                        ])]))),
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
            arrangement_with_sub_dir_of_act_as_cwd(
                sds_contents_before=self.relativity_option.populator_for_relativity_option_root__sds(
                    DirContents([
                        Dir('first-component-that-exists', [
                            empty_dir('second-component')])
                    ]))),
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
                             arrangement_with_sub_dir_of_act_as_cwd(
                                 sds_contents_before=cwd_contents(DirContents([
                                     empty_file('file')
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))

    def test_argument_exists_as_non_directory__multiple_path_components(self):
        self._check_argument('existing-dir/existing-file',
                             arrangement_with_sub_dir_of_act_as_cwd(
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
                             arrangement_with_sub_dir_of_act_as_cwd(
                                 sds_contents_before=cwd_contents(DirContents([
                                     Dir('existing-dir', [
                                         empty_file('existing-file')
                                     ])
                                 ]))),
                             Expectation(
                                 expected_action_result=is_failure(),
                             ))


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestFailingScenarios),
        suite_for_relativity_options(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


def arrangement_with_sub_dir_of_act_as_cwd(
        sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty()) -> Arrangement:
    return Arrangement(sds_contents_before=sds_contents_before,
                       pre_contents_population_action=SETUP_CWD_ACTION)


class MkDirIfNotExistsAndChangeToIt(SdsAction):
    def __init__(self, sds_2_dir_path):
        self.sds_2_dir_path = sds_2_dir_path

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        dir_path = self.sds_2_dir_path(environment.sds)
        dir_path.mkdir(parents=True, exist_ok=True)
        os.chdir(str(dir_path))


def mk_sub_dir_of_act_and_change_to_it(sub_dir_name: str) -> SdsAction:
    return MkDirIfNotExistsAndChangeToIt(lambda sds: sds.act_dir / sub_dir_name)


SETUP_CWD_ACTION = mk_sub_dir_of_act_and_change_to_it(_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
