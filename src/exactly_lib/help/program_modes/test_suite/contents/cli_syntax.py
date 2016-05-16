from exactly_lib import program_info
from exactly_lib.cli.cli_environment import common_cli_options as common_opts
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as case_opts
from exactly_lib.cli.cli_environment.program_modes.test_suite import command_line_options as opts
from exactly_lib.help.concepts.plain_concepts import actor
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.render import cli_program_syntax as render
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class SuiteCliSyntaxDocumentation(render.CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)
        self.parser = TextParser({
            'interpreter_actor': formatting.term(case_opts.INTERPRETER_ACTOR_TERM),
            'TEST_SUITE_FILE': _FILE_ARGUMENT.name,
        })
        self.synopsis = synopsis()

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(self.synopsis.maybe_single_line_description,
                                          docs.SectionContents(self.parser.fnap(_DESCRIPTION),
                                                               []))

    def synopsises(self) -> list:
        return [
            render.Synopsis(self.synopsis.command_line)
        ]

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


def synopsis() -> render.Synopsis:
    command_line = arg.CommandLine([
        arg.Single(arg.Multiplicity.MANDATORY,
                   arg.Constant(common_opts.SUITE_COMMAND)),
        arg.Single(arg.Multiplicity.OPTIONAL,
                   _ACTOR_OPTION),
        arg.Single(arg.Multiplicity.MANDATORY,
                   _FILE_ARGUMENT),
    ],
        prefix=program_info.PROGRAM_NAME)
    return render.Synopsis(command_line,
                           docs.text('Runs a test suite.'))


_DESCRIPTION = """\
Runs the test suite in file {TEST_SUITE_FILE}.
"""

_ACTOR_OPTION_DESCRIPTION = """\
Specifies an {interpreter_actor} to use for every test case in the suite.


{interpreter_program} is the absolute path of an executable program,
followed by optional arguments (using shell syntax).
"""

_ACTOR_OPTION = arg.option(long_name=opts.OPTION_FOR_ACTOR__LONG,
                           argument=case_opts.ACTOR_OPTION_ARGUMENT)

_FILE_ARGUMENT = arg.Named(opts.TEST_SUITE_FILE_ARGUMENT)
