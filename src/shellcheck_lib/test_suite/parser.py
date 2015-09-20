from shellcheck_lib.document import parse
from shellcheck_lib.general import line_source
from shellcheck_lib.test_suite import test_suite_doc
from shellcheck_lib.test_suite.instruction_set.sections.suites import SuitesSectionParser
from shellcheck_lib.test_suite.instruction_set.sections.cases import CasesSectionParser

SECTION_NAME__SUITS = 'suites'
SECTION_NAME__CASES = 'cases'

PARSER_CONFIGURATION = parse.SectionsConfiguration(
    None,
    (parse.SectionConfiguration(SECTION_NAME__SUITS, SuitesSectionParser()),
     parse.SectionConfiguration(SECTION_NAME__CASES, CasesSectionParser()),
     )
)


class Parser:
    def __init__(self):
        self.__plain_file_parser = parse.new_parser_for(PARSER_CONFIGURATION)

    def apply(self,
              plain_test_case: line_source.LineSource) -> test_suite_doc.TestSuite:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_suite_doc.TestSuite(
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__CASES),
        )


PARSER = Parser()
