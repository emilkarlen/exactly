from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help_texts.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.document import SectionContents


class _SymbolConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(SYMBOL_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = normalize_and_parse(_REST_DESCRIPTION)
        sub_sections = []
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs,
                                                          sub_sections))

    def _see_also_cross_refs(self) -> list:
        return [
        ]


SYMBOL_CONCEPT = _SymbolConcept()

_REST_DESCRIPTION = """\
The symbol functionality is under development,
and therefore, documentation is limited.
"""
