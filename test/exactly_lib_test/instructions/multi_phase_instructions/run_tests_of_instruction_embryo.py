import pathlib
import sys
import unittest

from exactly_lib.help_texts.file_ref import REL_HOME_OPTION
from exactly_lib.instructions.multi_phase_instructions import run as sut
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import symbol_table_with_entries
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.assertion_utils import sub_process_result_check as spr_check
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulatorForHomeContents, HomeOrSdsPopulator, multiple
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import home_and_sds_test
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidationAndSymbolUsagesOfExecute),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfInterpret),
        unittest.makeSuite(TestValidationAndSymbolUsagesOfSource),
        unittest.makeSuite(TestExecuteProgramWithPythonExecutorWithSourceOnCommandLine),
    ])


class TestCaseBase(home_and_sds_test.TestCaseBase):
    def _check_single_line_arguments_with_source_variants(self,
                                                          instruction_argument: str,
                                                          arrangement: ArrangementWithSds,
                                                          expectation: embryo_check.Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            parser = sut.embryo_parser('instruction-name')
            embryo_check.check(self, parser, source, arrangement, expectation)


class TestValidationAndSymbolUsagesOfExecute(TestCaseBase):
    def test_validate_should_fail_when_executable_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file'.format(
                relativity_option=relativity_option_conf.option_string)

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols_in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_success_when_executable_does_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} {executable_file}'.format(
                relativity_option=relativity_option_conf.option_string,
                executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
            )

            expectation = embryo_check.Expectation(
                symbol_usages=asrt.matches_sequence(relativity_option_conf.symbol_usage_expectation_assertions()),
            )

            arrangement = ArrangementWithSds(
                home_or_sds_contents=relativity_option_conf.populator_for_relativity_option_root(
                    fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])),
                symbols=relativity_option_conf.symbols_in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)


class TestValidationAndSymbolUsagesOfInterpret(TestCaseBase):
    def test_success_when_referenced_files_does_exist(self):
        symbol_name_for_executable_file = 'EXECUTABLE_FILE_SYMBOL_NAME'
        symbol_name_for_source_file = 'SOURCE_FILE_SYMBOL_NAME'
        source_file = fs.empty_file('source-file.src')
        for roc_executable_file in relativity_options(symbol_name_for_executable_file):
            for roc_source_file in relativity_options(symbol_name_for_source_file):
                argument = '{relativity_option_executable} {executable_file} {interpret_option}' \
                           ' {relativity_option_source_file} {source_file}'.format(
                    relativity_option_executable=roc_executable_file.option_string,
                    relativity_option_source_file=roc_source_file.option_string,
                    executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
                    interpret_option=sut.INTERPRET_OPTION,
                    source_file=source_file.file_name,
                )

                expectation = embryo_check.Expectation(
                    symbol_usages=asrt.matches_sequence(roc_executable_file.symbol_usage_expectation_assertions() +
                                                        roc_source_file.symbol_usage_expectation_assertions()),
                )

                arrangement = ArrangementWithSds(
                    home_or_sds_contents=multiple([
                        roc_executable_file.populator_for_relativity_option_root(
                            fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])),
                        roc_source_file.populator_for_relativity_option_root(
                            fs.DirContents([source_file])),
                    ]),
                    symbols=symbol_table_with_entries(
                        roc_executable_file.symbol_entries_for_arrangement() +
                        roc_source_file.symbol_entries_for_arrangement()),

                )
                test_name = 'exe-file-option={}, source-file-option={}'.format(
                    roc_executable_file.test_case_description,
                    roc_source_file.test_case_description,
                )
                with self.subTest(msg=test_name):
                    self._check_single_line_arguments_with_source_variants(argument,
                                                                           arrangement,
                                                                           expectation)

    def test_validate_should_fail_when_executable_does_not_exist(self):
        existing_file_to_interpret = 'existing-file-to-interpret.src'
        home_dir_contents = fs.DirContents([fs.empty_file(existing_file_to_interpret)])
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {interpret_option}' \
                       ' {rel_home_option} {existing_file}'.format(
                relativity_option=relativity_option_conf.option_string,
                interpret_option=sut.INTERPRET_OPTION,
                rel_home_option=REL_HOME_OPTION,
                existing_file=existing_file_to_interpret,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols_in_arrangement(),
                home_contents=home_dir_contents,
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_validate_should_fail_when_file_to_interpret_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '"{python_interpreter}" {interpret_option} {relativity_option} non-existing-file.py'.format(
                python_interpreter=sys.executable,
                interpret_option=sut.INTERPRET_OPTION,
                relativity_option=relativity_option_conf.option_string,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols_in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)


class TestValidationAndSymbolUsagesOfSource(TestCaseBase):
    def test_success_when_executable_does_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} {executable_file} {source_option} irrelevant-source'.format(
                relativity_option=relativity_option_conf.option_string,
                executable_file=EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0.file_name,
                source_option=sut.SOURCE_OPTION,
            )

            expectation = embryo_check.Expectation(
                symbol_usages=asrt.matches_sequence(relativity_option_conf.symbol_usage_expectation_assertions()),
            )

            arrangement = ArrangementWithSds(
                home_or_sds_contents=relativity_option_conf.populator_for_relativity_option_root(
                    fs.DirContents([EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0])),
                symbols=relativity_option_conf.symbols_in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_validate_should_fail_when_executable_does_not_exist(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {source_option} irrelevant-source'.format(
                relativity_option=relativity_option_conf.option_string,
                source_option=sut.SOURCE_OPTION,
            )

            expectation = _expect_validation_error_and_symbol_usages_of(relativity_option_conf)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols_in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)


def _expect_validation_error_and_symbol_usages_of(relativity_option_conf: rel_opt_conf.RelativityOptionConfiguration
                                                  ) -> embryo_check.Expectation:
    return _expect_validation_error_and_symbol_usages(relativity_option_conf,
                                                      relativity_option_conf.symbol_usage_expectation_assertions())


def _expect_validation_error_and_symbol_usages(relativity_option_conf: rel_opt_conf.RelativityOptionConfiguration,
                                               expected_symbol_usage: list) -> embryo_check.Expectation:
    expected_symbol_usages_assertion = asrt.matches_sequence(expected_symbol_usage)
    if relativity_option_conf.exists_pre_sds:
        return embryo_check.Expectation(
            validation_pre_sds=IS_VALIDATION_ERROR,
            symbol_usages=expected_symbol_usages_assertion,
        )
    else:
        return embryo_check.Expectation(
            validation_post_sds=IS_VALIDATION_ERROR,
            symbol_usages=expected_symbol_usages_assertion,
        )


class TestExecuteProgramWithPythonExecutorWithSourceOnCommandLine(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_executing_program_via_command_line('exit(0)'),
            ArrangementWithSds(),
            Expectation(main_result=spr_check.is_success_result(0, None)))

    def test_double_dash_should_invoke_execute(self):
        argument = py_exe.command_line_for_executing_program_via_command_line(
            'exit(0)',
            args_directly_after_interpreter='--')
        self._check_single_line_arguments_with_source_variants(
            argument,
            ArrangementWithSds(),
            Expectation(main_result=spr_check.is_success_result(0, None)))

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_executing_program_via_command_line('exit(1)'),
            ArrangementWithSds(),
            Expectation(main_result=spr_check.is_success_result(1, '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write(\\"on stderr\\"); exit(2)'
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_executing_program_via_command_line(python_program),
            ArrangementWithSds(),
            Expectation(main_result=spr_check.is_success_result(2, 'on stderr')))

    def test_non_existing_executable(self):
        self._check_single_line_arguments_with_source_variants(
            '/not/an/executable/program',
            ArrangementWithSds(),
            Expectation(validation_pre_sds=IS_VALIDATION_ERROR))


IS_VALIDATION_ERROR = asrt.is_instance_with(str, asrt.casted_to_boolean_is(True))


class RelativityOptionConfigurationForDefaultRelativity(rel_opt_conf.RelativityOptionConfiguration):
    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        raise NotImplementedError('should not be used by these tests')

    def __init__(self):
        super().__init__('')

    @property
    def exists_pre_sds(self) -> bool:
        return True

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path().cwd()

    def populator_for_relativity_option_root(self, contents: fs.DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForHomeContents(contents)


def relativity_options(symbol_name: str) -> list:
    return [
        RelativityOptionConfigurationForDefaultRelativity(),
        rel_opt_conf.RelativityOptionConfigurationForRelAct(),
        rel_opt_conf.RelativityOptionConfigurationForRelTmp(),
        rel_opt_conf.RelativityOptionConfigurationForRelSymbol(
            RelOptionType.REL_TMP,
            sut.REL_OPTION_ARG_CONF.options.accepted_relativity_variants,
            symbol_name=symbol_name),
        rel_opt_conf.RelativityOptionConfigurationForRelSymbol(
            RelOptionType.REL_HOME,
            sut.REL_OPTION_ARG_CONF.options.accepted_relativity_variants,
            symbol_name=symbol_name),
    ]


RELATIVITY_OPTIONS = relativity_options('EXECUTABLE_FILE_SYMBOL_NAME')

python_program_that_exits_with_code_0 = 'exit(0)'
EXECUTABLE_FILE_THAT_EXITS_WITH_CODE_0 = fs.python_executable_file('executable-file',
                                                                   python_program_that_exits_with_code_0)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
