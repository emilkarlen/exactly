import unittest

from exactly_lib.instructions.assert_ import exitcode as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, equivalent_source_variants__with_source_check
from exactly_lib_test.test_resources.execution import utils
from exactly_lib_test.test_resources.parse import remaining_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestParseAndExecuteTwoArguments),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_invalid_syntax(self):
        test_cases = [
            ' <> 1',
            ' = a',
            '',
            'a b c',
            'a',
            '-1',
            '256',
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            with self.subTest(msg=instruction_argument):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)

    def test_valid_syntax(self):
        parser = sut.Parser()
        actual_instruction = parser.parse(remaining_source('1'))
        self.assertIsInstance(actual_instruction,
                              AssertPhaseInstruction)


class TestParseAndExecuteTwoArguments(instruction_check.TestCaseBase):
    def test(self):
        test_cases = [
            (_actual_exitcode(0), ' =  72', _IS_FAIL),
            (_actual_exitcode(72), ' =  72', _IS_PASS),

            (_actual_exitcode(72), ' !  72', _IS_FAIL),
            (_actual_exitcode(72), ' !  73', _IS_PASS),

            (_actual_exitcode(72), ' <  28', _IS_FAIL),
            (_actual_exitcode(72), ' <  72', _IS_FAIL),
            (_actual_exitcode(72), ' <  87', _IS_PASS),

            (_actual_exitcode(72), ' <= 28', _IS_FAIL),
            (_actual_exitcode(72), ' <= 72', _IS_PASS),
            (_actual_exitcode(72), ' <= 87', _IS_PASS),

            (_actual_exitcode(72), ' > 28', _IS_PASS),
            (_actual_exitcode(72), ' > 72', _IS_FAIL),
            (_actual_exitcode(72), ' > 87', _IS_FAIL),

            (_actual_exitcode(72), ' >= 28', _IS_PASS),
            (_actual_exitcode(72), ' >= 72', _IS_PASS),
            (_actual_exitcode(72), ' >= 87', _IS_FAIL),
        ]
        for arrangement, instr_arg, expectation in test_cases:
            with self.subTest(msg=instr_arg):
                for source in equivalent_source_variants__with_source_check(self, instr_arg):
                    self._run(
                        source,
                        arrangement,
                        expectation,
                    )

    def _run(self,
             source: ParseSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


def _actual_exitcode(actual: int) -> ArrangementPostAct:
    return ArrangementPostAct(act_result_producer=ActResultProducerFromActResult(utils.ActResult(exitcode=actual)))


_IS_PASS = is_pass()
_IS_FAIL = Expectation(main_result=pfh_check.is_fail())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
