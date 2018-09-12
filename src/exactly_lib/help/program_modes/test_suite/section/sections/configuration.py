from typing import List

from exactly_lib.definitions.test_case import phase_names
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_suite.section.common import \
    TestSuiteSectionDocumentationForSectionWithInstructions
from exactly_lib.help.program_modes.test_suite.section.sections import test_case_phase_sections
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class ConfigurationSectionDocumentation(TestSuiteSectionDocumentationForSectionWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)
        self._tp = TextParser({
            'conf_phase': phase_names.CONFIGURATION_PHASE_NAME,
        })

    def instructions_section_header(self) -> docs.Text:
        return docs.text('Additional instructions')

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        return []

    def is_mandatory(self) -> bool:
        return False

    def contents_description(self) -> List[ParagraphItem]:
        return self._tp.fnap(_CONTENTS_DESCRIPTION)

    def purpose(self) -> Description:
        paragraphs = self._tp.fnap(_PURPOSE_REST_TEXT)
        paragraphs += test_case_phase_sections.insertion_position_description(self._section_name, True)
        return Description(self._tp.text(_PURPOSE_SINGLE_LINE_DESCRIPTION_TEXT),
                           paragraphs)


_PURPOSE_SINGLE_LINE_DESCRIPTION_TEXT = 'Common configuration, for all test cases in the suite'

_PURPOSE_REST_TEXT = """\
Corresponds to the {conf_phase:syntax} test case phase,
with some additional configuration possibilities.
"""

_CONTENTS_DESCRIPTION = """\
Sequence of instructions - same as the {conf_phase:syntax} test case phase.
"""
