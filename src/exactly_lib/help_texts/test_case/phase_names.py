from exactly_lib.help_texts.formatting import SectionName
from exactly_lib.test_case import phase_identifier

CONFIGURATION_PHASE_NAME = SectionName(phase_identifier.CONFIGURATION.identifier)
SETUP_PHASE_NAME = SectionName(phase_identifier.SETUP.section_name)
ACT_PHASE_NAME = SectionName(phase_identifier.ACT.section_name)
BEFORE_ASSERT_PHASE_NAME = SectionName(phase_identifier.BEFORE_ASSERT.section_name)
ASSERT_PHASE_NAME = SectionName(phase_identifier.ASSERT.section_name)
CLEANUP_PHASE_NAME = SectionName(phase_identifier.CLEANUP.section_name)

ALL = (
    CONFIGURATION_PHASE_NAME,
    SETUP_PHASE_NAME,
    ACT_PHASE_NAME,
    BEFORE_ASSERT_PHASE_NAME,
    ASSERT_PHASE_NAME,
    CLEANUP_PHASE_NAME,
)


def _phase_name_dictionary() -> dict:
    phase_names = {}
    for phase in ALL:
        phase_names[phase_name_dict_key_for(phase.plain)] = phase
    return phase_names


def phase_name_dict_key_for(phase_name: str) -> str:
    return phase_name.replace('-', '_')


PHASE_NAME_DICTIONARY = _phase_name_dictionary()
