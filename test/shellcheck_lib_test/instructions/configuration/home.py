import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.instructions.configuration import home as sut
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.sections.anonymous import ConfigurationBuilder
from shellcheck_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from shellcheck_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Dir
from shellcheck_lib_test.test_resources.parse import new_source2


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        source = new_source2('   ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)

    def test_fail_when_there_is_more_than_one_argument(self):
        source = new_source2('argument-1 argument-2')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.Parser().apply(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestFailingExecution(TestCaseBaseForParser):
    def test_hard_error_WHEN_path_does_not_exist(self):
        self._run(
                new_source2('non-existing-path'),
                Arrangement(),
                Expectation(main_result=sh_check.IsHardError()))

    def test_hard_error_WHEN_path_exists_but_is_a_file(self):
        file_name = 'existing-plain-file'
        self._run(
                new_source2(file_name),
                Arrangement(home_dir_contents=DirContents([empty_file(file_name)])),
                Expectation(main_result=sh_check.IsHardError())
        )


class TestSuccessfulExecution(TestCaseBaseForParser):
    def test_change_to_direct_sub_dir(self):
        directory_name = 'existing-directory'
        self._run(
                new_source2(directory_name),
                Arrangement(home_dir_contents=DirContents([empty_dir(directory_name)])),
                Expectation(configuration=AssertActualHomeDirIsDirectSubDirOfOriginalHomeDir(directory_name))
        )

    def test_change_to_2_level_sub_dir(self):
        first_dir = 'first_dir'
        second_dir = 'second_dir'
        self._run(
                new_source2('{}/{}'.format(first_dir, second_dir)),
                Arrangement(home_dir_contents=DirContents([Dir(first_dir,
                                                               [empty_dir(second_dir)])])),
                Expectation(configuration=AssertActualHomeDirIs2LevelSubDirOfOriginalHomeDir(first_dir,
                                                                                             second_dir))
        )

    def test_change_to_parent_dir(self):
        self._run(
                new_source2('..'),
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


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.TheDescription('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestFailingExecution))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulExecution))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
