import unittest

from exactly_lib import program_info
from exactly_lib.cli.cli_environment.command_line_options import SUITE_COMMAND
from exactly_lib.help.utils.render import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.command_line_syntax.elements import argument3 as arg
from exactly_lib.util.command_line_syntax.render import command_line3 as render
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
#from exactly_lib_test.util.textformat.test_resources import structure as struct_check


class CliSyntaxRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return render.ProgramDocumentationRenderer(environment).apply(_COMMAND_LINE, _ARGUMENT_DESCRIPTIONS)


_ACTOR = render.DescribedArgument(arg.Option(long_name='actor',
                                             argument='EXECUTABLE'),
                                  [docs.para('actor description')])

_ARGUMENT_DESCRIPTIONS = [
    _ACTOR,
]

_COMMAND_LINE = arg.CommandLine(program_info.PROGRAM_NAME,
                                [arg.Single(arg.Multiplicity.MANDATORY,
                                            arg.Constant(SUITE_COMMAND)),
                                 arg.Single(arg.Multiplicity.OPTIONAL,
                                            _ACTOR.argument),
                                 arg.Single(arg.Multiplicity.MANDATORY,
                                            arg.Named('FILE')),
                                 ])

#class Test(unittest.TestCase):
#    def test(self):
#        sc = CliSyntaxRenderer().apply(RenderingEnvironment(None))
#        struct_check.is_section_contents.apply(self, sc)
#        print(str(type(doc)))
