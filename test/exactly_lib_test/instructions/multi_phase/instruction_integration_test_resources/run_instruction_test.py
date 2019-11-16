import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import contents_in
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import program_resolvers
from exactly_lib_test.test_case_utils.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.test_resources import relativity_options
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.file_structure import empty_file, python_executable_file
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.programs.py_programs import py_pgm_that_exits_with_value_on_command_line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Configuration(ConfigurationBase):
    def expect_failure_because_specified_file_under_sds_is_missing(
            self,
            symbol_usages: ValueAssertion = asrt.is_empty_sequence):
        raise NotImplementedError()


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestSuccessfulExecution,
                               TestFailingExecution,
                               TestSuccessfulExecutionViaSymbolReference,
                               TestFailingValidationOfAbsolutePath,
                               TestFailingValidationOfRelHdsPath,
                               TestFailingValidationOfRelTmpPath,
                               TestSuccessfulValidation,
                               TestFailingValidationOfRelSymbol,
                               TestSuccessAndSymbolUsages,
                           ])


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


class TestSuccessfulExecutionViaSymbolReference(TestCaseBase):
    def runTest(self):
        output_to_stderr = 'on stderr'
        py_file = File('exit-with-value-on-command-line.py',
                       py_pgm_that_exits_with_value_on_command_line(output_to_stderr))

        py_file_rel_opt_conf = relativity_options.conf_rel_any(RelOptionType.REL_TMP)
        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        program_that_executes_py_pgm_symbol = NameAndValue(
            'PROGRAM_THAT_EXECUTES_PY_FILE',
            program_resolvers.interpret_py_source_file_that_must_exist(py_file_conf.path_resolver)
        )

        symbols_dict = SymbolTable({
            program_that_executes_py_pgm_symbol.name:
                symbol_utils.container(program_that_executes_py_pgm_symbol.value),
        })

        instruction_arguments = [
            pgm_args.symbol_ref_command_line(program_that_executes_py_pgm_symbol.name),
            0,
        ]
        self.conf.run_test(self,
                           single_line_source(args.sequence(instruction_arguments).as_str),
                           self.conf.arrangement(
                               home_or_sds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                                   DirContents([py_file])
                               ),
                               symbols=symbols_dict
                           ),
                           self.conf.expect_success(
                               symbol_usages=asrt.matches_sequence([
                                   asrt_pgm.is_program_reference_to(program_that_executes_py_pgm_symbol.name)
                               ])
                           ),
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


class TestFailingValidationOfRelHdsPath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(RelOptionType.REL_HDS_CASE, 'non-existing-file.py'),
            self.conf.arrangement(),
            self.conf.expect_failing_validation_pre_sds(),
        )


class TestFailingValidationOfRelTmpPath(TestCaseBase):
    def runTest(self):
        self.conf.run_test(
            self,
            source_for_interpreting(RelOptionType.REL_TMP, 'non-existing-file.py'),
            self.conf.arrangement(),
            self.conf.expect_failure_because_specified_file_under_sds_is_missing(),
        )


class TestFailingValidationOfRelSymbol(TestCaseBase):
    def runTest(self):
        symbol_name = 'SYMBOL_NAME'
        relativity_option = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_TMP,
            symbol_name,
            syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants)
        self.conf.run_test(
            self,
            single_line_source('{relativity_option} non-existing-file'.format(
                relativity_option=relativity_option.option_argument)),
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
            syntax_elements.REL_OPTION_ARG_CONF.options.accepted_relativity_variants)
        self.conf.run_test(
            self,
            single_line_source('{relativity_option} {executable_file}'.format(
                relativity_option=relativity_option.option_argument,
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
            source_for_interpreting(RelOptionType.REL_TMP, 'existing-file.py'),
            self.conf.arrangement(sds_contents_before_main=contents_in(
                RelSdsOptionType.REL_TMP,
                DirContents([empty_file('existing-file.py')]))),
            self.conf.expect_success(),
        )


def source_for_interpreting(relativity: RelOptionType,
                            file_name: str) -> ParseSource:
    return pgm_args.program(pgm_args.interpret_py_source_file(
        args.path_rel_opt(file_name,
                          relativity))).as_remaining_source
