from exactly_lib.common.instruction_documentation import InstructionDocumentation
from exactly_lib.help.utils.formatting import InstructionName
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.render.cli_program_syntax import CommandLineSyntaxRenderer


class InstructionDocumentationWithTextParserBase(InstructionDocumentation):
    """
    A `InstructionDocumentation` with convenient access to a `TextParser`.

    The format_map of the `TextParser` always contains a key
    "instruction_name" which is the name of the instruction as a `InstructionName` object
    (which gives access to some formatting using the ":fmt" syntax).
    """

    def __init__(self,
                 instruction_name: str,
                 format_map: dict):
        super().__init__(instruction_name)
        fm = {'instruction_name': InstructionName(instruction_name)}
        fm.update(format_map)
        self._parser = TextParser(fm)

    def _format(self, s: str, extra: dict = None) -> str:
        return self._parser.format(s, extra)

    def _text(self, s: str, extra: dict = None) -> str:
        return self._parser.text(s, extra)

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


class InstructionDocumentationWithCommandLineRenderingBase(InstructionDocumentationWithTextParserBase):
    def __init__(self,
                 instruction_name: str,
                 format_map: dict):
        super().__init__(instruction_name, format_map)

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        cl = argument.CommandLine(argument_usages)
        return self._cl_syntax(cl)

    def _cl_syntax(self, command_line: argument.CommandLine) -> str:
        cl_renderer = CommandLineSyntaxRenderer()
        return cl_renderer.as_str(command_line)
