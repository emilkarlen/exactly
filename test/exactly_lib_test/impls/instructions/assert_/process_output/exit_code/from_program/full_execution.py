import unittest

from exactly_lib.impls.types.condition.comparators import EQ, NE, LT
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.expectations import IS_PASS, \
    IS_FAIL
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    CHECKER
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.int_matchers import of_op, \
    of_neg_op
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    ProgramOfPythonInterpreterAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestApplicationOfMatcher(),
    ])


class TestApplicationOfMatcher(unittest.TestCase):
    def runTest(self):
        test_cases = [
            (_actual_exitcode(0), of_op(EQ, 72), IS_FAIL),
            (_actual_exitcode(72), of_op(EQ, 72), IS_PASS),

            (_actual_exitcode(72), of_neg_op(EQ, 72), IS_FAIL),
            (_actual_exitcode(72), of_neg_op(EQ, 73), IS_PASS),

            (_actual_exitcode(72), of_op(NE, 72), IS_FAIL),
            (_actual_exitcode(72), of_op(NE, 73), IS_PASS),

            (_actual_exitcode(72), of_op(LT, 28), IS_FAIL),
            (_actual_exitcode(72), of_op(LT, 72), IS_FAIL),
            (_actual_exitcode(72), of_op(LT, 87), IS_PASS),
        ]
        for program_syntax, matcher_syntax, expectation in test_cases:
            instruction_syntax = InstructionArguments(program_syntax, matcher_syntax, )
            with self.subTest(instruction_syntax.as_str__default()):
                CHECKER.check__abs_stx__source_variants(
                    self,
                    instruction_syntax,
                    ArrangementPostAct2(),
                    expectation,
                )


def _actual_exitcode(exit_code: int) -> ProgramAbsStx:
    return ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
        py_programs.py_pgm_with_stdout_stderr_exit_code__single_line(
            exit_code=exit_code
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
