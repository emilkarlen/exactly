from typing import Dict

from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_suite import section_names_plain

CONFIGURATION = SectionName(section_names_plain.SECTION_NAME__CONF)
CASES = SectionName(section_names_plain.SECTION_NAME__CASES)
SUITES = SectionName(section_names_plain.SECTION_NAME__SUITS)

ALL = (
    CONFIGURATION,
    CASES,
    SUITES,
)


def suite_section_name_dictionary() -> Dict[str, SectionName]:
    phase_names = {}
    for section in ALL:
        phase_names[suite_section_name_dict_key_for(section.plain)] = section
    return phase_names


def suite_section_name_dict_key_for(section_name: str) -> str:
    return section_name.replace('-', '_')
