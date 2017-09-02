import os
import unittest

from exactly_lib.instructions.multi_phase_instructions import change_dir as sut
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsNothing, PathPartAsFixedPath
from exactly_lib.type_system.file_ref import FileRef
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.named_element.symbol.test_resources.concrete_value_assertions import matches_file_ref_resolver
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import contents_in
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import sds_test, sds_env_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueIsNotNone
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueIsNone


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


class TestParseSet(unittest.TestCase):
    def test_no_argument_should_denote_act_dir(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '--rel-act'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(remaining_source(arguments))
                # ASSERT #
                expected_file_ref = _file_ref_of(RelOptionType.REL_ACT)
                assertion = matches_file_ref_resolver(expected_file_ref, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_no_relativity_option_should_use_default_option(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = 'single-argument'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(remaining_source(arguments))
                # ASSERT #
                expected_file_ref = file_refs.of_rel_option(RelOptionType.REL_CWD, PathPartAsFixedPath(arguments))
                assertion = matches_file_ref_resolver(expected_file_ref, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_no_arguments_is_rel_default_option(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = ''
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(remaining_source(arguments))
                # ASSERT #
                expected_file_ref = _file_ref_of(RelOptionType.REL_CWD)
                assertion = matches_file_ref_resolver(expected_file_ref, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_fail_when_superfluous_arguments(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = 'expected-argument superfluous-argument'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT & ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(remaining_source(arguments))

    def test_strip_trailing_space(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '  expected-argument  '
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(remaining_source(arguments))
                # ASSERT #
                expected_file_ref = file_refs.of_rel_option(RelOptionType.REL_CWD,
                                                            PathPartAsFixedPath(arguments.strip()))
                assertion = matches_file_ref_resolver(expected_file_ref, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_success_when_correct_number_of_arguments__escaped(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '"expected argument"'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(remaining_source(arguments))
                # ASSERT #
                expected_file_ref = file_refs.of_rel_option(RelOptionType.REL_CWD,
                                                            PathPartAsFixedPath('expected argument'))
                assertion = matches_file_ref_resolver(expected_file_ref, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_rel_tmp_without_argument(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '--rel-tmp'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(remaining_source(arguments))
                # ASSERT #
                expected_file_ref = _file_ref_of(RelOptionType.REL_TMP)
                assertion = matches_file_ref_resolver(expected_file_ref, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_rel_tmp_with_argument(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '--rel-tmp subdir'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(remaining_source(arguments))
                # ASSERT #
                expected_file_ref = file_refs.of_rel_option(RelOptionType.REL_TMP,
                                                            PathPartAsFixedPath('subdir'))
                assertion = matches_file_ref_resolver(expected_file_ref, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_rel_tmp_with_superfluous_argument(self):
        arguments = '--rel-tmp subdir superfluous'
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                    # ACT #
                    parser.parse(remaining_source(arguments))

    def test_rel_result_should_not_be_available_pre_act_phase(self):
        arguments = '--rel-result'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser = sut.EmbryoParser(is_after_act_phase=False)
            # ACT #
            parser.parse(remaining_source(arguments))


class ParseAndChangeDirAction(sds_env_utils.SdsAction):
    def __init__(self,
                 arguments: str,
                 is_after_act_phase: bool):
        self.arguments = arguments
        self.is_after_act_phase = is_after_act_phase

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        parser = sut.EmbryoParser(self.is_after_act_phase)
        instruction_embryo = parser.parse(remaining_source(self.arguments))
        return instruction_embryo.custom_main(environment)


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


class ChangeDirTo(sds_env_utils.SdsAction):
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
                             sds_test.Arrangement(sds_contents_before=contents_in(
                                 RelSdsOptionType.REL_ACT,
                                 DirContents([
                                     empty_dir('existing-dir')
                                 ]))),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir / 'existing-dir')
                                                  ))

    def test_relative_argument_should_change_dir_relative_to_cwd__from_tmp_dir(self):
        self._check_argument('sub1/sub2',
                             sds_test.Arrangement(
                                 sds_contents_before=contents_in(RelSdsOptionType.REL_TMP,
                                                                 DirContents([
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
                                                  sds_contents_before=contents_in(
                                                      RelSdsOptionType.REL_ACT,
                                                      DirContents([
                                                          empty_dir('sub-dir')
                                                      ]))
                                                  ),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir / 'sub-dir')
                                                  ))

    def test_single_dot_argument_should_have_no_effect(self):
        self._check_argument('.',
                             sds_test.Arrangement(pre_action_action=ChangeDirTo(lambda sds: sds.act_dir / 'sub-dir'),
                                                  sds_contents_before=contents_in(RelSdsOptionType.REL_ACT,
                                                                                  DirContents([
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
                             sds_test.Arrangement(sds_contents_before=contents_in(RelSdsOptionType.REL_TMP,
                                                                                  DirContents([
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
                             sds_test.Arrangement(sds_contents_before=contents_in(RelSdsOptionType.REL_ACT,
                                                                                  DirContents([
                                                                                      empty_file('existing-file')
                                                                                  ]))),
                             sds_test.Expectation(expected_action_result=is_failure()))


def _file_ref_of(relativity=RelOptionType.REL_ACT) -> FileRef:
    return file_refs.of_rel_option(relativity, PathPartAsNothing())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
