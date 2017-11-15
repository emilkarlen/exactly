from exactly_lib import program_info
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class _HdsConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO)

        self._parser = TextParser({
            'HDS': concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.singular_name,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = []
        sub_sections = []
        rest_paragraphs += self._fnap(_MAIN_DESCRIPTION_REST)
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs, sub_sections))

    def see_also_targets(self) -> list:
        return [
        ]

    def _fnap(self, template: str) -> list:
        return self._parser.fnap(template)


HOME_DIRECTORY_STRUCTURE_CONCEPT = _HdsConcept()

_MAIN_DESCRIPTION_REST = """\
The {HDS} is where files that should
not be modified are located.

For example, the test case file, and the system under test (SUT).
"""
