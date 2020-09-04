import os
import pathlib
import unittest
from typing import List, Optional

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.test_case_utils.program.parse import parse_executable_file_path
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table, symbol_table_from_none_or_value
from exactly_lib_test.section_document.element_parsers.test_resources.token_stream_assertions import \
    assert_token_stream
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import matches_path_sdv
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_data_type_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import \
    TcdsPopulator
from exactly_lib_test.test_case_utils.test_resources import pre_or_post_sds_validator as validator_util
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration
from exactly_lib_test.test_resources.files.file_structure import File, executable_file, DirContents
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class RelativityConfiguration:
    def __init__(self, rel_opt_conf: RelativityOptionConfiguration):
        self._rel_opt_conf = rel_opt_conf

    @property
    def option(self) -> str:
        return self._rel_opt_conf.option_argument_str

    @property
    def exists_pre_sds(self) -> bool:
        return self._rel_opt_conf.exists_pre_sds

    def file_installation(self, file: File) -> TcdsPopulator:
        return self._rel_opt_conf.populator_for_relativity_option_root(DirContents([file]))

    def installation_dir(self, tcds: Tcds) -> pathlib.Path:
        return self._rel_opt_conf.population_dir(tcds)


def suite_for(configuration: RelativityConfiguration) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTests([CheckExistingFile(configuration),
                      CheckExistingButNonExecutableFile(configuration),
                      CheckNonExistingFile(configuration)])
    return ret_val


class Arrangement:
    def __init__(self,
                 tcds_populator: TcdsPopulator,
                 symbols: SymbolTable = None):
        self.tcds_populator = tcds_populator
        self.symbols = symbol_table_from_none_or_value(symbols)


token_stream_is_null = assert_token_stream(is_null=asrt.is_true)


def token_stream_has_remaining_source(source: str) -> ValueAssertion:
    return assert_token_stream(is_null=asrt.is_false,
                               remaining_source=asrt.equals(source))


class ExpectationOnExeFile:
    def __init__(self,
                 path_ddv: PathDdv,
                 expected_symbol_references: List[SymbolReference],
                 symbol_for_value_checks: Optional[SymbolTable] = None,
                 ):
        self.symbol_for_value_checks = symbol_for_value_checks
        if symbol_for_value_checks is None:
            self.symbol_for_value_checks = empty_symbol_table()
        self.path_ddv = path_ddv
        self.expected_symbol_references = expected_symbol_references
        if self.expected_symbol_references is None:
            self.expected_symbol_references = []


class Expectation:
    def __init__(self,
                 source: ValueAssertion[ParseSource],
                 validation_result: validation.Expectation,
                 path_ddv: PathDdv,
                 expected_symbol_references: List[SymbolReference],
                 ):
        self.source = source
        self.validation_result = validation_result
        self.expectation_on_exe_file = ExpectationOnExeFile(
            path_ddv=path_ddv,
            expected_symbol_references=expected_symbol_references,
        )


def check_exe_file(put: unittest.TestCase,
                   expectation: ExpectationOnExeFile,
                   actual: PathSdv):
    path_sdv_assertion = matches_path_sdv(
        expectation.path_ddv,
        expected_symbol_references=equals_data_type_symbol_references(expectation.expected_symbol_references),
        symbol_table=expectation.symbol_for_value_checks)
    path_sdv_assertion.apply_with_message(put, actual,
                                          'path sdv')
    path_symbols = equals_data_type_symbol_references(expectation.expected_symbol_references)
    path_symbols.apply_with_message(put, actual.references,
                                    'path-sdv/references')


def check(put: unittest.TestCase,
          instruction_argument_string: str,
          arrangement: Arrangement,
          expectation: Expectation):
    # ARRANGE #
    source = ParseSource(instruction_argument_string)
    # ACT #
    actual_exe_file = parse_executable_file_path.parse_from_parse_source(source)
    # ASSERT #
    exe_file_as_command = command_sdvs.for_executable_file(actual_exe_file)

    expectation.source.apply_with_message(put,
                                          source,
                                          'parse source')
    check_exe_file(put, expectation.expectation_on_exe_file,
                   actual_exe_file)
    with tcds_with_act_as_curr_dir(
            tcds_contents=arrangement.tcds_populator) as environment:
        os.mkdir('act-cwd')
        os.chdir('act-cwd')
        validator_util.check_ddv(
            put,
            ddv_validators.all_of(exe_file_as_command.resolve(environment.symbols).validators),
            environment.tcds,
            expectation.validation_result,
        )


class CheckBase(unittest.TestCase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__()
        self.configuration = configuration

    def _check_existence_pre_sds(self, actual: PathSdv, symbols: SymbolTable):
        self.assertEqual(self.configuration.exists_pre_sds,
                         actual.resolve(symbols).exists_pre_sds(),
                         'Existence pre SDS')

    def _check_file_path(self, file_name: str,
                         actual: PathSdv,
                         environment: PathResolvingEnvironmentPreOrPostSds):
        self.assertEqual(self.configuration.installation_dir(environment.tcds) / file_name,
                         actual.resolve_value_of_any_dependency(environment),
                         'Path string')

    def _tcds_and_test_as_curr_dir(self, file: File) -> PathResolvingEnvironmentPreOrPostSds:
        contents = self.configuration.file_installation(file)
        return tcds_with_act_as_curr_dir(tcds_contents=contents)

    def _assert_passes_validation(self,
                                  actual: PathSdv,
                                  environment: PathResolvingEnvironmentPreOrPostSds):
        path_as_exe_file_cmd = command_sdvs.for_executable_file(actual)
        validator_util.check_ddv(self,
                                 ddv_validators.all_of(path_as_exe_file_cmd.resolve(environment.symbols).validators),
                                 environment.tcds,
                                 validation.expect_passes_all_validations())

    def _assert_does_not_pass_validation(self,
                                         actual: PathSdv,
                                         environment: PathResolvingEnvironmentPreOrPostSds):
        path_as_exe_file_cmd = command_sdvs.for_executable_file(actual)
        passes_pre_sds = not self.configuration.exists_pre_sds
        passes_post_sds = not passes_pre_sds
        validator_util.check_ddv(self,
                                 ddv_validators.all_of(path_as_exe_file_cmd.resolve(environment.symbols).validators),
                                 environment.tcds,
                                 validation.Expectation(passes_pre_sds=passes_pre_sds,
                                                        passes_post_sds=passes_post_sds))


class CheckExistingFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        # ARRANGE #
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        source = ParseSource(arguments_str)
        # ACT #
        exe_file = parse_executable_file_path.parse_from_parse_source(source)
        # ASSERT #
        source_assertion = has_remaining_part_of_first_line('remaining args')
        source_assertion.apply_with_message(self, source, 'source after parse')
        self._check_existence_pre_sds(exe_file, empty_symbol_table())
        with self._tcds_and_test_as_curr_dir(executable_file('file.exe')) as environment:
            self._check_file_path('file.exe', exe_file, environment)
            self._assert_passes_validation(exe_file, environment)


class CheckExistingButNonExecutableFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        # ARRANGE #
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        source = ParseSource(arguments_str)
        # ACT #
        exe_file = parse_executable_file_path.parse_from_parse_source(source)
        # ASSERT #
        with self._tcds_and_test_as_curr_dir(File.empty('file.exe')) as environment:
            self._assert_does_not_pass_validation(exe_file, environment)


class CheckNonExistingFile(CheckBase):
    def __init__(self, configuration: RelativityConfiguration):
        super().__init__(configuration)

    def runTest(self):
        # ARRANGE #
        conf = self.configuration
        arguments_str = '{} file.exe remaining args'.format(conf.option)
        source = ParseSource(arguments_str)
        # ACT #
        exe_file = parse_executable_file_path.parse_from_parse_source(source)
        # ASSERT #
        source_assertion = has_remaining_part_of_first_line('remaining args')
        source_assertion.apply_with_message(self, source, 'source after parse')
        symbols = empty_symbol_table()
        self._check_existence_pre_sds(exe_file, symbols)
        with tcds_with_act_as_curr_dir(symbols=symbols) as environment:
            self._check_file_path('file.exe', exe_file, environment)
            self._assert_does_not_pass_validation(exe_file, environment)


def has_remaining_part_of_first_line(remaining_part: str) -> ValueAssertion[ParseSource]:
    return asrt_source.source_is_not_at_end(current_line_number=asrt.equals(1),
                                            remaining_part_of_current_line=asrt.equals(
                                                remaining_part))
