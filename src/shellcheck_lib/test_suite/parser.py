from shellcheck_lib.document import parse
from shellcheck_lib.test_suite import test_suite_doc
from shellcheck_lib.test_suite.instruction_set.sections import anonymous
from shellcheck_lib.test_suite.instruction_set.sections import cases
from shellcheck_lib.test_suite.instruction_set.sections import suites
from shellcheck_lib.util import line_source

SECTION_NAME__CONF = 'conf'
SECTION_NAME__SUITS = 'suites'
SECTION_NAME__CASES = 'cases'

ALL_SECTION_NAMES = (SECTION_NAME__CONF,
                     SECTION_NAME__SUITS,
                     SECTION_NAME__CASES)

PARSER_CONFIGURATION = parse.SectionsConfiguration(
    (
        parse.SectionConfiguration(SECTION_NAME__CONF, anonymous.new_parser()),
        parse.SectionConfiguration(SECTION_NAME__SUITS, suites.new_parser()),
        parse.SectionConfiguration(SECTION_NAME__CASES, cases.new_parser()),
    ),
    default_section_name=SECTION_NAME__CONF
)


class Parser:
    def __init__(self):
        self.__plain_file_parser = parse.new_parser_for(PARSER_CONFIGURATION)

    def apply(self,
              plain_test_case: line_source.LineSource) -> test_suite_doc.TestSuiteDocument:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_suite_doc.TestSuiteDocument(
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__CONF),
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__CASES),
        )


PARSER = Parser()
