from exactly_lib.help.concepts.concept_structure import ConceptDocumentation
from exactly_lib.help.program_modes.test_case.instruction_documentation import InstructionDocumentation
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.description import Description
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc


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
    def __init__(self,
                 name: str):
        self._name_formats = formatting.SectionName(name)

    @property
    def name(self) -> formatting.SectionName:
        return self._name_formats

    def purpose(self) -> Description:
        raise NotImplementedError()

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
        raise NotImplementedError()

    @property
    def is_phase_with_instructions(self) -> bool:
        raise NotImplementedError()

    @property
    def instruction_set(self) -> SectionInstructionSet:
        """
        :return: None if this phase does not have instructions.
        """
        raise NotImplementedError()

    @property
    def see_also(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return []


class ConceptsHelp(tuple):
    def __new__(cls,
                concepts: iter):
        """
        :type concepts: [`ConceptDocumentation`]
        """
        return tuple.__new__(cls, (list(concepts),))

    @property
    def all_concepts(self) -> list:
        """
        :type: [`ConceptDocumentation`]
        """
        return self[0]

    def lookup_by_name_in_singular(self, concept_name: str) -> ConceptDocumentation:
        matches = list(filter(lambda c: c.name().singular == concept_name, self.all_concepts))
        if not matches:
            raise KeyError('Not a concept: ' + concept_name)
        return matches[0]