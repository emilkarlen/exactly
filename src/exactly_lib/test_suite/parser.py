from exactly_lib.help_texts.test_suite.section_names import SECTION_NAME__CONF, SECTION_NAME__SUITS, \
    SECTION_NAME__CASES, \
    DEFAULT_SECTION_NAME
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_suite import test_suite_doc
from exactly_lib.test_suite.instruction_set.sections import cases
from exactly_lib.test_suite.instruction_set.sections import suites
from exactly_lib.test_suite.instruction_set.sections.configuration import instruction_set

PARSER_CONFIGURATION = document_parser.SectionsConfiguration(
    (
        document_parser.SectionConfiguration(SECTION_NAME__CONF,
                                             instruction_set.new_parser()),
        document_parser.SectionConfiguration(SECTION_NAME__SUITS, suites.new_parser()),
        document_parser.SectionConfiguration(SECTION_NAME__CASES, cases.new_parser()),
    ),
    default_section_name=DEFAULT_SECTION_NAME
)


class Parser:
    def __init__(self):
        self.__plain_file_parser = document_parser.new_parser_for(PARSER_CONFIGURATION)

    def apply(self,
              plain_test_case: ParseSource) -> test_suite_doc.TestSuiteDocument:
        document = self.__plain_file_parser.parse(plain_test_case)
        return test_suite_doc.TestSuiteDocument(
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__CONF),
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__CASES),
        )
