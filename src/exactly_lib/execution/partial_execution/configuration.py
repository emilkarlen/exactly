from typing import Optional

from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure


class ConfPhaseValues(tuple):
    """Values resolved from the conf phase"""
    def __new__(cls,
                act_phase_handling: ActPhaseHandling,
                hds: HomeDirectoryStructure,
                timeout_in_seconds: Optional[int] = None):
        """
        :param timeout_in_seconds: None if no timeout
        """
        return tuple.__new__(cls, (act_phase_handling,
                                   hds,
                                   timeout_in_seconds,
                                   ))

    @property
    def act_phase_handling(self) -> ActPhaseHandling:
        return self[0]

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self[1]

    @property
    def timeout_in_seconds(self) -> Optional[int]:
        return self[2]


class TestCase(tuple):
    def __new__(cls,
                setup_phase: SectionContents,
                act_phase: SectionContents,
                before_assert_phase: SectionContents,
                assert_phase: SectionContents,
                cleanup_phase: SectionContents):
        return tuple.__new__(cls, (setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def setup_phase(self) -> SectionContents:
        return self[0]

    @property
    def act_phase(self) -> SectionContents:
        return self[1]

    @property
    def before_assert_phase(self) -> SectionContents:
        return self[2]

    @property
    def assert_phase(self) -> SectionContents:
        return self[3]

    @property
    def cleanup_phase(self) -> SectionContents:
        return self[4]
