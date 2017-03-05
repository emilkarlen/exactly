import os
import pathlib
import unittest

from exactly_lib.instructions.utils.arg_parse import parse_executable_file as sut
from exactly_lib.instructions.utils.arg_parse.parse_utils import TokenStream
from exactly_lib.instructions.utils.executable_file import ExecutableFile
from exactly_lib.test_case.phases.common import HomeAndSds
from exactly_lib_test.instructions.test_resources import pre_or_post_sds_validator as validator_util
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_or_sds_populator import HomeOrSdsPopulator
from exactly_lib_test.test_resources.file_structure import File, executable_file, empty_file
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


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


class Arrangement:
    def __init__(self, home_or_sds_populator: HomeOrSdsPopulator):
        self.home_or_sds_populator = home_or_sds_populator


token_stream_is_null = va.sub_component('is_null',
                                        TokenStream.is_null.fget,
                                        va.Constant(True))


def token_stream_is(source: str) -> va.ValueAssertion:
    return va.sub_component('source',
                            TokenStream.source.fget,
                            va.Equals(source))


class Expectation:
    def __init__(self,
                 exists_pre_eds: bool,
                 remaining_argument: va.ValueAssertion,
                 validation_result: validator_util.Expectation,
                 arguments_of_exe_file_ref: list):
        self.exists_pre_eds = exists_pre_eds
        self.remaining_argument = remaining_argument
        self.validation_result = validation_result
        self.arguments_of_exe_file_ref = arguments_of_exe_file_ref


def expectation_for_relativity_configuration(conf: RelativityConfiguration,
                                             remaining_argument: va.ValueAssertion,
                                             validation_result: validator_util.Expectation,
                                             arguments_of_exe_file_ref: list) -> Expectation:
    return Expectation(exists_pre_eds=conf.exists_pre_sds,
                       remaining_argument=remaining_argument,
                       validation_result=validation_result,
                       arguments_of_exe_file_ref=arguments_of_exe_file_ref)


def check(put: unittest.TestCase,
          instruction_argument_string: str,
          arrangement: Arrangement,
          expectation: Expectation):
    arguments = TokenStream(instruction_argument_string)
    (actual_exe_file, actual_remaining_argument) = sut.parse(arguments)
    expectation.remaining_argument.apply_with_message(put,
                                                      actual_remaining_argument,
                                                      'Remaining arguments')
    put.assertListEqual(expectation.arguments_of_exe_file_ref,
                        actual_exe_file.arguments,
                        'Arguments of executable file')
    put.assertEquals(expectation.exists_pre_eds,
                     actual_exe_file.exists_pre_sds(),
                     'Existence pre SDS')
    with home_and_sds_with_act_as_curr_dir(home_or_sds_contents=arrangement.home_or_sds_populator) as home_and_sds:
        os.mkdir('act-cwd')
        os.chdir('act-cwd')
        validator_util.check2(put,
                              actual_exe_file.validator,
                              home_and_sds,
                              expectation.validation_result)


class CheckBase(unittest.TestCase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__()
        self.configuration = configuration

    def _check_expectance_to_exist_pre_sds(self, actual: ExecutableFile):
        self.assertEquals(self.configuration.exists_pre_sds,
                          actual.exists_pre_sds(),
                          'Existence pre SDS')

    def _check_file_path(self, file_name: str, actual: ExecutableFile, home_and_sds: HomeAndSds):
        self.assertEqual(str(self.configuration.installed_file_path(file_name, home_and_sds)),
                         actual.path_string(home_and_sds),
                         'Path string')

    def _home_and_sds_and_test_as_curr_dir(self, file: File) -> HomeAndSds:
        contents = self.configuration.file_installation(file)
        return home_and_sds_with_act_as_curr_dir(home_or_sds_contents=contents)

    def _assert_passes_validation(self, actual: ExecutableFile, home_and_sds: HomeAndSds):
        validator_util.check(self, actual.validator, home_and_sds)

    def _assert_does_not_pass_validation(self, actual: ExecutableFile, home_and_sds: HomeAndSds):
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
        (exe_file, remaining_arguments) = sut.parse(arguments)
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
        (exe_file, remaining_arguments) = sut.parse(arguments)
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
        (exe_file, remaining_arguments) = sut.parse(arguments)
        with self._home_and_sds_and_test_as_curr_dir(empty_file('file.exe')) as home_and_sds:
            self._assert_does_not_pass_validation(exe_file, home_and_sds)


class CheckNonExistingFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        arguments = TokenStream(arguments_str)
        (exe_file, remaining_arguments) = sut.parse(arguments)
        self.assertEqual('remaining args',
                         remaining_arguments.source,
                         'Remaining arguments')
        self._check_expectance_to_exist_pre_sds(exe_file)
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            self._check_file_path('file.exe', exe_file, home_and_sds)
            self._assert_does_not_pass_validation(exe_file, home_and_sds)


def suite_for(configuration: RelativityConfiguration) -> list:
    ret_val = unittest.TestSuite()
    ret_val.addTests([CheckExistingFile(configuration),
                      CheckExistingFileWithArguments(configuration),
                      CheckExistingButNonExecutableFile(configuration),
                      CheckNonExistingFile(configuration)])
    return ret_val
