import os
import pathlib
import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import path as path_syntax
from exactly_lib.instructions.multi_phase import change_dir as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds
from exactly_lib.tcfs.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib.tcfs.relativity_root import REL_SDS_RESOLVERS
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check, path_name_variants
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import matches_path_sdv
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.tcfs.test_resources.format_rel_option import format_rel_options
from exactly_lib_test.tcfs.test_resources.path_arguments import RelOptPathArgument
from exactly_lib_test.tcfs.test_resources.sds_populator import contents_in
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir, File
from exactly_lib_test.test_resources.tcds_and_symbols import sds_test, sds_env_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase, \
    MessageBuilder
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueIsNone
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
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


class TestParse(unittest.TestCase):
    def test_no_relativity_option_should_use_default_option(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = 'single-argument'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))
                # ASSERT #
                expected_path = paths.of_rel_option(RelOptionType.REL_CWD,
                                                    paths.constant_path_part(arguments))
                assertion = matches_path_sdv(expected_path, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_fail_when_superfluous_arguments(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = 'expected-argument superfluous-argument'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT & ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))

    def test_fail_when_no_arguments(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = ''
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT & ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))

    def test_strip_trailing_space(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '  expected-argument  '
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))
                # ASSERT #
                expected_path = paths.of_rel_option(RelOptionType.REL_CWD,
                                                    paths.constant_path_part(arguments.strip()))
                assertion = matches_path_sdv(expected_path, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_success_when_correct_number_of_arguments__escaped(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = '"expected argument"'
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))
                # ASSERT #
                expected_path = paths.of_rel_option(RelOptionType.REL_CWD,
                                                    paths.constant_path_part('expected argument'))
                assertion = matches_path_sdv(expected_path, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_rel_tmp_with_argument(self):
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                arguments = format_rel_options('{rel_tmp} subdir')
                parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                # ACT #
                actual = parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))
                # ASSERT #
                expected_path = paths.of_rel_option(RelOptionType.REL_TMP,
                                                    paths.constant_path_part('subdir'))
                assertion = matches_path_sdv(expected_path, asrt.is_empty)
                assertion.apply_without_message(self, actual.destination)

    def test_rel_tmp_with_superfluous_argument(self):
        arguments = format_rel_options('{rel_tmp} subdir superfluous')
        for is_after_act_phase in [False, True]:
            with self.subTest(is_after_act_phase=is_after_act_phase):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser = sut.EmbryoParser(is_after_act_phase=is_after_act_phase)
                    # ACT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))

    def test_rel_result_should_not_be_available_pre_act_phase(self):
        arguments = path_syntax.REL_RESULT_OPTION
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser = sut.EmbryoParser(is_after_act_phase=False)
            # ACT #
            parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(arguments))

    def test_with_explicit_non_cd_relativity_and_source_layout_variants(self):
        # ARRANGE #
        relativity = RelOptionType.REL_TMP
        for is_after_act_phase in [False, True]:
            checker = embryo_checker(is_after_act_phase)
            for case in path_name_variants.SOURCE_LAYOUT_CASES:
                path_argument = RelOptPathArgument(case.input_value, relativity)
                with self.subTest(case.name,
                                  is_after_act_phase=is_after_act_phase):
                    with self.subTest(case.name):
                        # ACT & ASSERT #
                        checker.check__w_source_variants(
                            self,
                            path_argument.as_str,
                            ArrangementWithSds(
                                tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                                    relativity,
                                    DirContents([Dir.empty(case.expected_value)])
                                )
                            ),
                            embryo_check.Expectation(
                                side_effects_on_tcds=CwdAssertion(
                                    relativity,
                                    case.expected_value,
                                )
                            )
                        )


class ParseAndChangeDirAction(sds_env_utils.SdsAction):
    def __init__(self,
                 arguments: str,
                 is_after_act_phase: bool):
        self.arguments = arguments
        self.is_after_act_phase = is_after_act_phase

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        parser = sut.EmbryoParser(self.is_after_act_phase)
        instruction_embryo = parser.parse(ARBITRARY_FS_LOCATION_INFO, remaining_source(self.arguments))
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
    return asrt_renderer.is_renderer_of_major_blocks()


class ChangeDirTo(sds_env_utils.SdsAction):
    def __init__(self, sds2dir_fun):
        self.sds2dir_fun = sds2dir_fun

    def apply(self, environment: PathResolvingEnvironmentPostSds):
        os.chdir(str(self.sds2dir_fun(environment.sds)))


class CwdIsActDir(sds_test.PostActionCheck):
    def apply(self, put: unittest.TestCase, sds: SandboxDs):
        put.assertEqual(str(sds.act_dir),
                        os.getcwd(),
                        'Current Working Directory')


class CwdIsSubDirOfActDir(sds_test.PostActionCheck):
    def __init__(self, sub_dir_name: str):
        self.sub_dir_name = sub_dir_name

    def apply(self, put: unittest.TestCase, sds: SandboxDs):
        put.assertEqual(str(sds.act_dir / self.sub_dir_name),
                        os.getcwd(),
                        'Current Working Directory')


class CwdIs(sds_test.PostActionCheck):
    def __init__(self, sds2dir_fun):
        self.sds2dir_fun = sds2dir_fun

    def apply(self, put: unittest.TestCase, sds: SandboxDs):
        put.assertEqual(str(self.sds2dir_fun(sds)),
                        os.getcwd(),
                        'Current Working Directory')


class CwdAssertion(ValueAssertionBase[TestCaseDs]):
    def __init__(self,
                 expected_location: RelOptionType,
                 expected_base_name: str,
                 ):
        self.expected_location = expected_location
        self.expected_base_name = expected_base_name

    def _apply(self,
               put: unittest.TestCase,
               value: TestCaseDs,
               message_builder: MessageBuilder):
        expected = (
            paths.simple_of_rel_option(self.expected_location,
                                       self.expected_base_name)
                .value_of_any_dependency__d(value)
                .primitive
        )
        actual = pathlib.Path().cwd()

        put.assertEqual(expected,
                        actual,
                        message_builder.apply('current directory'))


class CwdSdsAssertion(ValueAssertionBase[SandboxDs]):
    def __init__(self,
                 expected_location: RelSdsOptionType,
                 expected_base_name: str,
                 ):
        self.expected_location = expected_location
        self.expected_base_name = expected_base_name

    def _apply(self,
               put: unittest.TestCase,
               value: SandboxDs,
               message_builder: MessageBuilder):
        sds_root = REL_SDS_RESOLVERS[self.expected_location].from_sds(value)
        expected = sds_root / self.expected_base_name

        actual = pathlib.Path().cwd()

        put.assertEqual(expected,
                        actual,
                        message_builder.apply('current directory'))


class TestSuccessfulScenarios(TestCaseBase):
    def test_relative_argument_should_change_dir_relative_to_cwd__from_act_dir(self):
        self._check_argument('existing-dir',
                             sds_test.Arrangement(sds_contents_before=contents_in(
                                 RelSdsOptionType.REL_ACT,
                                 DirContents([
                                     Dir.empty('existing-dir')
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
                                                                         Dir.empty('sub2')
                                                                     ])
                                                                 ])),
                                 pre_action_action=ChangeDirTo(lambda sds: sds.user_tmp_dir)),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(
                                                      lambda sds: sds.user_tmp_dir / 'sub1' / 'sub2')
                                                  ))

    def test_single_dot_argument_should_have_no_effect(self):
        self._check_argument('.',
                             sds_test.Arrangement(pre_action_action=ChangeDirTo(lambda sds: sds.act_dir / 'sub-dir'),
                                                  sds_contents_before=contents_in(RelSdsOptionType.REL_ACT,
                                                                                  DirContents([
                                                                                      Dir.empty('sub-dir')
                                                                                  ]))
                                                  ),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir / 'sub-dir')
                                                  ))

    def test_act_root_option_should_change_to_act_dir__dot_arg(self):
        self._check_argument(format_rel_options('{rel_act} .'),
                             sds_test.Arrangement(pre_action_action=ChangeDirTo(lambda sds: sds.root_dir)),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.act_dir)
                                                  ))

    def test_relative_tmp__with_argument__dot_arg(self):
        self._check_argument(format_rel_options('{rel_tmp} .'),
                             sds_test.Arrangement(),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(lambda sds: sds.user_tmp_dir)
                                                  ))

    def test_relative_tmp__with_argument(self):
        self._check_argument(format_rel_options('{rel_tmp} sub1/sub2'),
                             sds_test.Arrangement(sds_contents_before=contents_in(RelSdsOptionType.REL_TMP,
                                                                                  DirContents([
                                                                                      Dir('sub1', [
                                                                                          Dir.empty('sub2')
                                                                                      ])
                                                                                  ]))),
                             sds_test.Expectation(expected_action_result=is_success(),
                                                  post_action_check=CwdIs(
                                                      lambda sds: sds.user_tmp_dir / 'sub1' / 'sub2')
                                                  ))

    def test_relative_result__after_act_phase(self):
        self._check_argument_for_single_case(
            True,
            format_rel_options('{rel_result} .'),
            sds_test.Arrangement(),
            sds_test.Expectation(expected_action_result=is_success(),
                                 post_action_check=CwdIs(lambda sds: sds.result.root_dir)
                                 ))


class TestFailingScenarios(TestCaseBase):
    def test_argument_is_file(self):
        self._check_argument('existing-file',
                             sds_test.Arrangement(sds_contents_before=contents_in(RelSdsOptionType.REL_ACT,
                                                                                  DirContents([
                                                                                      File.empty('existing-file')
                                                                                  ]))),
                             sds_test.Expectation(expected_action_result=is_failure()))


def _path_of(relativity=RelOptionType.REL_ACT) -> PathDdv:
    return paths.of_rel_option(relativity, paths.empty_path_part())


def embryo_checker(is_after_act_phase: bool) -> embryo_check.Checker[Optional[TextRenderer]]:
    return embryo_check.Checker(sut.EmbryoParser(is_after_act_phase))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
