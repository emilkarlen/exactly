__author__ = 'emil'

from shelltest.phase_instr import line_source


class InstructionExecutor:
    """
    Abstract base class for the execution of a parsed source line/instruction.
    """
    def execute(self, phase_name: str, global_environment, phase_environment):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class PhaseContentElement:
    """
    Element of the contents of a phase: either a comment or an instruction.

    Construct elements with either new_comment_element or new_instruction_element.
    """

    def __init__(self,
                 source_line: line_source.Line,
                 executor: InstructionExecutor):
        self._source_line = source_line
        self._executor = executor

    @property
    def source_line(self) -> line_source.Line:
        return self._source_line

    @property
    def is_instruction(self) -> bool:
        return self._executor

    @property
    def is_comment(self) -> bool:
        return not self.is_instruction

    @property
    def executor(self) -> InstructionExecutor:
        """
        Precondition: is_instruction
        """
        return self._executor

    def execute(self, phase_name: str, global_environment, phase_environment):
        if self.is_instruction:
            self._executor.execute(phase_name,
                                   global_environment,
                                   phase_environment)


def new_comment_element(source_line: line_source.Line) -> PhaseContentElement:
    return PhaseContentElement(source_line, None)


def new_instruction_element(source_line: line_source.Line,
                            executor: InstructionExecutor) -> PhaseContentElement:
    return PhaseContentElement(source_line, executor)


class PhaseContents:
    """
    A sequence/list of PhaseContentElement:s.
    """

    def __init__(self, elements: tuple):
        """
        :param elements: List of PhaseContentElement.
        """
        self._elements = elements

    @property
    def elements(self) -> tuple:
        return self._elements


def new_empty_phase_contents() -> PhaseContents:
    return PhaseContents(())


class Document:
    """
    The result of parsing a file without encountering any errors.
    """

    def __init__(self, phase2instructions: dict):
        """
        :param phase2instructions dictionary str -> PhaseContents
        """
        self._phase2instructions = phase2instructions

    @property
    def phases(self) -> frozenset:
        return self._phase2instructions.keys()

    def instructions_for_phase(self, phase_name: str) -> PhaseContents:
        return self._phase2instructions[phase_name]

    def execute(self, global_environment, phases: iter):
        """
        Executes the given phases in the given order.
        :param global_environment: An environment passed to every Instruction.
        :param phases: [(phase_name: str, phase_environment)]
        List of phases to execute, and the environment to use for each phase.
        The phases are executed in the order they appear in the list (a phase may be executed more than
        one time). Phases that have no counterpart in the Document are silently ignored.
        :return:
        """
        for phase_name, phase_environment in phases:
            if phase_name in self._phase2instructions:
                instruction_sequence = self._phase2instructions[phase_name]
                for instruction in instruction_sequence.elements:
                    assert isinstance(instruction, PhaseContentElement)
                    instruction.execute(phase_name, global_environment, phase_environment)