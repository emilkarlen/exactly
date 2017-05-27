import unittest

from exactly_lib.instructions.multi_phase_instructions import run as sut
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.assertion_utils import sub_process_result_check as spr_check
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import home_and_sds_test
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
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


def py_pgm_that_exits_with_value_on_command_line(stderr_output) -> str:
    return """
import sys

sys.stderr.write('{}');
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
