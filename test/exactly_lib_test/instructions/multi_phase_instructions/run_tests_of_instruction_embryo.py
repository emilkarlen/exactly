import pathlib
import unittest

from exactly_lib.help_texts.file_ref import REL_HOME_OPTION
from exactly_lib.instructions.multi_phase_instructions import run as sut
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.assertion_utils import sub_process_result_check as spr_check
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulatorForHomeContents, HomeOrSdsPopulator
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import home_and_sds_test
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingValidationBecauseExecutableDoesNotExist),
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


class TestFailingValidationBecauseExecutableDoesNotExist(TestCaseBase):
    def test_execute(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file'.format(
                relativity_option=relativity_option_conf.option_string)

            expected_symbol_usage = asrt.matches_sequence(
                relativity_option_conf.symbol_usage_expectation_assertions())

            expectation = self._expect_validation_error(relativity_option_conf,
                                                        expected_symbol_usage)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols_in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_interpret(self):
        existing_file_to_interpret = 'existing-file-to-interpret.src'
        home_dir_contents = file_structure.DirContents([file_structure.empty_file(existing_file_to_interpret)])
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {interpret_option}' \
                       ' {rel_home_option} {existing_file}'.format(
                relativity_option=relativity_option_conf.option_string,
                interpret_option=sut.INTERPRET_OPTION,
                rel_home_option=REL_HOME_OPTION,
                existing_file=existing_file_to_interpret,
            )

            expected_symbol_usage = asrt.matches_sequence(
                relativity_option_conf.symbol_usage_expectation_assertions())

            expectation = self._expect_validation_error(relativity_option_conf,
                                                        expected_symbol_usage)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols_in_arrangement(),
                home_contents=home_dir_contents,
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def test_source(self):
        for relativity_option_conf in RELATIVITY_OPTIONS:
            argument = '{relativity_option} non-existing-file {source_option} irrelevant-source'.format(
                relativity_option=relativity_option_conf.option_string,
                source_option=sut.SOURCE_OPTION,
            )

            expected_symbol_usage = asrt.matches_sequence(
                relativity_option_conf.symbol_usage_expectation_assertions())

            expectation = self._expect_validation_error(relativity_option_conf,
                                                        expected_symbol_usage)

            arrangement = ArrangementWithSds(
                symbols=relativity_option_conf.symbols_in_arrangement(),
            )
            with self.subTest(msg='option=' + relativity_option_conf.test_case_description):
                self._check_single_line_arguments_with_source_variants(argument,
                                                                       arrangement,
                                                                       expectation)

    def _expect_validation_error(self,
                                 relativity_option_conf: rel_opt_conf.RelativityOptionConfiguration,
                                 expected_symbol_usage: asrt.ValueAssertion) -> embryo_check.Expectation:
        if relativity_option_conf.exists_pre_sds:
            return embryo_check.Expectation(
                validation_pre_sds=IS_VALIDATION_ERROR,
                symbol_usages=expected_symbol_usage,
            )
        else:
            return embryo_check.Expectation(
                validation_post_sds=IS_VALIDATION_ERROR,
                symbol_usages=expected_symbol_usage,
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

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForHomeContents(contents)


RELATIVITY_OPTIONS = [
    RelativityOptionConfigurationForDefaultRelativity(),
    rel_opt_conf.RelativityOptionConfigurationForRelAct(),
    rel_opt_conf.RelativityOptionConfigurationForRelTmp(),
    rel_opt_conf.RelativityOptionConfigurationForRelSymbol(
        RelOptionType.REL_TMP,
        sut.REL_OPTION_ARG_CONF.options.accepted_relativity_variants,
        symbol_name='EXECUTABLE_FILE_SYMBOL_NAME'),
    rel_opt_conf.RelativityOptionConfigurationForRelSymbol(
        RelOptionType.REL_HOME,
        sut.REL_OPTION_ARG_CONF.options.accepted_relativity_variants,
        symbol_name='EXECUTABLE_FILE_SYMBOL_NAME'),
]


def py_pgm_that_exits_with_value_on_command_line(stderr_output) -> str:
    return """
import sys

sys.stderr.write('{}');
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
