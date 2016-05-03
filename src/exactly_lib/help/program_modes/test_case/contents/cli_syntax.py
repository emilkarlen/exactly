from exactly_lib import program_info
from exactly_lib.help.utils.render import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.command_line_syntax.elements import argument
from exactly_lib.util.command_line_syntax.elements.cl_syntax import CommandLine
from exactly_lib.util.command_line_syntax.render.command_line import ProgramDocumentationRenderer
from exactly_lib.util.textformat.structure import document as doc


class CliSyntaxRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return ProgramDocumentationRenderer().apply(_COMMAND_LINE)


_COMMAND_LINE = CommandLine(program_info.PROGRAM_NAME,
                            [argument.ArgumentUsage(argument.PositionalArgument('FILE'),
                                                    argument.ArgumentUsageType.MANDATORY)])
