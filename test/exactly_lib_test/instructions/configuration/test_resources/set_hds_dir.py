import pathlib
import unittest

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_section import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parsing_configuration import FileSystemLocationInfo
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, ConfigurationPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import Arrangement, Expectation, \
    Executor
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.result.test_resources import sh_assertions
from exactly_lib_test.test_case.test_resources.configuration import arbitrary_configuration_builder
from exactly_lib_test.test_case_file_structure.test_resources.home_populators import contents_in
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, empty_dir, Dir
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class Configuration:
    def __init__(self, target_directory: RelHomeOptionType):
        self.target_directory = target_directory

    def get_property_dir_path(self, configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        raise NotImplementedError('abstract method')

    def set_property_dir_path(self,
                              configuration_builder: ConfigurationBuilder,
                              value: pathlib.Path):
        raise NotImplementedError('abstract method')

    def parser(self) -> InstructionParser:
        raise NotImplementedError('abstract method')

    def instruction_documentation(self) -> InstructionDocumentation:
        raise NotImplementedError('abstract method')


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestParse_fail_when_there_is_no_arguments,
        TestParse_fail_when_just_eq_argument,
        TestParse_fail_when_there_is_more_than_one_argument,
        Test_path_SHOULD_be_relative_file_reference_relativity_root_dir,
        TestFailingExecution_hard_error_WHEN_path_does_not_exist,
        TestFailingExecution_hard_error_WHEN_path_exists_but_is_a_file,
        TestSuccessfulExecution_change_to_direct_sub_dir,
        TestSuccessfulExecution_change_to_2_level_sub_dir,
        TestSuccessfulExecution_change_to_parent_dir,
    ]

    functionality_test_suite = unittest.TestSuite([tc(configuration) for tc in test_cases])
    documentation_test_suite = suite_for_instruction_documentation(configuration.instruction_documentation())

    return unittest.TestSuite([
        functionality_test_suite,
        documentation_test_suite,
    ])


class TestCaseForConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)
        self.conf = configuration

    def runTest(self):
        raise NotImplementedError()

    def _check(self,
               instruction_argument: str,
               arrangement: Arrangement,
               expectation: Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            Executor(self, arrangement, expectation).execute(self.conf.parser(), source)


class TestParse_fail_when_there_is_no_arguments(TestCaseForConfigurationBase):
    def runTest(self):
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestParse_fail_when_just_eq_argument(TestCaseForConfigurationBase):
    def runTest(self):
        for source in equivalent_source_variants(self, '  = '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestParse_fail_when_there_is_more_than_one_argument(TestCaseForConfigurationBase):
    def runTest(self):
        for source in equivalent_source_variants(self, ' = argument-1 argument-2'):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class Test_path_SHOULD_be_relative_file_reference_relativity_root_dir(TestCaseForConfigurationBase):
    def runTest(self):
        # ARRANGE #
        initial_path_name = 'the-initial-path'
        file_reference_relativity_path_name = 'the-file-ref-rel-path'

        file_reference_relativity_path = pathlib.Path(file_reference_relativity_path_name)
        fs_location_info = FileSystemLocationInfo(file_reference_relativity_path)

        path_argument_str = 'path-argument'
        source = remaining_source(instruction_arguments.ASSIGNMENT_OPERATOR + ' ' + path_argument_str)

        conf_builder = arbitrary_configuration_builder()
        self.conf.set_property_dir_path(conf_builder, pathlib.Path(initial_path_name))

        # ACT #

        instruction = self.conf.parser().parse(fs_location_info, source)
        assert isinstance(instruction, ConfigurationPhaseInstruction)

        cwd_dir_contents = DirContents([
            Dir(initial_path_name,
                [empty_dir(path_argument_str)]),

            Dir(file_reference_relativity_path_name,
                [empty_dir(path_argument_str)]),
        ])

        with tmp_dir_as_cwd(cwd_dir_contents):
            expected_path = (file_reference_relativity_path / path_argument_str).resolve()
            result = instruction.main(conf_builder)

        # ASSERT #

        self.assertTrue(result.is_success)

        changed_path = self.conf.get_property_dir_path(conf_builder)

        self.assertEqual(expected_path, changed_path)


class TestFailingExecution_hard_error_WHEN_path_does_not_exist(TestCaseForConfigurationBase):
    def runTest(self):
        self._check(
            '= non-existing-path',
            Arrangement(),
            Expectation(main_result=sh_assertions.is_hard_error()))


class TestFailingExecution_hard_error_WHEN_path_exists_but_is_a_file(TestCaseForConfigurationBase):
    def runTest(self):
        file_name = 'existing-plain-file'
        self._check(
            '= ' + file_name,
            Arrangement(
                hds_contents=contents_in(self.conf.target_directory, DirContents([
                    empty_file(file_name)]))),
            Expectation(
                main_result=sh_assertions.is_hard_error())
        )


class TestSuccessfulExecution_change_to_direct_sub_dir(TestCaseForConfigurationBase):
    def runTest(self):
        directory_name = 'existing-directory'
        self._check(
            ' = ' + directory_name,
            Arrangement(
                hds_contents=contents_in(self.conf.target_directory, DirContents([
                    empty_dir(directory_name)]))),
            Expectation(
                configuration=AssertActualHomeDirIsDirectSubDirOfOriginalHomeDir(self.conf,
                                                                                 directory_name))
        )


class TestSuccessfulExecution_change_to_2_level_sub_dir(TestCaseForConfigurationBase):
    def runTest(self):
        first_dir = 'first_dir'
        second_dir = 'second_dir'
        self._check(
            ' =  {}/{}'.format(first_dir, second_dir),
            Arrangement(
                hds_contents=contents_in(self.conf.target_directory, DirContents([
                    Dir(first_dir,
                        [empty_dir(second_dir)])]))),
            Expectation(
                configuration=AssertActualHomeDirIs2LevelSubDirOfOriginalHomeDir(self.conf,
                                                                                 first_dir,
                                                                                 second_dir))
        )


class TestSuccessfulExecution_change_to_parent_dir(TestCaseForConfigurationBase):
    def runTest(self):
        self._check(
            ' = ..',
            Arrangement(),
            Expectation(configuration=AssertActualHomeDirIsParentOfOriginalHomeDir(self.conf))
        )


class AssertActualHomeDirIsDirectSubDirOfOriginalHomeDir(config_check.Assertion):
    def __init__(self,
                 configuration: Configuration,
                 name_of_sub_dir: str):
        self.configuration = configuration
        self.name_of_sub_dir = name_of_sub_dir

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        initial_value = self.configuration.get_property_dir_path(initial)
        actual_value = self.configuration.get_property_dir_path(actual_result)
        put.assertEqual(initial_value / self.name_of_sub_dir,
                        actual_value)


class AssertActualHomeDirIs2LevelSubDirOfOriginalHomeDir(config_check.Assertion):
    def __init__(self,
                 configuration: Configuration,
                 first_sub_dir: str,
                 second_sub_dir: str):
        self.configuration = configuration
        self.first_sub_dir = first_sub_dir
        self.second_sub_dir = second_sub_dir

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        initial_value = self.configuration.get_property_dir_path(initial)
        actual_value = self.configuration.get_property_dir_path(actual_result)
        put.assertEqual(initial_value / self.first_sub_dir / self.second_sub_dir,
                        actual_value)


class AssertActualHomeDirIsParentOfOriginalHomeDir(config_check.Assertion):
    def __init__(self,
                 configuration: Configuration):
        self.configuration = configuration

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        initial_value = self.configuration.get_property_dir_path(initial)
        actual_value = self.configuration.get_property_dir_path(actual_result)
        put.assertEqual(initial_value.parent,
                        actual_value)
