from shelltest.general import line_source


class Instruction:
    """
    Base class for an element of a phase that is not a comment.
    """
    pass


class PhaseContentElement:
    """
    Element of the contents of a phase: either a comment or an instruction.

    Construct elements with either new_comment_element or new_instruction_element.
    """

    def __init__(self,
                 source_line: line_source.Line,
                 instruction: Instruction):
        self._source_line = source_line
        self._instruction = instruction

    @property
    def source_line(self) -> line_source.Line:
        return self._source_line

    @property
    def is_instruction(self) -> bool:
        return self._instruction

    @property
    def is_comment(self) -> bool:
        return not self.is_instruction

    @property
    def instruction(self) -> Instruction:
        """
        Precondition: is_instruction
        """
        return self._instruction


def new_comment_element(source_line: line_source.Line) -> PhaseContentElement:
    return PhaseContentElement(source_line, None)


def new_instruction_element(source_line: line_source.Line,
                            executor: Instruction) -> PhaseContentElement:
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

    def __init__(self, phase2elements: dict):
        """
        :param phase2elements dictionary str -> PhaseContents
        """
        self._phase2elements = phase2elements

    @property
    def phases(self) -> frozenset:
        return self._phase2elements.keys()

    def elements_for_phase(self, phase_name: str) -> PhaseContents:
        return self._phase2elements[phase_name]
