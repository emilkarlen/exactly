import pathlib

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.test_suite import suite_hierarchy_reading
from exactly_lib.test_suite.instruction_set.test_suite_definition import TestSuiteDefinition


def resolve_handling_setup_from_suite(default_handling_setup: TestCaseHandlingSetup,
                                      test_suite_definition: TestSuiteDefinition,
                                      suite_to_read_config_from: pathlib.Path) -> TestCaseHandlingSetup:
    if not suite_to_read_config_from:
        return default_handling_setup

    suite_reader = suite_hierarchy_reading.Reader(
        suite_hierarchy_reading.Environment(
            test_suite_definition.configuration_section_parser,
            default_handling_setup.preprocessor,
            default_handling_setup.act_phase_setup)
    )
    test_suite = suite_reader.apply(suite_to_read_config_from)
    return test_suite.test_case_handling_setup
