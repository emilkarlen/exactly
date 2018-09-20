from typing import List

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.help.program_modes.test_suite.contents_structure.section_documentation import \
    TestSuiteSectionDocumentationBaseForSectionWithoutInstructions, TestSuiteSectionDocumentation
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def section_documentation(phase_name: str,
                          contents_is_inserted_before_case_contents: bool) -> TestSuiteSectionDocumentation:
    return _SectionThatIsIdenticalToTestCasePhase(phase_name, contents_is_inserted_before_case_contents)


class _SectionThatIsIdenticalToTestCasePhase(TestSuiteSectionDocumentationBaseForSectionWithoutInstructions):
    def __init__(self,
                 phase_name: str,
                 contents_is_inserted_before_case_contents: bool):
        super().__init__(phase_name)
        self._contents_is_inserted_before_case_contents = contents_is_inserted_before_case_contents
        self._tp = TextParser({
            'phase': self.section_info.name,
        })

    def contents_description(self) -> SectionContents:
        return self._tp.section_contents(_CONTENTS_DESCRIPTION)

    def purpose(self) -> Description:
        paragraphs = self._tp.fnap(_CORRESPONDENCE_DESCRIPTION)
        paragraphs += insertion_position_description(self.section_info.name,
                                                     self._contents_is_inserted_before_case_contents)

        return Description(self._tp.text(_SINGLE_LINE_DESCRIPTION),
                           paragraphs)

    @property
    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            TestCasePhaseCrossReference(self.name.plain)
        ]


def insertion_position_description(phase: SectionName,
                                   contents_is_inserted_before_case_contents: bool) -> List[ParagraphItem]:
    return normalize_and_parse(_INSERTION_DESCRIPTION_PARAGRAPHS.format(
        insertion_position=_INSERTION_POSITIONS[contents_is_inserted_before_case_contents],
        phase=phase,
    ))


_SINGLE_LINE_DESCRIPTION = 'Common contents of the {phase} phase, for all test cases in the suite'

_INSERTION_POSITIONS = {
    False: 'after',
    True: 'before',
}

_CORRESPONDENCE_DESCRIPTION = """\
Corresponds to the {phase:syntax} test case phase.
"""

_INSERTION_DESCRIPTION_PARAGRAPHS = """\
The section contents is included {insertion_position} the contents
of the {phase} phase of each test case.
"""

_CONTENTS_DESCRIPTION = """\
Identical to contents of the {phase:syntax} test case phase.
"""
