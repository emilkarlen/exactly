from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.help.concepts.plain_concepts import actor
from exactly_lib.help.concepts.plain_concepts.preprocessor import PREPROCESSOR_CONCEPT
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.render import cli_program_syntax as render
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class TestCaseCliSyntaxDocumentation(render.CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)
        self.parser = TextParser({
            'interpreter_actor': formatting.term(opt.INTERPRETER_ACTOR_TERM),
            'TEST_CASE_FILE': _FILE_ARGUMENT.name,
            'phase': phase_name_dictionary(),
        })

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(docs.text('Runs a test case.'),
                                          docs.SectionContents(self.parser.fnap(_DESCRIPTION),
                                                               []))

    def synopsises(self) -> list:
        return [
            render.Synopsis(
                arg.CommandLine([
                    arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                               _OPTION_PLACEHOLDER_ARGUMENT),
                    arg.Single(arg.Multiplicity.MANDATORY,
                               _FILE_ARGUMENT),
                ],
                    prefix=self.program_name)
            )]

    def argument_descriptions(self) -> list:
        return [
            self._actor_argument(),
            self._keep_sandbox_argument(),
            self._execute_act_phase_argument(),
            self._preprocessor_argument(),
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

    def _keep_sandbox_argument(self) -> render.DescribedArgument:
        extra_format_map = {
            'sandbox': formatting.concept(SANDBOX_CONCEPT.name().singular),
        }
        return render.DescribedArgument(_KEEP_SANDBOX_OPTION,
                                        self.parser.fnap(_KEEPING_SANDBOX_OPTION_DESCRIPTION, extra_format_map),
                                        see_also=[
                                            SANDBOX_CONCEPT.cross_reference_target(),
                                        ])

    def _execute_act_phase_argument(self) -> render.DescribedArgument:
        return render.DescribedArgument(_EXECUTING_ACT_PHASE_OPTION,
                                        self.parser.fnap(_EXECUTING_ACT_PHASE_OPTION_DESCRIPTION),
                                        )

    def _preprocessor_argument(self) -> render.DescribedArgument:
        extra_format_map = {
            'preprocessor': _PREPROCESSOR_OPTION.argument,
        }
        return render.DescribedArgument(_PREPROCESSOR_OPTION,
                                        self.parser.fnap(_PREPROCESSOR_OPTION_DESCRIPTION, extra_format_map),
                                        see_also=[
                                            PREPROCESSOR_CONCEPT.cross_reference_target(),
                                        ])


_DESCRIPTION = """\
Runs the test case in file {TEST_CASE_FILE}.
"""

_FILE_ARGUMENT = arg.Named(opt.TEST_CASE_FILE_ARGUMENT)

_OPTION_PLACEHOLDER_ARGUMENT = arg.Named('OPTION')

_ACTOR_OPTION_DESCRIPTION = """\
Specifies an {interpreter_actor}, by giving the executable program that serves as the interpreter.


{interpreter_program} is an absolute path followed by optional arguments
(using shell syntax).
"""

_ACTOR_OPTION = arg.option(long_name=opt.OPTION_FOR_ACTOR__LONG,
                           argument=opt.ACTOR_OPTION_ARGUMENT)

_KEEPING_SANDBOX_OPTION_DESCRIPTION = """\
Executes a test case as normal, but the {sandbox} is preserved,
and it's root directory is the only output on stdout.
"""

_KEEP_SANDBOX_OPTION = arg.option(long_name=opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG,
                                  short_name=opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT)

_EXECUTING_ACT_PHASE_OPTION_DESCRIPTION = """\
Executes the test case as usual, but instead of "reporting" the result,
the outcome of {phase[act]:syntax} is emitted:

output on stdout/stderr from {phase[act]:syntax} becomes the output on stdout/stderr;
the exit code from {phase[act]:syntax} becomes the exit code from the program."""

_EXECUTING_ACT_PHASE_OPTION = arg.option(long_name=opt.OPTION_FOR_EXECUTING_ACT_PHASE__LONG)

_PREPROCESSOR_OPTION_DESCRIPTION = """\
A program that transforms the test case file as the first step in the processing of it.


{preprocessor} is an executable program, together with optional command line arguments
(unix shell syntax).


When executed, it is given a single (additional) argument: the name of the test case file to preprocess.
"""

_PREPROCESSOR_OPTION = arg.option(long_name=opt.OPTION_FOR_PREPROCESSOR__LONG,
                                  argument=opt.PREPROCESSOR_OPTION_ARGUMENT)
