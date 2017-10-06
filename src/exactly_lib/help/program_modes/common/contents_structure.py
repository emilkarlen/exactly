from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.description import Description


class SectionInstructionSet(tuple):
    def __new__(cls,
                instruction_descriptions: iter):
        """
        :type instruction_descriptions: [`InstructionDocumentation`]
        """
        description_list = list(instruction_descriptions)
        description_list.sort(key=InstructionDocumentation.instruction_name)
        return tuple.__new__(cls, (description_list,))

    @property
    def instruction_descriptions(self) -> list:
        """
        :type: [`InstructionDocumentation`]
        """
        return self[0]

    @property
    def name_2_description(self) -> dict:
        return dict(map(lambda description: (description.instruction_name(), description),
                        self.instruction_descriptions))


class SectionDocumentation:
    """
    Documentation about a section in a "section document".
    """

    def __init__(self, name: str):
        self._name_formats = formatting.SectionName(name)

    @property
    def name(self) -> formatting.SectionName:
        return self._name_formats

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
        raise NotImplementedError()

    @property
    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """

        return []
