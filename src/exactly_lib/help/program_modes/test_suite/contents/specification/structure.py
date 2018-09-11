from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import formatting
from exactly_lib.definitions.test_suite import section_names
from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.util.textformat.construction.section_contents_constructor import constant_section_contents
from exactly_lib.util.textformat.construction.section_hierarchy import hierarchy
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import Node
from exactly_lib.util.textformat.construction.section_hierarchy.structures import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def hierarchy_generator(header: str, suite_help: TestSuiteHelp) -> SectionHierarchyGenerator:
    return _HierarchyGenerator(suite_help).generator(header)


class _HierarchyGenerator:
    def __init__(self, suite_help: TestSuiteHelp):
        self._suite_help = suite_help
        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
        })

    def generator(self, header: str) -> SectionHierarchyGenerator:
        return hierarchy.parent(
            header,
            self._tp.fnap(_PRELUDE),
            [
                Node('cases-and-sub-suites',
                     self._cases_and_sub_suites('Test cases and sub suites')
                     ),
                Node('common-test-case-contents',
                     self._common_tc_contents('Common test case contents')
                     ),
            ])

    def _cases_and_sub_suites(self, header: str) -> SectionHierarchyGenerator:
        return hierarchy.leaf(
            header,
            constant_section_contents(
                docs.section_contents(self._cases_and_sub_suites_paragraphs())
            )
        )

    def _common_tc_contents(self, header: str) -> SectionHierarchyGenerator:
        return hierarchy.leaf(
            header,
            constant_section_contents(
                docs.section_contents(self._common_tc_contents_paragraphs())
            ))

    def _cases_and_sub_suites_paragraphs(self) -> List[ParagraphItem]:
        ret_val = self._tp.fnap(_CASES_AND_SUB_SUITES)
        ret_val.append(sections_short_list(self._suite_help.test_cases_and_sub_suites_sections,
                                           default_section_name=section_names.DEFAULT_SECTION_NAME,
                                           section_concept_name='section'))
        return ret_val

    def _common_tc_contents_paragraphs(self) -> List[ParagraphItem]:
        ret_val = self._tp.fnap(_COMMON_TC_CONTENTS)
        ret_val.append(sections_short_list(self._suite_help.test_case_phase_sections,
                                           default_section_name=section_names.DEFAULT_SECTION_NAME,
                                           section_concept_name='section'))
        return ret_val


_PRELUDE = """\
A suite is a sequence of "sections".


Some sections correspond to test case "phases".
"""

_CASES_AND_SUB_SUITES = """\
A test suite is made up of test cases and sub suites.


These are specified in sections:
"""

_COMMON_TC_CONTENTS = """\
A test suite has a section corresponding to every test case phase.


These sections specify test case contents that is common to all cases in the suite.

The contents is included in every test case in the suite.


Note that the contents is only included in test cases listed directly in the suite -
not in sub suites!

The reason for this is that it should be easy to run a test case standalone, and {program_name}
has no functionality for looking up the ultimate root suite
that a test case belongs to.


Sections:
"""
