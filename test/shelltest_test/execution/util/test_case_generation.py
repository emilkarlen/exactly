__author__ = 'emil'

from shelltest.phase_instr import model
from shelltest.phase_instr import line_source
from shelltest.exec_abs_syn import abs_syn_gen


class TestCaseGeneratorBase:
    """
    Base class for generation of Test Cases using dummy source lines.

    Generates and stores a single test case.

    The test case is build/generated only a single time.
    """

    def __init__(self):
        self.__previous_line_number = 0
        self.__test_case = None

    @property
    def test_case(self) -> abs_syn_gen.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> abs_syn_gen.TestCase:
        raise NotImplementedError()

    def _next_instruction_line(self, instruction: model.Instruction) -> model.PhaseContentElement:
        return model.new_instruction_element(
            self._next_line(),
            instruction)

    def _next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))
