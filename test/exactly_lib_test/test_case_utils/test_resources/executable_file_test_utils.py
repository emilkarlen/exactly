import os
import pathlib
import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.external_program import parse as sut
from exactly_lib.test_case_utils.external_program.executable_file import ExecutableFileWithArgsResolver
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table, symbol_table_from_none_or_value
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import matches_file_ref_resolver
from exactly_lib_test.symbol.data.test_resources.list_assertions import matches_list_resolver
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator
from exactly_lib_test.test_case_utils.test_resources import pre_or_post_sds_validator as validator_util
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.file_structure import File, executable_file, empty_file, DirContents
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.data.test_resources.list_values import list_value_of_string_constants


class RelativityConfiguration:
    def __init__(self, rel_opt_conf: RelativityOptionConfiguration):
        self._rel_opt_conf = rel_opt_conf

    @property
    def option(self) -> str:
        return self._rel_opt_conf.option_string

    @property
    def exists_pre_sds(self) -> bool:
        return self._rel_opt_conf.exists_pre_sds

    def file_installation(self, file: File) -> HomeOrSdsPopulator:
        return self._rel_opt_conf.populator_for_relativity_option_root(DirContents([file]))

    def installation_dir(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        return self._rel_opt_conf.population_dir(home_and_sds)


def suite_for(configuration: RelativityConfiguration) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests([CheckExistingFile(configuration),
                      CheckExistingFileWithArguments(configuration),
                      CheckExistingButNonExecutableFile(configuration),
                      CheckNonExistingFile(configuration)])
    return ret_val


class Arrangement:
    def __init__(self,
                 home_or_sds_populator: HomeOrSdsPopulator,
                 symbols: SymbolTable = None):
        self.home_or_sds_populator = home_or_sds_populator
        self.symbols = symbol_table_from_none_or_value(symbols)


token_stream_is_null = assert_token_stream(is_null=asrt.is_true)


def token_stream_has_remaining_source(source: str) -> asrt.ValueAssertion:
    return assert_token_stream(is_null=asrt.is_false,
                               remaining_source=asrt.equals(source))


class ExpectationOnExeFile:
    def __init__(self,
                 file_resolver_value: FileRef,
                 expected_symbol_references_of_file: list,
                 argument_resolver_value: ListValue,
                 expected_symbol_references_of_argument: list,
                 symbol_for_value_checks: SymbolTable = None):
        self.symbol_for_value_checks = symbol_for_value_checks
        if symbol_for_value_checks is None:
            self.symbol_for_value_checks = empty_symbol_table()
        self.file_resolver_value = file_resolver_value
        self.expected_symbol_references_of_file = expected_symbol_references_of_file
        if self.expected_symbol_references_of_file is None:
            self.expected_symbol_references_of_file = []
        self.argument_resolver_value = argument_resolver_value
        self.expected_symbol_references_of_argument = expected_symbol_references_of_argument
        if self.expected_symbol_references_of_argument is None:
            self.expected_symbol_references_of_argument = []


class Expectation:
    def __init__(self,
                 source: asrt.ValueAssertion[ParseSource],
                 validation_result: validator_util.Expectation,
                 file_resolver_value: FileRef,
                 expected_symbol_references_of_file: list,
                 argument_resolver_value: ListValue,
                 expected_symbol_references_of_argument: list):
        self.source = source
        self.validation_result = validation_result
        self.expectation_on_exe_file = ExpectationOnExeFile(file_resolver_value=file_resolver_value,
                                                            expected_symbol_references_of_file=expected_symbol_references_of_file,
                                                            argument_resolver_value=argument_resolver_value,
                                                            expected_symbol_references_of_argument=expected_symbol_references_of_argument)


def check_exe_file(put: unittest.TestCase,
                   expectation: ExpectationOnExeFile,
                   actual: ExecutableFileWithArgsResolver):
    file_resolver_assertion = matches_file_ref_resolver(
        expectation.file_resolver_value,
        expected_symbol_references=equals_symbol_references(expectation.expected_symbol_references_of_file),
        symbol_table=expectation.symbol_for_value_checks)
    file_resolver_assertion.apply_with_message(put, actual.executable_file,
                                               'file_resolver')
    file_ref_symbols = equals_symbol_references(expectation.expected_symbol_references_of_file)
    file_ref_symbols.apply_with_message(put, actual.executable_file.references,
                                        'file-resolver/references')
    arguments_resolver_assertion = matches_list_resolver(
        expectation.argument_resolver_value,
        expected_symbol_references=equals_symbol_references(expectation.expected_symbol_references_of_argument),
        symbols=expectation.symbol_for_value_checks,
    )
    arguments_resolver_assertion.apply_with_message(put, actual.arguments,
                                                    'arguments')
    assertion_on_all_references = equals_symbol_references(expectation.expected_symbol_references_of_file +
                                                           expectation.expected_symbol_references_of_argument)
    assertion_on_all_references.apply_with_message(put, actual.as_command.references,
                                                   'references')


def check(put: unittest.TestCase,
          instruction_argument_string: str,
          arrangement: Arrangement,
          expectation: Expectation):
    # ARRANGE #
    source = ParseSource(instruction_argument_string)
    # ACT #
    actual_exe_file = sut.parse_executable_file_with_args_from_parse_source(source)
    # ASSERT #
    expectation.source.apply_with_message(put,
                                          source,
                                          'parse source')
    check_exe_file(put, expectation.expectation_on_exe_file,
                   actual_exe_file)
    with home_and_sds_with_act_as_curr_dir(
            home_or_sds_contents=arrangement.home_or_sds_populator) as environment:
        os.mkdir('act-cwd')
        os.chdir('act-cwd')
        validator_util.check(put,
                             actual_exe_file.as_command.validator,
                             environment,
                             expectation.validation_result)


class CheckBase(unittest.TestCase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__()
        self.configuration = configuration

    def _check_expectance_to_exist_pre_sds(self, actual: ExecutableFileWithArgsResolver, symbols: SymbolTable):
        self.assertEqual(self.configuration.exists_pre_sds,
                         actual.executable_file.resolve(symbols).exists_pre_sds(),
                         'Existence pre SDS')

    def _check_file_path(self, file_name: str, actual: ExecutableFileWithArgsResolver,
                         environment: PathResolvingEnvironmentPreOrPostSds):
        self.assertEqual(self.configuration.installation_dir(environment.home_and_sds) / file_name,
                         actual.executable_file.resolve_value_of_any_dependency(environment),
                         'Path string')

    def _home_and_sds_and_test_as_curr_dir(self, file: File) -> PathResolvingEnvironmentPreOrPostSds:
        contents = self.configuration.file_installation(file)
        return home_and_sds_with_act_as_curr_dir(home_or_sds_contents=contents)

    def _assert_passes_validation(self, actual: ExecutableFileWithArgsResolver,
                                  environment: PathResolvingEnvironmentPreOrPostSds):
        validator_util.check(self, actual.as_command.validator, environment,
                             validator_util.expect_passes_all_validations())

    def _assert_does_not_pass_validation(self, actual: ExecutableFileWithArgsResolver,
                                         environment: PathResolvingEnvironmentPreOrPostSds):
        passes_pre_sds = not self.configuration.exists_pre_sds
        passes_post_sds = not passes_pre_sds
        validator_util.check(self, actual.as_command.validator, environment,
                             validator_util.Expectation(passes_pre_sds=passes_pre_sds,
                                                        passes_post_sds=passes_post_sds))


class CheckExistingFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        source = ParseSource(arguments_str)
        exe_file = sut.parse_executable_file_with_args_from_parse_source(source)
        source_assertion = has_remaining_part_of_first_line('remaining args')
        source_assertion.apply_with_message(self, source, 'source after parse')
        self._check_expectance_to_exist_pre_sds(exe_file, empty_symbol_table())
        with self._home_and_sds_and_test_as_curr_dir(executable_file('file.exe')) as environment:
            self._check_file_path('file.exe', exe_file, environment)
            self._assert_passes_validation(exe_file, environment)


class CheckExistingFileWithArguments(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '( {} file.exe arg1 -arg2 ) remaining args'.format(conf.option)
        source = ParseSource(arguments_str)
        exe_file = sut.parse_executable_file_with_args_from_parse_source(source)
        expected_arguments = list_value_of_string_constants(['arg1', '-arg2'])
        arguments_assertion = matches_list_resolver(expected_arguments,
                                                    expected_symbol_references=asrt.is_empty_sequence)
        arguments_assertion.apply_with_message(self, exe_file.arguments,
                                               'arguments')
        source_assertion = has_remaining_part_of_first_line('remaining args')
        source_assertion.apply_with_message(self, source, 'source after parse')
        self._check_expectance_to_exist_pre_sds(exe_file, empty_symbol_table())
        with self._home_and_sds_and_test_as_curr_dir(executable_file('file.exe')) as environment:
            self._check_file_path('file.exe', exe_file, environment)
            self._assert_passes_validation(exe_file, environment)


class CheckExistingButNonExecutableFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        source = ParseSource(arguments_str)
        exe_file = sut.parse_executable_file_with_args_from_parse_source(source)
        with self._home_and_sds_and_test_as_curr_dir(empty_file('file.exe')) as environment:
            self._assert_does_not_pass_validation(exe_file, environment)


class CheckNonExistingFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        source = ParseSource(arguments_str)
        exe_file = sut.parse_executable_file_with_args_from_parse_source(source)
        source_assertion = has_remaining_part_of_first_line('remaining args')
        source_assertion.apply_with_message(self, source, 'source after parse')
        symbols = empty_symbol_table()
        self._check_expectance_to_exist_pre_sds(exe_file, symbols)
        with home_and_sds_with_act_as_curr_dir(symbols=symbols) as environment:
            self._check_file_path('file.exe', exe_file, environment)
            self._assert_does_not_pass_validation(exe_file, environment)


def has_remaining_part_of_first_line(remaining_part: str) -> asrt.ValueAssertion[ParseSource]:
    return asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                            remaining_part_of_current_line=asrt.equals(
                                                remaining_part))
