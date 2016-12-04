from exactly_lib.cli.cli_environment.program_modes.test_case.command_line_options import OPTION_FOR_PREPROCESSOR
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, Name
from exactly_lib.help.suite_reporters.names_and_cross_references import ALL_SUITE_REPORTERS__CROSS_REFS
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.structure.structures import text


class _SuiteReporterConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('reporter', 'reporters'))

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'preprocessor_option': formatting.cli_option(OPTION_FOR_PREPROCESSOR),
        })
        return from_simple_description(
            Description(text(_SINGLE_LINE_DESCRIPTION),
                        tp.fnap(_DESCRIPTION_REST)))

    def see_also(self) -> list:
        return ALL_SUITE_REPORTERS__CROSS_REFS


SUITE_REPORTER_CONCEPT = _SuiteReporterConcept()

_SINGLE_LINE_DESCRIPTION = """\
Reports the outcome of a test suite via stdout, stderr and exit code."""

_DESCRIPTION_REST = """\
TODO
"""
