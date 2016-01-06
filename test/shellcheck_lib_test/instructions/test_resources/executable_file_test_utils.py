import pathlib
import unittest

from shellcheck_lib.instructions.utils import executable_file as sut
from shellcheck_lib.instructions.utils.parse_utils import TokenStream
from shellcheck_lib.test_case.sections.common import HomeAndEds
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import pre_or_post_eds_validator as validator_util
from shellcheck_lib_test.instructions.test_resources.utils import home_and_eds_and_test_as_curr_dir
from shellcheck_lib_test.test_resources.file_structure import File, DirContents, executable_file, empty_file


class Configuration:
    def __init__(self,
                 option: str,
                 exists_pre_eds: bool):
        self.option = option
        self.exists_pre_eds = exists_pre_eds
        # self.passes_validation_pre_eds = passes_validation_pre_eds
        # self.passes_validation_post_eds = passes_validation_post_eds

    def file_installation(self, file: File) -> (DirContents, eds_populator.EdsPopulator):
        raise NotImplementedError()

    def installed_file_path(self,
                            file_name: str,
                            home_and_eds: HomeAndEds) -> pathlib.Path:
        raise NotImplementedError()


class CheckBase(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def _check_expectance_to_exist_pre_eds(self, actual: sut.ExecutableFile):
        self.assertEquals(self.configuration.exists_pre_eds,
                          actual.exists_pre_eds,
                          'Existence pre EDS')

    def _check_file_path(self, file_name: str, actual: sut.ExecutableFile, home_and_eds: HomeAndEds):
        self.assertEqual(str(self.configuration.installed_file_path(file_name, home_and_eds)),
                         actual.path_string(home_and_eds),
                         'Path string')

    def _home_and_eds_and_test_as_curr_dir(self, file: File) -> HomeAndEds:
        contents = self.configuration.file_installation(file)
        return home_and_eds_and_test_as_curr_dir(
                home_dir_contents=contents[0],
                eds_contents=contents[1])

    def _assert_passes_validation(self, actual: sut.ExecutableFile, home_and_eds: HomeAndEds):
        validator_util.check(self, actual.validator, home_and_eds)

    def _assert_does_not_pass_validation(self, actual: sut.ExecutableFile, home_and_eds: HomeAndEds):
        passes_pre_eds = not self.configuration.exists_pre_eds
        passes_post_eds = not passes_pre_eds
        validator_util.check(self, actual.validator, home_and_eds,
                             passes_pre_eds=passes_pre_eds,
                             passes_post_eds=passes_post_eds)


class CheckExistingFile(CheckBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self._check_expectance_to_exist_pre_eds(exe_file)
        with self._home_and_eds_and_test_as_curr_dir(executable_file('file.exe')) as home_and_eds:
            self._check_file_path('file.exe', exe_file, home_and_eds)
            self._assert_passes_validation(exe_file, home_and_eds)


class CheckExistingFileWithArguments(CheckBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '( {} file.exe arg1 -arg2 ) remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual(['arg1', '-arg2'],
                         exe_file.arguments,
                         'Arguments to executable')
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self._check_expectance_to_exist_pre_eds(exe_file)
        with self._home_and_eds_and_test_as_curr_dir(executable_file('file.exe')) as home_and_eds:
            self._check_file_path('file.exe', exe_file, home_and_eds)
            self._assert_passes_validation(exe_file, home_and_eds)


class CheckExistingButNonExecutableFile(CheckBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        with self._home_and_eds_and_test_as_curr_dir(empty_file('file.exe')) as home_and_eds:
            self._assert_does_not_pass_validation(exe_file, home_and_eds)


class CheckNonExistingFile(CheckBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self._check_expectance_to_exist_pre_eds(exe_file)
        with home_and_eds_and_test_as_curr_dir() as home_and_eds:
            self._check_file_path('file.exe', exe_file, home_and_eds)
            self._assert_does_not_pass_validation(exe_file, home_and_eds)


def suite_for(configuration: Configuration) -> list:
    ret_val = unittest.TestSuite()
    ret_val.addTests([CheckExistingFile(configuration),
                      CheckExistingFileWithArguments(configuration),
                      CheckExistingButNonExecutableFile(configuration),
                      CheckNonExistingFile(configuration)])
    return ret_val
