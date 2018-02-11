from typing import Sequence, Dict, Callable, List, Iterable

from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help_texts import doc_format
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure.core import StringText
from exactly_lib.util.textformat.structure.paragraph import Paragraph


class SectionInstructionSet(tuple):
    def __new__(cls, instruction_descriptions: Iterable[InstructionDocumentation]):
        description_list = list(instruction_descriptions)
        description_list.sort(key=InstructionDocumentation.instruction_name)
        return tuple.__new__(cls, (description_list,))

    @property
    def instruction_documentations(self) -> Sequence[InstructionDocumentation]:
        return self[0]

    @property
    def name_2_description(self) -> Dict[str, InstructionDocumentation]:
        return {
            description.instruction_name(): description
            for description in self.instruction_documentations
        }


class InstructionGroup(tuple):
    """A grouping of instructions, to be listed under a common header."""

    def __new__(cls,
                header: str,
                identifier: str,
                description_paragraphs: Sequence[Paragraph],
                instruction_documentations: Sequence[InstructionDocumentation]):
        return tuple.__new__(cls, (header,
                                   identifier,
                                   description_paragraphs,
                                   instruction_documentations))

    @property
    def header(self) -> str:
        return self[0]

    @property
    def identifier(self) -> str:
        return self[1]

    @property
    def description_paragraphs(self) -> Sequence[Paragraph]:
        return self[2]

    @property
    def instruction_documentations(self) -> Sequence[InstructionDocumentation]:
        return self[3]


class SectionDocumentation:
    """
    Documentation about a section in a "section document".
    """

    def __init__(self, name: str):
        self._name_formats = formatting.SectionName(name)

    @property
    def name(self) -> formatting.SectionName:
        return self._name_formats

    @property
    def syntax_name_text(self) -> StringText:
        return doc_format.section_name_text(self.name)

    def purpose(self) -> Description:
        raise NotImplementedError()

    def is_mandatory(self) -> bool:
        raise NotImplementedError()

    @property
    def has_instructions(self) -> bool:
        raise NotImplementedError()

    @property
    def instruction_set(self) -> SectionInstructionSet:
        """
        :return: None if this phase does not have instructions.
        """
        raise NotImplementedError('abstract method')

    @property
    def instruction_group_by(self) -> Callable[[List[InstructionDocumentation]], List[InstructionGroup]]:
        """
        A function group instructions for presentation.

        Should return a list with at least one element = one group.

        :return:  None if the instructions have no grouping.
        """
        return None

    @property
    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return []
