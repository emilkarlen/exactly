from exactly_lib.help.utils.formatting import SectionName
from exactly_lib.test_suite import parser

CONFIGURATION_SECTION_NAME = SectionName(parser.SECTION_NAME__CONF)
CASES_SECTION_NAME = SectionName(parser.SECTION_NAME__CASES)
SUITES_SECTION_NAME = SectionName(parser.SECTION_NAME__SUITS)

ALL = (
    CONFIGURATION_SECTION_NAME,
    CASES_SECTION_NAME,
    SUITES_SECTION_NAME,
)


def suite_section_name_dictionary() -> dict:
    phase_names = {}
    for phase in ALL:
        phase_names[suite_section_name_dict_key_for(phase.plain)] = phase
    return phase_names


def suite_section_name_dict_key_for(phase_name: str) -> str:
    return phase_name.replace('-', '_')
