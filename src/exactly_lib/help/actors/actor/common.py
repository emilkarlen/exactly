from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax


class ActPhaseDocumentationSyntaxBase:
    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()

    def __init__(self, text_parser: TextParser):
        self._parser = text_parser

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        cl = a.CommandLine(argument_usages)
        return self._cl_syntax(cl)

    def _cl_syntax(self, command_line: a.CommandLine) -> str:
        return self.CL_SYNTAX_RENDERER.as_str(command_line)

    def _arg_syntax(self, arg: a.Argument) -> str:
        return self.ARG_SYNTAX_RENDERER.visit(arg)

    def _cli_argument_syntax_element_description(self,
                                                 argument: a.Argument,
                                                 description_rest: list) -> SyntaxElementDescription:
        return SyntaxElementDescription(self._arg_syntax(argument),
                                        description_rest)

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
