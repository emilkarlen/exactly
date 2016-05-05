from exactly_lib import program_info
from exactly_lib.cli.cli_environment.command_line_options import SUITE_COMMAND
from exactly_lib.help.concepts.plain_concepts import actor
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.description import DescriptionWithSubSections
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.render import cli_program_syntax as render
from exactly_lib.util.textformat.structure import structures as docs


class SuiteCliSyntaxDocumentation(render.CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)
        self.parser = TextParser({
            'interpreter_actor': formatting.term(actor.INTERPRETER_ACTOR_TERM),
            'TEST_SUITE_FILE': _FILE_ARGUMENT.name,
        })

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(docs.text('Runs a test suite.'),
                                          docs.SectionContents(self.parser.fnap(_DESCRIPTION),
                                                               []))

    def synopsises(self) -> list:
        return [
            render.Synopsis(
                arg.CommandLine([arg.Single(arg.Multiplicity.MANDATORY,
                                            arg.Constant(SUITE_COMMAND)),
                                 arg.Single(arg.Multiplicity.OPTIONAL,
                                            _ACTOR_OPTION),
                                 arg.Single(arg.Multiplicity.MANDATORY,
                                            _FILE_ARGUMENT),
                                 ],
                                prefix=self.program_name)
            )]

    def argument_descriptions(self) -> list:
        return [
            self._actor_argument(),
        ]

    def _actor_argument(self) -> render.DescribedArgument:
        extra_format_map = {
            'interpreter_program': _ACTOR_OPTION.argument,
        }
        return render.DescribedArgument(_ACTOR_OPTION,
                                        self.parser.fnap(_ACTOR_OPTION_DESCRIPTION, extra_format_map),
                                        see_also=[
                                            actor.ACTOR_CONCEPT.cross_reference_target(),
                                        ])


_DESCRIPTION = """\
Runs the test suite in file {TEST_SUITE_FILE}.
"""

_ACTOR_OPTION_DESCRIPTION = """\
Specifies an {interpreter_actor}, by giving the executable program that serves as the interpreter.


{interpreter_program} is an absolute path followed by optional arguments
(using shell syntax).
"""

_ACTOR_OPTION = arg.Option(long_name='actor',
                           argument='PROGRAM')

_FILE_ARGUMENT = arg.Named('FILE')
