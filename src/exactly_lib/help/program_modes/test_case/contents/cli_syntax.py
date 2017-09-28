from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, see_also_items_from_cross_refs
from exactly_lib.help.entities.concepts.configuration_parameters import actor
from exactly_lib.help.entities.concepts.configuration_parameters.actor import ACTOR_CONCEPT
from exactly_lib.help.entities.concepts.plain_concepts.preprocessor import PREPROCESSOR_CONCEPT
from exactly_lib.help.entities.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.entities.concepts.plain_concepts.shell_syntax import SHELL_SYNTAX_CONCEPT
from exactly_lib.help.utils.cli_program.cli_program_documentation import CliProgramSyntaxDocumentation
from exactly_lib.help.utils.cli_program.cli_program_documentation_rendering import \
    ProgramDocumentationSectionContentsRenderer
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator, leaf
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.phase_names import phase_name_dictionary
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


def generator(header: str) -> SectionHierarchyGenerator:
    return leaf(header, ProgramDocumentationSectionContentsRenderer(TestCaseCliSyntaxDocumentation()))


class TestCaseCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)
        from exactly_lib.help_texts.entity.actors import SOURCE_INTERPRETER_ACTOR
        self.parser = TextParser({
            'interpreter_actor': formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name),
            'TEST_CASE_FILE': _FILE_ARGUMENT.name,
            'phase': phase_name_dictionary(),
            'actor_concept': formatting.concept(ACTOR_CONCEPT.singular_name()),
            'shell_syntax_concept': formatting.concept(SHELL_SYNTAX_CONCEPT.singular_name()),
        })
        self.synopsis = synopsis()

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(self.synopsis.maybe_single_line_description,
                                          docs.SectionContents(self.parser.fnap(_DESCRIPTION),
                                                               []))

    def synopsises(self) -> list:
        return [
            cli_syntax.Synopsis(self.synopsis.command_line)
        ]

    def argument_descriptions(self) -> list:
        return [
            self._actor_argument(),
            self._keep_sandbox_argument(),
            self._execute_act_phase_argument(),
            self._preprocessor_argument(),
            self._suite_argument(),
        ]

    def _actor_argument(self) -> cli_syntax.DescribedArgument:
        extra_format_map = {
            'interpreter_program': _ACTOR_OPTION.argument,
        }
        return cli_syntax.DescribedArgument(_ACTOR_OPTION,
                                            self.parser.fnap(_ACTOR_OPTION_DESCRIPTION, extra_format_map),
                                            see_also_items=see_also_items_from_cross_refs([
                                                actor.ACTOR_CONCEPT.cross_reference_target(),
                                                SHELL_SYNTAX_CONCEPT.cross_reference_target()
                                            ]),
                                            )

    def _keep_sandbox_argument(self) -> cli_syntax.DescribedArgument:
        extra_format_map = {
            'sandbox': formatting.concept(SANDBOX_CONCEPT.name().singular),
        }
        return cli_syntax.DescribedArgument(_KEEP_SANDBOX_OPTION,
                                            self.parser.fnap(_KEEPING_SANDBOX_OPTION_DESCRIPTION, extra_format_map),
                                            see_also_items=[
                                                CrossReferenceIdSeeAlsoItem(SANDBOX_CONCEPT.cross_reference_target()),
                                            ])

    def _execute_act_phase_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(_EXECUTING_ACT_PHASE_OPTION,
                                            self.parser.fnap(_EXECUTING_ACT_PHASE_OPTION_DESCRIPTION),
                                            )

    def _preprocessor_argument(self) -> cli_syntax.DescribedArgument:
        extra_format_map = {
            'preprocessor': _PREPROCESSOR_OPTION.argument,
        }
        return cli_syntax.DescribedArgument(_PREPROCESSOR_OPTION,
                                            self.parser.fnap(_PREPROCESSOR_OPTION_DESCRIPTION, extra_format_map),
                                            see_also_items=see_also_items_from_cross_refs([
                                                PREPROCESSOR_CONCEPT.cross_reference_target(),
                                                SHELL_SYNTAX_CONCEPT.cross_reference_target()
                                            ]
                                            ))

    def _suite_argument(self) -> cli_syntax.DescribedArgument:
        extra_format_map = {
            'preprocessor': _PREPROCESSOR_OPTION.argument,
        }
        return cli_syntax.DescribedArgument(_SUITE_OPTION,
                                            self.parser.fnap(_SUITE_OPTION_DESCRIPTION, extra_format_map),
                                            )


def synopsis() -> cli_syntax.Synopsis:
    command_line = arg.CommandLine([
        arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                   _OPTION_PLACEHOLDER_ARGUMENT),
        arg.Single(arg.Multiplicity.MANDATORY,
                   _FILE_ARGUMENT)],
        prefix=program_info.PROGRAM_NAME)
    return cli_syntax.Synopsis(command_line,
                               docs.text('Runs a test case.'))


_DESCRIPTION = """\
Runs the test case in file {TEST_CASE_FILE}.
"""

_FILE_ARGUMENT = arg.Named(opt.TEST_CASE_FILE_ARGUMENT)

_OPTION_PLACEHOLDER_ARGUMENT = arg.Named('OPTION')

_ACTOR_OPTION_DESCRIPTION = """\
Specifies an {interpreter_actor} {actor_concept}, by giving the executable program that serves as the interpreter.


{interpreter_program} is an absolute path followed by optional arguments
(using {shell_syntax_concept}).


Note: An {actor_concept} specified in the test case will have precedence over the {actor_concept} given here.
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
(unix {shell_syntax_concept}).


When executed, it is given a single (additional) argument: the name of the test case file to preprocess.
"""

_PREPROCESSOR_OPTION = arg.option(long_name=opt.OPTION_FOR_PREPROCESSOR__LONG,
                                  argument=opt.PREPROCESSOR_OPTION_ARGUMENT)

_SUITE_OPTION_DESCRIPTION = """\
Reads configuration from the given suite.

The test case is executed as if it were part of the suite.
"""

_SUITE_OPTION = arg.option(long_name=opt.OPTION_FOR_SUITE__LONG,
                           argument=opt.SUITE_OPTION_METAVAR)
