from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import formatting
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_suite import section_names
from exactly_lib.definitions.test_suite import section_names_plain
from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp
from exactly_lib.util.textformat.constructor import sections, paragraphs
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

CASES_AND_SUB_SUITES_HEADER = 'Test cases and sub suites'

COMMON_CASE_CONTENTS_HEADER = 'Common test case contents'

COMMON_CASE_CONTENTS_AND_CONFIG_HEADER = 'Common test case contents and configuration'

ADDITIONAL_TEST_CASE_CONFIG_HEADER = 'Additional test case configuration'

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def root(header: str, suite_help: TestSuiteHelp) -> SectionHierarchyGenerator:
    return _HierarchyGenerator(suite_help).generator(header)


class _HierarchyGenerator:
    def __init__(self, suite_help: TestSuiteHelp):
        self._suite_help = suite_help
        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'conf_section': section_names.CONFIGURATION,
            'conf_phase': phase_names.CONFIGURATION,
        })

    def generator(self, header: str) -> SectionHierarchyGenerator:
        return h.hierarchy(
            header,
            paragraphs.constant(self._tp.fnap(_PRELUDE)),
            [
                h.child('cases-and-sub-suites',
                        self._cases_and_sub_suites(CASES_AND_SUB_SUITES_HEADER)
                        ),
                h.child('common-test-case-contents',
                        self._common_tc_contents(COMMON_CASE_CONTENTS_HEADER)
                        ),
                h.child('additional-test-case-conf',
                        h.leaf(
                            ADDITIONAL_TEST_CASE_CONFIG_HEADER,
                            sections.constant_contents(
                                docs.section_contents(self._tp.fnap(_ADDITIONAL_TEST_CASE_CONFIG))
                            ))
                        ),
            ])

    def _cases_and_sub_suites(self, header: str) -> SectionHierarchyGenerator:
        return h.leaf(
            header,
            sections.constant_contents(
                docs.section_contents(self._cases_and_sub_suites_paragraphs())
            )
        )

    def _common_tc_contents(self, header: str) -> SectionHierarchyGenerator:
        return h.leaf(
            header,
            sections.constant_contents(
                docs.section_contents(self._common_tc_contents_paragraphs())
            ))

    def _cases_and_sub_suites_paragraphs(self) -> List[ParagraphItem]:
        ret_val = self._tp.fnap(_CASES_AND_SUB_SUITES)
        ret_val.append(sections_short_list(self._suite_help.test_cases_and_sub_suites_sections,
                                           default_section_name=section_names_plain.DEFAULT_SECTION_NAME,
                                           section_concept_name='section'))
        return ret_val

    def _common_tc_contents_paragraphs(self) -> List[ParagraphItem]:
        ret_val = self._tp.fnap(_COMMON_TC_CONTENTS)
        ret_val.append(sections_short_list(self._suite_help.test_case_phase_sections,
                                           default_section_name=section_names_plain.DEFAULT_SECTION_NAME,
                                           section_concept_name='section'))
        return ret_val


_PRELUDE = """\
A suite is made up of "sections".


Some sections correspond to test case "phases".


All sections are optional.
"""

_CASES_AND_SUB_SUITES = """\
A test suite contains test cases and sub suites.


These are specified in sections:
"""

_COMMON_TC_CONTENTS = """\
A test suite has a section corresponding to every test case phase.


These sections specify test case contents that is common to all cases in the suite.

The contents is included in every test case in the suite.


Note that the contents is only included in test cases listed directly in the suite -
not in sub suites.

The reason for this is that it should be easy to run a test case standalone, and {program_name}
has no functionality for looking up the ultimate root suite
that a test case belongs to.


Sections:
"""

_ADDITIONAL_TEST_CASE_CONFIG = """\
The {conf_section} section has additional configuration possibilities,
compared to those of the {conf_phase} test case phase.
"""
