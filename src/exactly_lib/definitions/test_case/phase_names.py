from typing import Dict

from exactly_lib.definitions.formatting import SectionName
from exactly_lib.test_case import phase_identifier

CONFIGURATION = SectionName(phase_identifier.CONFIGURATION.identifier)
SETUP = SectionName(phase_identifier.SETUP.section_name)
ACT = SectionName(phase_identifier.ACT.section_name)
BEFORE_ASSERT = SectionName(phase_identifier.BEFORE_ASSERT.section_name)
ASSERT = SectionName(phase_identifier.ASSERT.section_name)
CLEANUP = SectionName(phase_identifier.CLEANUP.section_name)

ALL = (
    CONFIGURATION,
    SETUP,
    ACT,
    BEFORE_ASSERT,
    ASSERT,
    CLEANUP,
)


def _phase_name_dictionary() -> Dict[str, SectionName]:
    phase_names = {}
    for phase in ALL:
        phase_names[phase_name_dict_key_for(phase.plain)] = phase
    return phase_names


def phase_name_dict_key_for(phase_name: str) -> str:
    return phase_name.replace('-', '_')


PHASE_NAME_DICTIONARY = _phase_name_dictionary()
