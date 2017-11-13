from exactly_lib.common.help.see_also import SeeAlsoUrlInfo
from exactly_lib.help.entities.suite_reporters.contents_structure import SuiteReporterDocumentation
from exactly_lib.help_texts.entity.suite_reporters import JUNIT_REPORTER
from exactly_lib.test_suite.reporters import junit
from exactly_lib.util.textformat.textformat_parser import TextParser


class JunitSuiteReporterDocumentation(SuiteReporterDocumentation):
    def __init__(self):
        super().__init__(JUNIT_REPORTER)
        format_map = {
            'EXIT_CODE': str(junit.UNCONDITIONAL_EXIT_CODE),
            'test_suite_element': junit.TEST_SUITE_ELEMENT_NAME,
            'test_suites_element': junit.TEST_SUITES_ELEMENT_NAME,
            'url': JUNIT_XML_SYNTAX_SEE_ALSO_URL_INFO.url,
        }
        self._parser = TextParser(format_map)

    def syntax_of_output(self) -> list:
        return self._parser.fnap(_SYNTAX_OF_OUTPUT)

    def exit_code_description(self) -> list:
        return self._parser.fnap(_EXIT_CODE_DESCRIPTION)

    def _see_also_targets__specific(self) -> list:
        return [JUNIT_XML_SYNTAX_SEE_ALSO_URL_INFO]


JUNIT_XML_SYNTAX_SEE_ALSO_URL_INFO = SeeAlsoUrlInfo('Windy Road JUnit XSD',
                                                    'https://github.com/windyroad/JUnit-Schema/')

_SYNTAX_OF_OUTPUT = """\
{url}

as of 2016-11-14.


A suite with sub suites is reported as a '{test_suites_element}' element.


A suite without sub suites is reported as a '{test_suite_element}' element.
"""

_EXIT_CODE_DESCRIPTION = """\
Unconditionally {EXIT_CODE}.
"""
