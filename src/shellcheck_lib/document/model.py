import enum

from shellcheck_lib.general import line_source


class Instruction:
    """
    Base class for an element of a phase that is not a comment.
    """
    pass


class ElementType(enum.Enum):
    EMPTY = 1
    COMMENT = 2
    INSTRUCTION = 3


class PhaseContentElement:
    """
    Element of the contents of a phase: either a comment or an instruction.

    Construct elements with either new_comment_element or new_instruction_element.
    """

    def __init__(self,
                 element_type: ElementType,
                 source: line_source.LineSequence,
                 instruction: Instruction):
        self._element_type = element_type
        self._source = source
        self._instruction = instruction

    @property
    def source(self) -> line_source.LineSequence:
        return self._source

    @property
    def first_line(self) -> line_source.Line:
        return self._source.first_line

    @property
    def element_type(self) -> ElementType:
        return self._element_type

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


def new_empty_e(source: line_source.LineSequence) -> PhaseContentElement:
    return PhaseContentElement(ElementType.EMPTY,
                               source,
                               None)


def new_comment_e(source: line_source.LineSequence) -> PhaseContentElement:
    return PhaseContentElement(ElementType.COMMENT,
                               source,
                               None)


def new_instruction_e(source: line_source.LineSequence,
                      instruction: Instruction) -> PhaseContentElement:
    return PhaseContentElement(ElementType.INSTRUCTION,
                               source,
                               instruction)


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

    def elements_for_phase_or_empty_if_phase_not_present(self, phase_name: str) -> PhaseContents:
        if phase_name in self._phase2elements:
            return self.elements_for_phase(phase_name)
        else:
            return PhaseContents(())


def empty_document() -> Document:
    return Document({})
