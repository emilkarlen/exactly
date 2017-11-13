import pathlib
import unittest

from exactly_lib.act_phase_setups import null as sut
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSuccessfulExecution(),
        TestNoSymbolsAreReferenced(),
    ])


def _instructions_for_executing_py_file(src_path: pathlib.Path) -> list:
    cmd = py_exe.command_line_for_interpreting(src_path)
    return [instr([cmd])]


class TestSuccessfulExecution(unittest.TestCase):
    def runTest(self):
        expected_output = pr.sub_process_result(exitcode=asrt.equals(0),
                                                stdout=asrt.equals(''),
                                                stderr=asrt.equals(''))
        cases = [
            (
                'no act phase contents',
                []
            ),
            (
                'act phase contents of just comments',
                [instr([LINE_COMMENT_MARKER + ' a comment'])]
            ),
            (
                'act phase contents of just comments and empty lines',
                [instr([LINE_COMMENT_MARKER + ' a comment',
                        '',
                        LINE_COMMENT_MARKER + ' a second comment',
                        ])]
            ),
            (
                'act phase contents with non-comment and non-empty line',
                [instr(['not a comment and not empty',
                        ])]
            ),
        ]
        executor_constructor = sut.Constructor()
        for case_name, act_phase_instructions in cases:
            with self.subTest(case_name=case_name):
                arrangement = Arrangement()
                expectation = Expectation(sub_process_result_from_execute=expected_output)
                check_execution(self,
                                executor_constructor,
                                act_phase_instructions,
                                arrangement,
                                expectation)


class TestNoSymbolsAreReferenced(unittest.TestCase):
    def runTest(self):
        cases = [
            (
                'no act phase contents',
                []
            ),
            (
                'act phase contents with a line that has symbol reference syntax',
                [instr([symbol_reference_syntax_for_name('symbol_name')])]
            ),
        ]
        executor_constructor = sut.Constructor()
        for case_name, act_phase_instructions in cases:
            with self.subTest(case_name=case_name):
                arrangement = Arrangement()
                expectation = Expectation(symbol_usages=asrt.is_empty_list)
                check_execution(self,
                                executor_constructor,
                                act_phase_instructions,
                                arrangement,
                                expectation)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
