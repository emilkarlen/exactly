import os
import unittest

from exactly_lib.help_texts.file_ref import REL_TMP_OPTION
from exactly_lib.instructions.multi_phase_instructions import run as sut
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_from_parts_for_executing_sub_process import \
    TheInstructionEmbryo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case import os_services
from exactly_lib.test_case.phases.common import PhaseLoggingPaths, InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_utils import sub_process_execution as spe
from exactly_lib_test.instructions.test_resources.assertion_utils import sub_process_result_check as spr_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import contents_in
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.parse import single_line_source
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import home_and_sds_test
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecuteProgramWithShellArgumentList),
        unittest.makeSuite(TestExecuteInterpret),
        unittest.makeSuite(TestSource),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name',
                                                                            'single line description')),
    ])


class ExecuteAction(HomeAndSdsAction):
    def __init__(self, instruction_embryo: TheInstructionEmbryo):
        self.instruction_embryo = instruction_embryo

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds) -> spe.ResultAndStderr:
        return self.instruction_embryo.main(InstructionEnvironmentForPostSdsStep(environment.hds,
                                                                                 dict(os.environ),
                                                                                 environment.sds,
                                                                                 'the-phase'),
                                            PhaseLoggingPaths(environment.sds.log_dir, 'the-phase'),
                                            os_services.new_default())


class TestCaseBase(home_and_sds_test.TestCaseBase):
    def _check_single_line_arguments_with_source_variants(self,
                                                          instruction_argument: str,
                                                          arrangement: home_and_sds_test.Arrangement,
                                                          expectation: home_and_sds_test.Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            embryo_parser = sut.embryo_parser('instruction-name')
            instruction_embryo = embryo_parser.parse(source)
            action = ExecuteAction(instruction_embryo)
            self._check(action, arrangement, expectation)

    def _check_source(self,
                      source: ParseSource,
                      arrangement: home_and_sds_test.Arrangement,
                      expectation: home_and_sds_test.Expectation):
        instruction_embryo = sut.embryo_parser('instruction-name').parse(source)
        action = ExecuteAction(instruction_embryo)
        self._check(action, arrangement, expectation)


class TestExecuteProgramWithShellArgumentList(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_executing_program_via_command_line('exit(0)'),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.is_success_result(0,
                                                                                             None)))

    def test_double_dash_should_invoke_execute(self):
        argument = py_exe.command_line_for_executing_program_via_command_line(
            'exit(0)',
            args_directly_after_interpreter='--')
        self._check_single_line_arguments_with_source_variants(
            argument,
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.is_success_result(0,
                                                                                             None)))

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_executing_program_via_command_line('exit(1)'),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.is_success_result(1,
                                                                                             '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write(\\"on stderr\\"); exit(2)'
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_executing_program_via_command_line(python_program),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.is_success_result(2,
                                                                                             'on stderr')))

    def test_invalid_executable(self):
        self._check_single_line_arguments_with_source_variants(
            '/not/an/executable/program',
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.IsFailure()))


class TestExecuteInterpret(TestCaseBase):
    def test_check_zero_exit_code__rel_home_default(self):
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_arguments([sut.INTERPRET_OPTION,
                                               'exit-with-value-on-command-line.py',
                                               0]),
            home_and_sds_test.Arrangement(
                home_dir_contents_before=DirContents([
                    File('exit-with-value-on-command-line.py',
                         py_pgm_that_exits_with_value_on_command_line(''))])),
            home_and_sds_test.Expectation(
                expected_action_result=spr_check.is_success_result(0,
                                                                   None),

            )
        )

    def test_check_zero_exit_code__rel_tmp(self):
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_arguments([sut.INTERPRET_OPTION,
                                               REL_TMP_OPTION,
                                               'exit-with-value-on-command-line.py',
                                               0]),
            home_and_sds_test.Arrangement(
                sds_contents_before=contents_in(RelSdsOptionType.REL_TMP,
                                                DirContents([
                                                    File('exit-with-value-on-command-line.py',
                                                         py_pgm_that_exits_with_value_on_command_line(''))]))),
            home_and_sds_test.Expectation(
                expected_action_result=spr_check.is_success_result(0,
                                                                   None)),
        )

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            py_exe.command_line_for_arguments([sut.INTERPRET_OPTION,
                                               'exit-with-value-on-command-line.py',
                                               2]),
            home_and_sds_test.Arrangement(
                home_dir_contents_before=DirContents([
                    File('exit-with-value-on-command-line.py',
                         py_pgm_that_exits_with_value_on_command_line('on stderr'))])),
            home_and_sds_test.Expectation(
                expected_action_result=spr_check.is_success_result(2,
                                                                   'on stderr'),

            )
        )

    def test_invalid_executable(self):
        argument = '/not/an/executable/program {} {} {}'.format(sut.INTERPRET_OPTION,
                                                                'exit-with-value-on-command-line.py',
                                                                0)
        self._check_single_line_arguments_with_source_variants(
            argument,
            home_and_sds_test.Arrangement(
                home_dir_contents_before=DirContents([
                    File('exit-with-value-on-command-line.py',
                         py_pgm_that_exits_with_value_on_command_line(''))])),
            home_and_sds_test.Expectation(
                expected_action_result=spr_check.IsFailure(),

            ))


class TestSource(TestCaseBase):
    def test_parse_should_fail_when_no_source_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.SetupParser().parse(single_line_source('EXECUTABLE %s' % sut.SOURCE_OPTION))

    def test_check_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            self._python_interpreter_for_source_on_command_line('exit(0)'),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.is_success_result(0,
                                                                                             None)))

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            self._python_interpreter_for_source_on_command_line('exit(1)'),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.is_success_result(1,
                                                                                             '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write("on stderr"); exit(2)'
        self._check_single_line_arguments_with_source_variants(
            self._python_interpreter_for_source_on_command_line(python_program),
            home_and_sds_test.Arrangement(),
            home_and_sds_test.Expectation(expected_action_result=spr_check.is_success_result(2,
                                                                                             'on stderr')))

    @staticmethod
    def _python_interpreter_for_source_on_command_line(argument: str) -> str:
        return '( {} ) {} {}'.format(py_exe.interpreter_that_executes_argument(),
                                     sut.SOURCE_OPTION,
                                     argument)


def py_pgm_that_exits_with_value_on_command_line(stderr_output) -> str:
    return """
import sys

sys.stderr.write('{}');
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
