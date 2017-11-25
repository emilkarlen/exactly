from exactly_lib.help_texts.formatting import SectionName
from exactly_lib.help_texts.test_suite import section_names

CONFIGURATION_SECTION_NAME = SectionName(section_names.SECTION_NAME__CONF)
CASES_SECTION_NAME = SectionName(section_names.SECTION_NAME__CASES)
SUITES_SECTION_NAME = SectionName(section_names.SECTION_NAME__SUITS)

ALL = (
    CONFIGURATION_SECTION_NAME,
    CASES_SECTION_NAME,
    SUITES_SECTION_NAME,
)


def suite_section_name_dictionary() -> dict:
    phase_names = {}
    for section in ALL:
        phase_names[suite_section_name_dict_key_for(section.plain)] = section
    return phase_names


def suite_section_name_dict_key_for(section_name: str) -> str:
    return section_name.replace('-', '_')
