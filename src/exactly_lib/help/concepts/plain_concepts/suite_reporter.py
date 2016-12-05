from exactly_lib.cli.cli_environment.program_modes.test_suite.command_line_options import OPTION_FOR_REPORTER
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, Name
from exactly_lib.help.suite_reporters import names_and_cross_references as reporters
from exactly_lib.help.suite_reporters.names_and_cross_references import all_suite_reporters_cross_refs
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure.structures import text


class _SuiteReporterConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('reporter', 'reporters'))

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'reporter_option': formatting.cli_option(OPTION_FOR_REPORTER),
            'default_reporter': formatting.entity(reporters.DEFAULT_REPORTER.singular_name),
        })
        return from_simple_description(
            Description(text(_SINGLE_LINE_DESCRIPTION),
                        tp.fnap(_DESCRIPTION_REST)))

    def see_also(self) -> list:
        return all_suite_reporters_cross_refs()


SUITE_REPORTER_CONCEPT = _SuiteReporterConcept()

_SINGLE_LINE_DESCRIPTION = """\
Reports the outcome of a test suite via stdout, stderr and exit code.
"""

_DESCRIPTION_REST = """\
The reporter is specified via the command line using the {reporter_option} option.


Default reporter: {default_reporter}.
"""
