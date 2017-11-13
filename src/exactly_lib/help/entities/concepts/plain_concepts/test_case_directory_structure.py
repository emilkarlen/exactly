from exactly_lib import program_info
from exactly_lib.help.entities.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class _TcdsConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT_INFO)

        self._parser = TextParser({
            'HDS': formatting.concept_(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO),
            'HDS_description': concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.single_line_description_str,
            'SDS': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
            'SDS_description': concepts.SANDBOX_CONCEPT_INFO.single_line_description_str,
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
            concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO.cross_reference_target,
            concepts.SANDBOX_CONCEPT_INFO.cross_reference_target,
        ]

    def _fnap(self, template: str) -> list:
        return self._parser.fnap(template)


TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT = _TcdsConcept()

_MAIN_DESCRIPTION_REST = """\
Consists of two sets of directories:


  * {HDS}
  
    {HDS_description}
  
  * {SDS}
  
    {SDS_description}



{program_name} has support for referring to all of these directories.
"""
