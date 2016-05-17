import enum

from exactly_lib.util import line_source


class Instruction:
    """
    Base class for an element of a phase that is not a comment.
    """
    pass


class ElementType(enum.Enum):
    EMPTY = 1
    COMMENT = 2
    INSTRUCTION = 3


class SectionContentElement:
    """
    Element of the contents of a section: either a comment or an instruction.

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
    def instruction(self) -> Instruction:
        """
        Precondition: Element type is INSTRUCTION.
        """
        return self._instruction


def new_empty_e(source: line_source.LineSequence) -> SectionContentElement:
    return SectionContentElement(ElementType.EMPTY,
                                 source,
                                 None)


def new_comment_e(source: line_source.LineSequence) -> SectionContentElement:
    return SectionContentElement(ElementType.COMMENT,
                                 source,
                                 None)


def new_instruction_e(source: line_source.LineSequence,
                      instruction: Instruction) -> SectionContentElement:
    return SectionContentElement(ElementType.INSTRUCTION,
                                 source,
                                 instruction)


class SectionContents:
    """
    A sequence/list of SectionContentElement:s.
    """

    def __init__(self, elements: tuple):
        """
        :param elements: List of `SectionContentElement`.
        """
        self._elements = elements

    @property
    def elements(self) -> tuple:
        return self._elements


def new_empty_section_contents() -> SectionContents:
    return SectionContents(())


class Document:
    """
    The result of parsing a file without encountering any errors.
    """

    def __init__(self, section2elements: dict):
        """
        :param section2elements dictionary str -> PhaseContents
        """
        self._section2elements = section2elements

    @property
    def section(self) -> frozenset:
        return self._section2elements.keys()

    def elements_for_section(self, phase_name: str) -> SectionContents:
        return self._section2elements[phase_name]

    def elements_for_section_or_empty_if_phase_not_present(self, phase_name: str) -> SectionContents:
        if phase_name in self._section2elements:
            return self.elements_for_section(phase_name)
        else:
            return SectionContents(())


def empty_document() -> Document:
    return Document({})
