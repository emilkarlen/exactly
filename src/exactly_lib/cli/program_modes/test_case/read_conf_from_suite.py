import pathlib

from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import document_parser
from exactly_lib.test_suite import suite_file_reading


def resolve_handling_setup_from_suite(default_handling_setup: TestCaseHandlingSetup,
                                      configuration_section_parser: document_parser.SectionElementParser,
                                      suite_to_read_config_from: pathlib.Path) -> TestCaseHandlingSetup:
    if not suite_to_read_config_from:
        return default_handling_setup

    suite_document = suite_file_reading.read_suite_document(suite_to_read_config_from,
                                                            configuration_section_parser)
    return suite_file_reading.resolve_test_case_handling_setup(suite_document,
                                                               default_handling_setup)
