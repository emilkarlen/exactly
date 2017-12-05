import pathlib

from exactly_lib.help_texts.test_suite.section_names import SECTION_NAME__CONF, SECTION_NAME__SUITS, \
    SECTION_NAME__CASES, \
    DEFAULT_SECTION_NAME
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.exceptions import FileSourceError
from exactly_lib.section_document.model import ElementType
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.utils import new_for_file
from exactly_lib.test_suite import test_suite_doc
from exactly_lib.test_suite.instruction_set import parse
from exactly_lib.test_suite.instruction_set.sections import cases
from exactly_lib.test_suite.instruction_set.sections import suites
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionEnvironment


def read_suite_document(suite_file_path: pathlib.Path,
                        configuration_section_parser: document_parser.SectionElementParser
                        ) -> test_suite_doc.TestSuiteDocument:
    """
    :raises parse.SuiteSyntaxError: The suite file has syntax errors
    """
    source = new_for_file(suite_file_path)
    try:
        return _Parser(configuration_section_parser).apply(source)
    except FileSourceError as ex:
        raise parse.SuiteSyntaxError(suite_file_path,
                                     ex.source_error.line,
                                     ex.source_error.message,
                                     maybe_section_name=ex.maybe_section_name)


def resolve_test_case_handling_setup(
        test_suite: test_suite_doc.TestSuiteDocument,
        default_handling_setup: TestCaseHandlingSetup) -> TestCaseHandlingSetup:
    instruction_environment = ConfigurationSectionEnvironment(default_handling_setup.preprocessor,
                                                              default_handling_setup.act_phase_setup)
    for section_element in test_suite.configuration_section.elements:
        if section_element.element_type is ElementType.INSTRUCTION:
            section_element.instruction_info.instruction.execute(instruction_environment)
    return TestCaseHandlingSetup(instruction_environment.act_phase_setup,
                                 instruction_environment.preprocessor)


class _Parser:
    def __init__(self, configuration_section_parser: document_parser.SectionElementParser):
        parser_configuration = document_parser.SectionsConfiguration(
            (
                document_parser.SectionConfiguration(SECTION_NAME__CONF,
                                                     configuration_section_parser),
                document_parser.SectionConfiguration(SECTION_NAME__SUITS, suites.new_parser()),
                document_parser.SectionConfiguration(SECTION_NAME__CASES, cases.new_parser()),
            ),
            default_section_name=DEFAULT_SECTION_NAME
        )
        self.__plain_file_parser = document_parser.new_parser_for(parser_configuration)

    def apply(self,
              plain_test_case: ParseSource) -> test_suite_doc.TestSuiteDocument:
        document = self.__plain_file_parser.parse(plain_test_case)
        return test_suite_doc.TestSuiteDocument(
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__CONF),
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__CASES),
        )
