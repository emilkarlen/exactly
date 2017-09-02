from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, Name
from exactly_lib.help_texts.entity.concepts import name_and_ref_target
from exactly_lib.util.description import DescriptionWithSubSections, single_line_description_with_sub_sections


class ConceptTestImpl(PlainConceptDocumentation):
    def __init__(self, singular_name: str):
        super().__init__(name_and_ref_target(Name(singular_name,
                                                  'plural of ' + singular_name),
                                             'single line description'))

    def purpose(self) -> DescriptionWithSubSections:
        return single_line_description_with_sub_sections('single line description')
