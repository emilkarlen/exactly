from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.test_case import phase_identifier
from exactly_lib_test.help.test_resources import section_documentation

TEST_CASE_HELP_WITH_PRODUCTION_PHASES = TestCaseHelp([
    section_documentation(phase_identifier.CONFIGURATION.identifier, []),
    section_documentation(phase_identifier.SETUP.identifier, []),
    section_documentation(phase_identifier.ACT.identifier, []),
    section_documentation(phase_identifier.BEFORE_ASSERT.identifier, []),
    section_documentation(phase_identifier.ASSERT.identifier, []),
    section_documentation(phase_identifier.CLEANUP.identifier, []),
])
