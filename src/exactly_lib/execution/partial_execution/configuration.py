from exactly_lib.section_document.model import SectionContents
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.util.name_and_value import NameAndValue


class ConfPhaseValues(tuple):
    """Values resolved from the conf phase"""

    def __new__(cls,
                actor: NameAndValue[Actor],
                hds: HomeDs,
                ):
        return tuple.__new__(cls, (actor, hds,))

    @property
    def actor(self) -> NameAndValue[Actor]:
        return self[0]

    @property
    def hds(self) -> HomeDs:
        return self[1]


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
