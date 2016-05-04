from exactly_lib import program_info
from exactly_lib.cli.cli_environment.command_line_options import SUITE_COMMAND
from exactly_lib.help.utils.render import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.command_line_syntax.elements import argument2 as arg
from exactly_lib.util.command_line_syntax.render.command_line2 import ProgramDocumentationRenderer
from exactly_lib.util.textformat.structure import document as doc


class CliSyntaxRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return ProgramDocumentationRenderer().apply(_COMMAND_LINE)


_COMMAND_LINE = arg.CommandLine(program_info.PROGRAM_NAME,
                                [arg.Single(arg.Multiplicity.MANDATORY,
                                            arg.Constant(SUITE_COMMAND)),
                                 arg.Single(arg.Multiplicity.OPTIONAL,
                                            arg.Option(long_name='actor',
                                                       element=arg.ArgumentValueElement('EXECUTABLE'))),
                                 arg.Single(arg.Multiplicity.MANDATORY,
                                            arg.Named(arg.ArgumentValueElement('FILE'))),
                                 ])
