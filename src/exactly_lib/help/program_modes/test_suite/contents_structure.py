from typing import List, Iterable

from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation


class TestSuiteHelp(tuple):
    def __new__(cls,
                test_suite_section_helps: Iterable[SectionDocumentation]):
        return tuple.__new__(cls, (list(test_suite_section_helps),))

    @property
    def section_helps(self) -> List[SectionDocumentation]:
        return self[0]
