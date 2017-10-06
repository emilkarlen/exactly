from exactly_lib.help.entities.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help_texts.entity import concepts
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.document import SectionContents


class _TypeConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.TYPE_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = normalize_and_parse(_REST_DESCRIPTION)
        sub_sections = []
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs,
                                                          sub_sections))

    def see_also_targets(self) -> list:
        return [
        ]


TYPE_CONCEPT = _TypeConcept()

_REST_DESCRIPTION = """\
The type functionality is under development,
and therefore, documentation is limited.
"""
