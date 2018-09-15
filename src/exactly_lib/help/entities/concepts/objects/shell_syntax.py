from typing import List

from exactly_lib.cli.definitions.program_modes.test_suite.command_line_options import OPTION_FOR_REPORTER
from exactly_lib.common.help.see_also import SeeAlsoUrlInfo
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import suite_reporters as reporters
from exactly_lib.definitions.entity.concepts import SHELL_SYNTAX_CONCEPT_INFO
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.textformat_parser import TextParser

PYTHON_SHELL_SYNTAX_SEE_ALSO_URL_INFO = SeeAlsoUrlInfo('Python shell syntax',
                                                       'https://docs.python.org/3/library/shlex.html#parsing-rules')


class _ShellSyntaxConcept(ConceptDocumentation):
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

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            PYTHON_SHELL_SYNTAX_SEE_ALSO_URL_INFO
        ]


SHELL_SYNTAX_CONCEPT = _ShellSyntaxConcept()

_DESCRIPTION_REST = """\
Quoting according to the "shlex" module of the Python language.


The syntax resembles that of the Unix shell.


The "shlex" module is used in POSIX mode.
"""
