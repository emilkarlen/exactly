import unittest

from exactly_lib.definitions.primitives import program as program_primitives
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import contents_in
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.test_resources import relativity_options
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.file_structure import python_executable_file
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.programs.py_programs import py_pgm_that_exits_with_1st_value_on_command_line
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
                               TestZeroExitCode,
                               TestNonZeroExitCode,
                               TestNonZeroExitCodeAndIgnoredExitCode,
                               TestSuccessfulExecutionViaSymbolReference,
                               TestFailingValidationOfAbsolutePath,
                               TestFailingValidationOfRelHdsPath,
                               TestFailingValidationOfRelTmpPath,
                               TestSuccessfulValidation,
                               TestFailingValidationOfRelSymbol,
                               TestSuccessAndSymbolUsages,
                               TestInvalidSyntaxSuperfluousArguments,
                           ])


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.conf))


class TestZeroExitCode(TestCaseBase):
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
                       py_pgm_that_exits_with_1st_value_on_command_line(output_to_stderr))

        py_file_rel_opt_conf = relativity_options.conf_rel_any(RelOptionType.REL_TMP)
        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        program_that_executes_py_pgm_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_THAT_EXECUTES_PY_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
        )

        symbols = program_that_executes_py_pgm_symbol.symbol_table

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
                               symbols=symbols
                           ),
                           self.conf.expect_success(
                               symbol_usages=asrt.matches_sequence([
                                   program_that_executes_py_pgm_symbol.reference_assertion
                               ])
                           ),
                           )


class TestNonZeroExitCode(TestCaseBase):
    def runTest(self):
        self.conf.run_test(self,
                           single_line_source(py_exe.command_line_for_executing_program_via_command_line('exit(1)')),
                           self.conf.arrangement(),
                           self.conf.expect_failure_of_main(),
                           )


class TestNonZeroExitCodeAndIgnoredExitCode(TestCaseBase):
    def runTest(self):
        argument_elements = (
            ab.OptionArgument(program_primitives.WITH_IGNORED_EXIT_CODE_OPTION_NAME).as_argument_elements
                .followed_by(pgm_args.interpret_py_source_elements('exit(1)'))
        )
        self.conf.run_test(
            self,
            argument_elements.as_remaining_source,
            self.conf.arrangement(),
            self.conf.expect_success(),
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
                DirContents([File.empty('existing-file.py')]))),
            self.conf.expect_success(),
        )


class TestInvalidSyntaxSuperfluousArguments(TestCaseBase):
    def runTest(self):
        parser = self.conf.parser()
        source = pgm_args.program_w_superfluous_args().as_remaining_source
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(ARBITRARY_FS_LOCATION_INFO,
                         source)


def source_for_interpreting(relativity: RelOptionType,
                            file_name: str) -> ParseSource:
    return pgm_args.program(pgm_args.interpret_py_source_file(
        args.path_rel_opt(file_name,
                          relativity))).as_remaining_source
