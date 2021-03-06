import pathlib
import unittest
from pathlib import Path
from typing import Callable

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.definitions.instruction_arguments import ASSIGNMENT_OPERATOR
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.configuration.test_resources.instruction_check import Arrangement, Expectation, \
    Executor
from exactly_lib_test.impls.instructions.configuration.test_resources.source_with_assignment import \
    syntax_for_assignment_of
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir, File
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class Configuration:
    def __init__(self, target_directory: RelHdsOptionType):
        self.target_directory = target_directory

    def get_property_dir_path(self, configuration_builder: ConfigurationBuilder) -> pathlib.Path:
        return configuration_builder.hds.get(self.target_directory)

    def set_property_dir_path(self,
                              configuration_builder: ConfigurationBuilder,
                              value: pathlib.Path):
        configuration_builder.set_hds_dir(self.target_directory, value)

    def parser(self) -> InstructionParser:
        raise NotImplementedError('abstract method')

    def instruction_documentation(self) -> InstructionDocumentation:
        raise NotImplementedError('abstract method')


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_cases = [
        TestParse_fail_when_there_is_no_arguments,
        TestParse_fail_when_just_eq_argument,
        TestParse_fail_when_there_is_more_than_one_argument,
        TestSuccessfulExecution_path_SHOULD_be_relative_path_relativity_root_dir,
        TestFailingExecution_validation_error_WHEN_path_does_not_exist,
        TestFailingExecution_validation_error_WHEN_path_exists_but_is_a_file,
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
        raise NotImplementedError('abstract method')

    def _check(self,
               instruction_argument: str,
               arrangement: Arrangement,
               expectation: Expectation):
        for source in equivalent_source_variants__with_source_check__consume_last_line(self, instruction_argument):
            Executor(self, arrangement, expectation).execute(self.conf.parser(), source)

    def conf_prop_equals(self, path_rel_root_path_2_expected: Callable[[Path], Path]
                         ) -> Callable[[Path], Assertion[ConfigurationBuilder]]:
        def ret_val(path_rel_root_path: Path) -> Assertion[ConfigurationBuilder]:
            return asrt.sub_component('path prop value',
                                      self.conf.get_property_dir_path,
                                      asrt.equals(path_rel_root_path_2_expected(path_rel_root_path)))

        return ret_val


class TestParse_fail_when_there_is_no_arguments(TestCaseForConfigurationBase):
    def runTest(self):
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestParse_fail_when_just_eq_argument(TestCaseForConfigurationBase):
    def runTest(self):
        for source in equivalent_source_variants(self, ' {assign} '.format(assign=ASSIGNMENT_OPERATOR)):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestParse_fail_when_there_is_more_than_one_argument(TestCaseForConfigurationBase):
    def runTest(self):
        for source in equivalent_source_variants(self, ' {assign} argument-1 argument-2'.format(
                assign=ASSIGNMENT_OPERATOR)):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestSuccessfulExecution_path_SHOULD_be_relative_path_relativity_root_dir(TestCaseForConfigurationBase):
    def runTest(self):
        path_argument_str = 'path-argument'

        self._check(
            syntax_for_assignment_of(path_argument_str),
            Arrangement(
                root_dir_contents=DirContents([Dir.empty(path_argument_str)])
            ),
            Expectation(
                main_result=
                svh_assertions.is_success(),

                path_rel_root_2_conf=
                self.conf_prop_equals(
                    lambda path_rel_root: path_rel_root / path_argument_str)
            )
        )


class TestFailingExecution_validation_error_WHEN_path_does_not_exist(TestCaseForConfigurationBase):
    def runTest(self):
        self._check(
            syntax_for_assignment_of('non-existing-path'),
            Arrangement(),
            Expectation(main_result=svh_assertions.is_validation_error()))


class TestFailingExecution_validation_error_WHEN_path_exists_but_is_a_file(TestCaseForConfigurationBase):
    def runTest(self):
        file_name = 'existing-plain-file'
        self._check(
            syntax_for_assignment_of(file_name),
            Arrangement(
                root_dir_contents=DirContents([File.empty(file_name)])),
            Expectation(
                main_result=svh_assertions.is_validation_error())
        )


class TestSuccessfulExecution_change_to_direct_sub_dir(TestCaseForConfigurationBase):
    def runTest(self):
        directory_name = 'existing-directory'
        self._check(
            syntax_for_assignment_of(directory_name),
            Arrangement(
                root_dir_contents=DirContents([Dir.empty(directory_name)])),
            Expectation(
                path_rel_root_2_conf=
                self.conf_prop_equals(
                    lambda path_rel_root_dir: path_rel_root_dir / directory_name)
            )
        )


class TestSuccessfulExecution_change_to_2_level_sub_dir(TestCaseForConfigurationBase):
    def runTest(self):
        first_dir = 'first_dir'
        second_dir = 'second_dir'
        self._check(
            syntax_for_assignment_of('{}/{}'.format(first_dir, second_dir)),
            Arrangement(
                root_dir_contents=
                DirContents([Dir(first_dir,
                                 [Dir.empty(second_dir)])])),
            Expectation(
                path_rel_root_2_conf=
                self.conf_prop_equals(
                    lambda path_rel_root_dir: path_rel_root_dir / first_dir / second_dir)
            )
        )


class TestSuccessfulExecution_change_to_parent_dir(TestCaseForConfigurationBase):
    def runTest(self):
        self._check(
            syntax_for_assignment_of('..'),
            Arrangement(),
            Expectation(
                path_rel_root_2_conf=
                self.conf_prop_equals(
                    lambda path_rel_root_dir: path_rel_root_dir.parent)
            )
        )
