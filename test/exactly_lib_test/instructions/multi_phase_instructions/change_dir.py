import os
import pathlib
import unittest

from exactly_lib.instructions.multi_phase_instructions import change_dir as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.file_ref_relativity import RelOptionType
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.execution.sds_check import sds_test
from exactly_lib_test.test_resources.execution.sds_check import sds_utils
from exactly_lib_test.test_resources.execution.sds_check.sds_populator import act_dir_contents, tmp_user_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueIsNotNone
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueIsNone


class TestParseSet(unittest.TestCase):
    def test_no_argument_should_denote_act_dir(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '--rel-act'
                actual = sut.parse(arguments, is_after_act_phase=is_after_act_phase)
                self.assertIs(RelOptionType.REL_ACT,
                              actual.destination_type(empty_symbol_table()))

    def test_no_relativity_option_should_use_default_option(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = 'single-argument'
                actual = sut.parse(arguments, is_after_act_phase=is_after_act_phase)
                self.assertIs(RelOptionType.REL_CWD,
                              actual.destination_type(empty_symbol_table()))
                self.assertEqual('single-argument',
                                 str(actual.path_argument))

    def test_no_arguments_is_rel_default_option(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = ''
                actual = sut.parse(arguments, is_after_act_phase=is_after_act_phase)
                self.assertIs(RelOptionType.REL_CWD,
                              actual.destination_type(empty_symbol_table()))
                self.assertEqual(str(pathlib.PurePath()),
                                 str(actual.path_argument))

    def test_fail_when_superfluous_arguments(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = 'expected-argument superfluous-argument'
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse(arguments, is_after_act_phase=is_after_act_phase)

    def test_strip_trailing_space(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '  expected-argument  '
                actual = sut.parse(arguments, is_after_act_phase=is_after_act_phase)
                self.assertIs(RelOptionType.REL_CWD,
                              actual.destination_type(empty_symbol_table()))
                self.assertEqual('expected-argument',
                                 str(actual.path_argument))

    def test_success_when_correct_number_of_arguments__escaped(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '"expected argument"'
                actual = sut.parse(arguments, is_after_act_phase=is_after_act_phase)
                self.assertIs(RelOptionType.REL_CWD,
                              actual.destination_type(empty_symbol_table()))
                self.assertEqual('expected argument',
                                 str(actual.path_argument))

    def test_rel_tmp_without_argument(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '--rel-tmp'
                actual = sut.parse(arguments, is_after_act_phase=is_after_act_phase)
                self.assertIs(RelOptionType.REL_TMP,
                              actual.destination_type(empty_symbol_table()))
                self.assertEqual(str(pathlib.PurePosixPath()),
                                 str(actual.path_argument))

    def test_rel_tmp_with_argument(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '--rel-tmp subdir'
                actual = sut.parse(arguments, is_after_act_phase=is_after_act_phase)
                self.assertIs(RelOptionType.REL_TMP,
                              actual.destination_type(empty_symbol_table()))
                self.assertEqual('subdir',
                                 str(actual.path_argument))

    def test_rel_tmp_with_superfluous_argument(self):
        arguments = '--rel-tmp subdir superfluous'
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse(arguments, is_after_act_phase=is_after_act_phase)

    def test_rel_result_should_not_be_available_pre_act_phase(self):
        arguments = '--rel-result'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parse(arguments, is_after_act_phase=False)


class ParseAndChangeDirAction(sds_utils.SdsAction):
    def __init__(self,
                 arguments: str,
                 is_after_act_phase: bool):
        self.arguments = arguments
        self.is_after_act_phase = is_after_act_phase

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        destination_directory = sut.parse(self.arguments, self.is_after_act_phase)
        return sut.change_dir(destination_directory, environment)


class TestCaseBase(sds_test.TestCaseBase):
    def _check_argument(self,
                        arguments: str,
                        arrangement: sds_test.Arrangement,
                        expectation: sds_test.Expectation):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                self._check_argument_for_single_case(is_after_act_phase,
                                                     arguments,
                                                     arrangement,
                                                     expectation)

    def _check_argument_for_single_case(self,
                                        is_after_act_phase: bool,
                                        arguments: str,
                                        arrangement: sds_test.Arrangement,
                                        expectation: sds_test.Expectation):
        action = ParseAndChangeDirAction(arguments, is_after_act_phase)
        self._check(action,
                    arrangement,
                    expectation)


def is_success() -> ValueAssertion:
    return ValueIsNone()


def is_failure() -> ValueAssertion:
    return ValueIsNotNone()


class ChangeDirTo(sds_utils.SdsAction):
    def __init__(self, sds2dir_fun):
        self.sds2dir_fun = sds2dir_fun

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        os.chdir(str(self.sds2dir_fun(environment.sds)))


class CwdIsActDir(sds_test.PostActionCheck):
    def apply(self, put: unittest.TestCase, sds: SandboxDirectoryStructure):
        put.assertEqual(str(sds.act_dir),
                        os.getcwd(),
                        'Current Working Directory')


class CwdIsSubDirOfActDir(sds_test.PostActionCheck):
    def __init__(self, sub_dir_name: str):
        self.sub_dir_name = sub_dir_name

    def apply(self, put: unittest.TestCase, sds: SandboxDirectoryStructure):
        put.assertEqual(str(sds.act_dir / self.sub_dir_name),
                        os.getcwd(),
                        'Current Working Directory')


class CwdIs(sds_test.PostActionCheck):
    def __init__(self, sds2dir_fun):
        self.sds2dir_fun = sds2dir_fun

    def apply(self, put: unittest.TestCase, sds: SandboxDirectoryStructure):
        put.assertEqual(str(self.sds2dir_fun(sds)),
                        os.getcwd(),
                        'Current Working Directory')


class TestSuccessfulScenarios(TestCaseBase):
    def test_relative_argument_should_change_dir_relative_to_cwd__from_act_dir(self):
        self._check_argument('existing-dir',
                             sds_test.Arrangement(sds_contents_before=act_dir_contents(DirContents([
                                 empty_dir('existing-dir')
                             ]))),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir / 'existing-dir')
                                                  ))

    def test_relative_argument_should_change_dir_relative_to_cwd__from_tmp_dir(self):
        self._check_argument('sub1/sub2',
                             sds_test.Arrangement(
                                 sds_contents_before=tmp_user_dir_contents(DirContents([
                                     Dir('sub1', [
                                         empty_dir('sub2')
                                     ])
                                 ])),
                                 pre_action_action=ChangeDirTo(lambda sds: sds.tmp.user_dir)),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(
                                                      lambda sds: sds.tmp.user_dir / 'sub1' / 'sub2')
                                                  ))

    def test_no_argument_should_have_no_effect(self):
        self._check_argument('',
                             sds_test.Arrangement(pre_action_action=ChangeDirTo(lambda sds: sds.act_dir / 'sub-dir'),
                                                  sds_contents_before=act_dir_contents(DirContents([
                                                      empty_dir('sub-dir')
                                                  ]))
                                                  ),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir / 'sub-dir')
                                                  ))

    def test_single_dot_argument_should_have_no_effect(self):
        self._check_argument('.',
                             sds_test.Arrangement(pre_action_action=ChangeDirTo(lambda sds: sds.act_dir / 'sub-dir'),
                                                  sds_contents_before=act_dir_contents(DirContents([
                                                      empty_dir('sub-dir')
                                                  ]))
                                                  ),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir / 'sub-dir')
                                                  ))

    def test_act_root_option_should_change_to_act_dir(self):
        self._check_argument('--rel-act',
                             sds_test.Arrangement(pre_action_action=ChangeDirTo(lambda sds: sds.root_dir)),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir)
                                                  ))

    def test_act_root_option_should_change_to_act_dir__dot_arg(self):
        self._check_argument('--rel-act .',
                             sds_test.Arrangement(pre_action_action=ChangeDirTo(lambda sds: sds.root_dir)),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir)
                                                  ))

    def test_relative_tmp__without_argument(self):
        self._check_argument('--rel-tmp',
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.tmp.user_dir)
                                                  ))

    def test_relative_tmp__without_argument__dot_arg(self):
        self._check_argument('--rel-tmp .',
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.tmp.user_dir)
                                                  ))

    def test_relative_tmp__with_argument(self):
        self._check_argument('--rel-tmp sub1/sub2',
                             sds_test.Arrangement(sds_contents_before=tmp_user_dir_contents(DirContents([
                                 Dir('sub1', [
                                     empty_dir('sub2')
                                 ])
                             ]))),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(
                                                      lambda sds: sds.tmp.user_dir / 'sub1' / 'sub2')
                                                  ))

    def test_relative_result__after_act_phase(self):
        self._check_argument_for_single_case(
            True,
            '--rel-result',
            sds_test.Arrangement(),
            sds_test.Expectation(expected_action_result=is_success(),
                                 post_action_check=CwdIs(lambda sds: sds.result.root_dir)
                                 ))


class TestFailingScenarios(TestCaseBase):
    def test_argument_is_file(self):
        self._check_argument('existing-file',
                             sds_test.Arrangement(sds_contents_before=act_dir_contents(DirContents([
                                 empty_file('existing-file')
                             ]))),
                             sds_test.Expectation(expected_action_result=is_failure()))


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseSet),
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestFailingScenarios),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name',
                                                                            is_after_act_phase=False,
                                                                            is_in_assert_phase=False)),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name',
                                                                            is_after_act_phase=True,
                                                                            is_in_assert_phase=False)),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name',
                                                                            is_after_act_phase=True,
                                                                            is_in_assert_phase=True)),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
