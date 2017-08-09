from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib.help.program_modes.common.renderers import default_section_para
from exactly_lib.help.utils.rendering.section_contents_renderer import SectionContentsRenderer
from exactly_lib.util.textformat.structure import structures as docs


class SectionDocumentationRendererBase(SectionContentsRenderer):
    def __init__(self,
                 section_documentation: SectionDocumentation,
                 section_concept_name: str):
        self.__section_documentation = section_documentation
        self.__section_concept_name = section_concept_name

    def _default_section_info(self, default_section_name: str) -> list:
        ret_val = []
        if self.__section_documentation.name.plain == default_section_name:
            ret_val.append(default_section_para(self.__section_concept_name))
        return ret_val

    def _mandatory_info_para(self):
        mandatory_or_optional = 'mandatory' if self.__section_documentation.is_mandatory() else 'optional'
        return docs.para('The {} {} is {}.'.format(self.__section_documentation.name,
                                                   self.__section_concept_name,
                                                   mandatory_or_optional))
