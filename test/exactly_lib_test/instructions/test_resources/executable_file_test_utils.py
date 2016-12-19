import pathlib
import unittest

from exactly_lib.instructions.utils import executable_file as sut
from exactly_lib.instructions.utils.arg_parse import parse_executable_file
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.instructions.test_resources import pre_or_post_sds_validator as validator_util
from exactly_lib_test.test_resources.execution.home_or_sds_populator import HomeOrSdsPopulator
from exactly_lib_test.test_resources.execution.utils import home_and_sds_and_test_as_curr_dir
from exactly_lib_test.test_resources.file_structure import File, executable_file, empty_file


class RelativityConfiguration:
    def __init__(self,
                 option: str,
                 exists_pre_sds: bool):
        self.option = option
        self.exists_pre_sds = exists_pre_sds

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        raise NotImplementedError()

    def installed_file_path(self,
                            file_name: str,
                            home_and_sds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()


class CheckBase(unittest.TestCase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__()
        self.configuration = configuration

    def _check_expectance_to_exist_pre_sds(self, actual: sut.ExecutableFile):
        self.assertEquals(self.configuration.exists_pre_sds,
                          actual.exists_pre_sds,
                          'Existence pre SDS')

    def _check_file_path(self, file_name: str, actual: sut.ExecutableFile, home_and_sds: HomeAndSds):
        self.assertEqual(str(self.configuration.installed_file_path(file_name, home_and_sds)),
                         actual.path_string(home_and_sds),
                         'Path string')

    def _home_and_sds_and_test_as_curr_dir(self, file: File) -> HomeAndSds:
        contents = self.configuration.file_installation(file)
        return home_and_sds_and_test_as_curr_dir(home_or_sds_contents=contents)

    def _assert_passes_validation(self, actual: sut.ExecutableFile, home_and_sds: HomeAndSds):
        validator_util.check(self, actual.validator, home_and_sds)

    def _assert_does_not_pass_validation(self, actual: sut.ExecutableFile, home_and_sds: HomeAndSds):
        passes_pre_sds = not self.configuration.exists_pre_sds
        passes_post_sds = not passes_pre_sds
        validator_util.check(self, actual.validator, home_and_sds,
                             passes_pre_sds=passes_pre_sds,
                             passes_post_sds=passes_post_sds)


class CheckExistingFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = parse_executable_file.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self._check_expectance_to_exist_pre_sds(exe_file)
        with self._home_and_sds_and_test_as_curr_dir(executable_file('file.exe')) as home_and_sds:
            self._check_file_path('file.exe', exe_file, home_and_sds)
            self._assert_passes_validation(exe_file, home_and_sds)


class CheckExistingFileWithArguments(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '( {} file.exe arg1 -arg2 ) remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = parse_executable_file.parse(arguments)
        self.assertEqual(['arg1', '-arg2'],
                         exe_file.arguments,
                         'Arguments to executable')
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self._check_expectance_to_exist_pre_sds(exe_file)
        with self._home_and_sds_and_test_as_curr_dir(executable_file('file.exe')) as home_and_sds:
            self._check_file_path('file.exe', exe_file, home_and_sds)
            self._assert_passes_validation(exe_file, home_and_sds)


class CheckExistingButNonExecutableFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = parse_executable_file.parse(arguments)
        with self._home_and_sds_and_test_as_curr_dir(empty_file('file.exe')) as home_and_sds:
            self._assert_does_not_pass_validation(exe_file, home_and_sds)


class CheckNonExistingFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = parse_executable_file.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self._check_expectance_to_exist_pre_sds(exe_file)
        with home_and_sds_and_test_as_curr_dir() as home_and_sds:
            self._check_file_path('file.exe', exe_file, home_and_sds)
            self._assert_does_not_pass_validation(exe_file, home_and_sds)


def suite_for(configuration: RelativityConfiguration) -> list:
    ret_val = unittest.TestSuite()
    ret_val.addTests([CheckExistingFile(configuration),
                      CheckExistingFileWithArguments(configuration),
                      CheckExistingButNonExecutableFile(configuration),
                      CheckNonExistingFile(configuration)])
    return ret_val
