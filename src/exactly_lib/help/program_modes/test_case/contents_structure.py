from typing import Dict, Sequence

from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation


class TestCaseHelp(tuple):
    def __new__(cls,
                phase_helps: Sequence[SectionDocumentation]):
        return tuple.__new__(cls, (list(phase_helps),))

    @property
    def phase_helps_in_order_of_execution(self) -> Sequence[SectionDocumentation]:
        return self[0]

    @property
    def phase_name_2_phase_help(self) -> Dict[str, SectionDocumentation]:
        return {
            ph_help.name.plain: ph_help
            for ph_help in self.phase_helps_in_order_of_execution
        }
