from typing import List, Iterable

from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation


class TestSuiteHelp(tuple):
    def __new__(cls,
                test_cases_and_sub_suites_sections: Iterable[SectionDocumentation],
                test_case_phase_sections: Iterable[SectionDocumentation]):
        cs_list = list(test_cases_and_sub_suites_sections)
        p_list = list(test_case_phase_sections)
        return tuple.__new__(cls, (cs_list + p_list,
                                   cs_list,
                                   p_list))

    @property
    def section_helps(self) -> List[SectionDocumentation]:
        return self[0]

    @property
    def test_cases_and_sub_suites_sections(self) -> List[SectionDocumentation]:
        return self[1]

    @property
    def test_case_phase_sections(self) -> List[SectionDocumentation]:
        return self[2]
