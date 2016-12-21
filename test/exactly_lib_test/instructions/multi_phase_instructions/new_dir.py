import pathlib
import unittest

from exactly_lib.instructions.multi_phase_instructions import new_dir as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources.file_contents.relativity_options import \
    RelativityOptionConfigurationForRelSdsBase, RelativityOptionConfigurationForRelAct, \
    RelativityOptionConfigurationForRelTmp
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.utils.arg_parse.test_resources import args_with_rel_ops
from exactly_lib_test.test_resources.execution import sds_populator
from exactly_lib_test.test_resources.execution import sds_test
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, cwd_contents, SdsPopulator
from exactly_lib_test.test_resources.execution.sds_test import Arrangement, Expectation
from exactly_lib_test.test_resources.execution.utils import SdsAction, mk_sub_dir_of_act_and_change_to_it
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions.sds_contents_check import cwd_contains_exactly, \
    SubDirOfSdsContainsExactly

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
        self.assertEqual('expected-argument',
                         result)

    def test_success_when_correct_number_of_arguments(self):
        arguments = 'expected-argument'
        result = sut.parse(arguments)
        self.assertEqual('expected-argument',
                         result)

    def test_success_when_correct_number_of_arguments__escaped(self):
        arguments = '"expected argument"'
        result = sut.parse(arguments)
        self.assertEqual('expected argument',
                         result)


class ParseAndMkDirAction(SdsAction):
    def __init__(self,
                 arguments: str):
        self.arguments = arguments

    def apply(self, sds: SandboxDirectoryStructure):
        directory_argument = sut.parse(self.arguments)
        return sut.make_dir_in_current_dir(directory_argument)


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
    def __init__(self, relativity_option: RelativityOptionConfigurationForRelSdsBase):
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


class RelativityOptionConfigurationForDefaultRelativity(RelativityOptionConfigurationForRelSdsBase):
    def __init__(self):
        super().__init__('')

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path().cwd()

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return cwd_contents(contents)


def suite_for_relativity_options() -> unittest.TestSuite:
    _relativity_options = [
        RelativityOptionConfigurationForDefaultRelativity(),
        RelativityOptionConfigurationForRelAct(),
        RelativityOptionConfigurationForRelTmp(),
    ]

    return unittest.TestSuite([suite_for_relativity_option(relativity_option)
                               for relativity_option in _relativity_options])


def suite_for_relativity_option(relativity_option: RelativityOptionConfigurationForRelSdsBase) -> unittest.TestSuite:
    test_cases = [
        test_creation_of_directory_with_single_path_component,
        test_creation_of_directory_with_multiple_path_components,
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
        self._check_argument_with_relativity_option('{relativity_option} first-component/second-component',
                                                    arrangement_with_sub_dir_of_act_as_cwd(),
                                                    Expectation(expected_action_result=is_success(),
                                                                expected_sds_contents_after=cwd_contains_exactly(
                                                                    DirContents([
                                                                        Dir('first-component', [
                                                                            empty_dir('second-component')
                                                                        ])
                                                                    ]))
                                                                ))


class TestSuccessfulScenariosWithExistingDirectories(TestCaseForCheckOfArgumentBase):
    def test_whole_argument_exists_as_directory__single_path_component(self):
        self._check_argument('existing-directory',
                             arrangement_with_sub_dir_of_act_as_cwd(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     empty_dir('existing-directory')
                                 ]))),
                             Expectation(
                                 expected_action_result=is_success(),
                                 expected_sds_contents_after=cwd_contains_exactly(DirContents([
                                     empty_dir('existing-directory')
                                 ]))
                             ))

    def test_whole_argument_exists_as_directory__multiple_path_components(self):
        self._check_argument('first-component/second-component',
                             arrangement_with_sub_dir_of_act_as_cwd(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     Dir('first-component', [
                                         empty_dir('second-component')
                                     ])]))),
                             Expectation(
                                 expected_action_result=is_success(),
                                 expected_sds_contents_after=cwd_contains_exactly(DirContents([
                                     Dir('first-component', [
                                         empty_dir('second-component')
                                     ])
                                 ]))
                             ))

    def test_initial_component_of_argument_exists_as_directory__multiple_path_components(self):
        self._check_argument('first-component-that-exists/second-component',
                             arrangement_with_sub_dir_of_act_as_cwd(
                                 sds_contents_before=act_dir_contents(DirContents([
                                     Dir('first-component-that-exists', [
                                         empty_dir('second-component')])
                                 ]))),
                             Expectation(
                                 expected_action_result=is_success(),
                                 expected_sds_contents_after=cwd_contains_exactly(DirContents([
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
        unittest.makeSuite(TestSuccessfulScenariosWithExistingDirectories),
        unittest.makeSuite(TestFailingScenarios),
        suite_for_relativity_options(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


def arrangement_with_sub_dir_of_act_as_cwd(
        sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty()) -> Arrangement:
    return Arrangement(sds_contents_before=sds_contents_before,
                       pre_contents_population_action=_SETUP_CWD_ACTION)


_SETUP_CWD_ACTION = mk_sub_dir_of_act_and_change_to_it(_SUB_DIR_OF_ACT_DIR_THAT_IS_CWD)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
