from exactly_lib.common.help.instruction_documentation import InstructionDocumentation
from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import document as doc, structures as docs


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
                 name: str,
                 section_concept_name: str):
        self._name_formats = formatting.SectionName(name)
        self._section_concept_name = section_concept_name

    @property
    def name(self) -> formatting.SectionName:
        return self._name_formats

    def purpose(self) -> Description:
        raise NotImplementedError()

    def is_mandatory(self) -> bool:
        raise NotImplementedError()

    def render(self, environment: RenderingEnvironment) -> doc.SectionContents:
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
    def see_also_items(self) -> list:
        """
        :rtype: [`SeeAlsoItem`]
        """
        return [CrossReferenceIdSeeAlsoItem(x) for x in self.see_also]

    @property
    def see_also(self) -> list:
        """
        :rtype [`CrossReferenceTarget`]
        """
        return []

    def _default_section_info(self, default_section_name: str) -> list:
        ret_val = []
        if self.name.plain == default_section_name:
            ret_val.append(default_section_para(self._section_concept_name))
        return ret_val

    def _mandatory_info_para(self):
        mandatory_or_optional = 'mandatory' if self.is_mandatory() else 'optional'
        return docs.para('The {} {} is {}.'.format(self.name,
                                                   self._section_concept_name,
                                                   mandatory_or_optional))


def default_section_para(section_concept_name: str = 'section') -> docs.ParagraphItem:
    return docs.para(_DEFAULT_SECTION_STRING.format(section_concept_name=section_concept_name))


_DEFAULT_SECTION_STRING = """This is the default {section_concept_name}."""
