import unittest

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.instructions.multi_phase_instructions import run
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelSdsOptionType
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.run_instruction_utils import source_for_interpreting
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import contents_in
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, python_executable_file
from exactly_lib_test.test_resources.parse import single_line_source
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Configuration(ConfigurationBase):
    def expect_failure_because_specified_file_under_sds_is_missing(
            self,
            symbol_usages: asrt.ValueAssertion = asrt.is_empty_list):
        raise NotImplementedError()


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.conf))


class TestSuccessfulExecution(TestCaseBase):
    def runTest(self):
        self.conf.run_test(self,
                           single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(0)')),
                           self.conf.arrangement(),
                           self.conf.expect_success(),
                           )


class TestFailingExecution(TestCaseBase):
    def runTest(self):
        self.conf.run_test(self,
                           single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                           self.conf.arrangement(),
                           self.conf.expect_failure_of_main(),
                           )


class TestFailingValidationOfAbsolutePath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            single_line_source('/absolute/path/to/program/that/does/not/exist'),
            self.conf.arrangement(),
            self.conf.expect_failing_validation_pre_sds(),
        )


class TestFailingValidationOfRelHomePath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(file_ref_texts.REL_HOME_CASE_OPTION, 'non-existing-file.py'),
            self.conf.arrangement(),
            self.conf.expect_failing_validation_pre_sds(),
        )


class TestFailingValidationOfRelTmpPath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(file_ref_texts.REL_TMP_OPTION, 'non-existing-file.py'),
            self.conf.arrangement(),
            self.conf.expect_failure_because_specified_file_under_sds_is_missing(),
        )


class TestFailingValidationOfRelSymbol(TestCaseBase):
    def runTest(self):
        symbol_name = 'SYMBOL_NAME'
        relativity_option = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_TMP,
            symbol_name,
            run.REL_OPTION_ARG_CONF.options.accepted_relativity_variants)
        self.conf.run_test(
            self,
            single_line_source('{relativity_option} non-existing-file'.format(
                relativity_option=relativity_option.option_string)),
            self.conf.arrangement(symbols=relativity_option.symbols.in_arrangement()),
            self.conf.expect_failure_because_specified_file_under_sds_is_missing(
                symbol_usages=relativity_option.symbols.usages_expectation(),
            ),
        )


class TestSuccessAndSymbolUsages(TestCaseBase):
    def runTest(self):
        executable_file_that_exits_with_code_0 = python_executable_file('executable-file',
                                                                        'exit(0)')
        symbol_name = 'SYMBOL_NAME'
        relativity_option = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_TMP,
            symbol_name,
            run.REL_OPTION_ARG_CONF.options.accepted_relativity_variants)
        self.conf.run_test(
            self,
            single_line_source('{relativity_option} {executable_file}'.format(
                relativity_option=relativity_option.option_string,
                executable_file=executable_file_that_exits_with_code_0.file_name)),
            self.conf.arrangement(
                home_or_sds_contents=relativity_option.populator_for_relativity_option_root(
                    DirContents([executable_file_that_exits_with_code_0])
                ),
                symbols=relativity_option.symbols.in_arrangement()),
            self.conf.expect_success(
                symbol_usages=relativity_option.symbols.usages_expectation(),
            ),
        )


class TestSuccessfulValidation(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(file_ref_texts.REL_TMP_OPTION, 'existing-file.py'),
            self.conf.arrangement(sds_contents_before_main=contents_in(
                RelSdsOptionType.REL_TMP,
                DirContents([empty_file('existing-file.py')]))),
            self.conf.expect_success(),
        )


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestSuccessfulExecution,
                               TestFailingExecution,
                               TestFailingValidationOfAbsolutePath,
                               TestFailingValidationOfRelHomePath,
                               TestFailingValidationOfRelTmpPath,
                               TestSuccessfulValidation,
                               TestFailingValidationOfRelSymbol,
                               TestSuccessAndSymbolUsages,
                           ])
