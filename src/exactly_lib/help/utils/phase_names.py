from exactly_lib.execution import phases
from exactly_lib.help.utils.formatting import SectionName

CONFIGURATION_PHASE_NAME = SectionName(phases.ANONYMOUS.identifier)
SETUP_PHASE_NAME = SectionName(phases.SETUP.section_name)
ACT_PHASE_NAME = SectionName(phases.ACT.section_name)
BEFORE_ASSERT_PHASE_NAME = SectionName(phases.BEFORE_ASSERT.section_name)
ASSERT_PHASE_NAME = SectionName(phases.ASSERT.section_name)
CLEANUP_PHASE_NAME = SectionName(phases.CLEANUP.section_name)

ALL = (
    CONFIGURATION_PHASE_NAME,
    SETUP_PHASE_NAME,
    ACT_PHASE_NAME,
    BEFORE_ASSERT_PHASE_NAME,
    ASSERT_PHASE_NAME,
    CLEANUP_PHASE_NAME,
)


def phase_name_dictionary() -> dict:
    phase_names = {}
    for phase in ALL:
        phase_names[phase.plain.replace('-', '_')] = phase
    return phase_names
