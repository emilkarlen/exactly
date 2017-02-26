import unittest

from exactly_lib.instructions.configuration import home as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, equivalent_source_variants__with_source_check
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestFailingExecution),
        unittest.makeSuite(TestSuccessfulExecution),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction mame')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)

    def test_fail_when_there_is_more_than_one_argument(self):
        for source in equivalent_source_variants(self, 'argument-1 argument-2'):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             instruction_argument: str,
             arrangement: Arrangement,
             expectation: Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._check(sut.Parser(), source, arrangement, expectation)


class TestFailingExecution(TestCaseBaseForParser):
    def test_hard_error_WHEN_path_does_not_exist(self):
        self._run(
            'non-existing-path',
            Arrangement(),
            Expectation(main_result=sh_check.is_hard_error()))

    def test_hard_error_WHEN_path_exists_but_is_a_file(self):
        file_name = 'existing-plain-file'
        self._run(
            file_name,
            Arrangement(home_dir_contents=DirContents([empty_file(file_name)])),
            Expectation(main_result=sh_check.is_hard_error())
        )


class TestSuccessfulExecution(TestCaseBaseForParser):
    def test_change_to_direct_sub_dir(self):
        directory_name = 'existing-directory'
        self._run(
            directory_name,
            Arrangement(home_dir_contents=DirContents([empty_dir(directory_name)])),
            Expectation(configuration=AssertActualHomeDirIsDirectSubDirOfOriginalHomeDir(directory_name))
        )

    def test_change_to_2_level_sub_dir(self):
        first_dir = 'first_dir'
        second_dir = 'second_dir'
        self._run(
            '{}/{}'.format(first_dir, second_dir),
            Arrangement(home_dir_contents=DirContents([Dir(first_dir,
                                                           [empty_dir(second_dir)])])),
            Expectation(configuration=AssertActualHomeDirIs2LevelSubDirOfOriginalHomeDir(first_dir,
                                                                                         second_dir))
        )

    def test_change_to_parent_dir(self):
        self._run(
            '..',
            Arrangement(),
            Expectation(configuration=AssertActualHomeDirIsParentOfOriginalHomeDir())
        )


class AssertActualHomeDirIsDirectSubDirOfOriginalHomeDir(config_check.Assertion):
    def __init__(self,
                 name_of_sub_dir: str):
        self.name_of_sub_dir = name_of_sub_dir

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        put.assertEqual(initial.home_dir_path / self.name_of_sub_dir,
                        actual_result.home_dir_path)


class AssertActualHomeDirIs2LevelSubDirOfOriginalHomeDir(config_check.Assertion):
    def __init__(self,
                 first_sub_dir: str,
                 second_sub_dir: str):
        self.first_sub_dir = first_sub_dir
        self.second_sub_dir = second_sub_dir

    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        put.assertEqual(initial.home_dir_path / self.first_sub_dir / self.second_sub_dir,
                        actual_result.home_dir_path)


class AssertActualHomeDirIsParentOfOriginalHomeDir(config_check.Assertion):
    def apply(self,
              put: unittest.TestCase,
              initial: ConfigurationBuilder,
              actual_result: ConfigurationBuilder):
        put.assertEqual(initial.home_dir_path.parent,
                        actual_result.home_dir_path)
