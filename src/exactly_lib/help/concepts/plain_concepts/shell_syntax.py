from exactly_lib.cli.cli_environment.program_modes.test_suite.command_line_options import OPTION_FOR_REPORTER
from exactly_lib.common.help.see_also import see_also_url
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.concepts.names_and_cross_references import SHELL_SYNTAX_CONCEPT_INFO
from exactly_lib.help.suite_reporters import names_and_cross_references as reporters
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description


class _ShellSyntaxConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(SHELL_SYNTAX_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        tp = TextParser({
            'reporter_option': formatting.cli_option(OPTION_FOR_REPORTER),
            'default_reporter': formatting.entity(reporters.DEFAULT_REPORTER.singular_name),
        })
        return from_simple_description(
            Description(self.single_line_description(),
                        tp.fnap(_DESCRIPTION_REST)))

    def see_also_items(self) -> list:
        return [
            see_also_url('Python shell syntax',
                         'https://docs.python.org/3/library/shlex.html#parsing-rules')
        ]


SHELL_SYNTAX_CONCEPT = _ShellSyntaxConcept()

_DESCRIPTION_REST = """\
Quoting according to the "shlex" module of the Python language.


The syntax resembles that of the Unix shell.


The "shlex" module is used in POSIX mode.
"""
