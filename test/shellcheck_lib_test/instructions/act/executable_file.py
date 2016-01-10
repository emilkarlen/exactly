from shellcheck_lib.instructions.act import executable_file as sut
from shellcheck_lib_test.instructions.act.test_resources.instruction_check import *
from shellcheck_lib_test.instructions.test_resources import svh_check__va
from shellcheck_lib_test.test_resources.file_structure import DirContents, executable_file
from shellcheck_lib_test.test_resources.file_utils import absolute_path_toexecutable_file


class TestBase(TestCaseBase):
    def __check(self,
                source: str,
                arrangement: Arrangement,
                expectation: Expectation):
        self._check(sut.ExecutableFileInstruction,
                    source,
                    arrangement,
                    expectation)


class TestValidation(TestBase):
    def test_fails_when_command_is_relative_but_does_not_exist_relative_home__no_arguments(self):
        self.__check('relative-path-of-existing-program',
                     Arrangement(),
                     Expectation(validation_pre_eds=svh_check__va.is_validation_error()))

    def test_succeeds_when_command_is_relative_and_does_exist_relative_home__no_arguments(self):
        relative_path = 'relative-path-of-existing-program'
        self.__check(relative_path,
                     Arrangement(home_dir_contents=DirContents([
                         executable_file(relative_path, '')])),
                     Expectation())

    def test_fails_when_command_is_relative_but_does_not_exist_relative_home__with_arguments(self):
        relative_path = 'relative-path-of-existing-program'
        self.__check('%s argument-to-program' % relative_path,
                     Arrangement(),
                     Expectation(validation_pre_eds=svh_check__va.is_validation_error()))

    def test_succeeds_when_command_is_relative_and_does_exist_relative_home__with_arguments(self):
        relative_path = 'relative-path-of-existing-program'
        self.__check('%s argument-to-program' % relative_path,
                     Arrangement(home_dir_contents=DirContents([
                         executable_file(relative_path, '')])),
                     Expectation())

    def test_succeeds_when_command_is_absolute_without_arguments(self):
        with absolute_path_toexecutable_file() as absolute_path:
            self.__check(str(absolute_path),
                         Arrangement(),
                         Expectation())

    def test_succeeds_when_command_is_absolute_with_arguments(self):
        with absolute_path_toexecutable_file() as absolute_path:
            self.__check('%s argument-to-program' % str(absolute_path),
                         Arrangement(),
                         Expectation())


class TestStatementGeneration(TestBase):
    def test_that_relative_path_is_transformed_to_absolute_path(self):
        self.fail('TODO')


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidation),
        unittest.makeSuite(TestStatementGeneration),
    ])
