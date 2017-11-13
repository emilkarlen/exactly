from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.textformat_parser import TextParser


class ActPhaseDocumentationSyntaxBase:
    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    def __init__(self, text_parser: TextParser):
        self._parser = text_parser

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        cl = a.CommandLine(argument_usages)
        return self.CL_SYNTAX_RENDERER.as_str(cl)

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH = """\
Comment lines are lines beginning with {LINE_COMMENT_MARKER}
(optionally preceded by space).
"""
ARGUMENT_SYNTAX_ELEMENT = """\
A command line argument.


Uses {shell_syntax_concept}.
"""
