from exactly_lib.definitions.test_case import phase_names_plain

SECTION_NAME__CONF = 'conf'
SECTION_NAME__SUITS = 'suites'
SECTION_NAME__CASES = 'cases'

SECTION_NAME__CASE_SETUP = phase_names_plain.SETUP_PHASE_NAME
SECTION_NAME__CASE_ACT = phase_names_plain.ACT_PHASE_NAME
SECTION_NAME__CASE_BEFORE_ASSERT = phase_names_plain.BEFORE_ASSERT_PHASE_NAME
SECTION_NAME__CASE_ASSERT = phase_names_plain.ASSERT_PHASE_NAME
SECTION_NAME__CASE_CLEANUP = phase_names_plain.CLEANUP_PHASE_NAME

ALL_SUITE_SPECIFIC_SECTION_NAMES = (SECTION_NAME__CONF,
                                    SECTION_NAME__SUITS,
                                    SECTION_NAME__CASES)

DEFAULT_SECTION_NAME = SECTION_NAME__CASES

SECTION_CONCEPT_NAME = 'section'
