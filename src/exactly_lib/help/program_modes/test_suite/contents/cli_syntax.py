from exactly_lib import program_info
from exactly_lib.cli.cli_environment import common_cli_options as common_opts
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as case_opts
from exactly_lib.cli.cli_environment.program_modes.test_suite import command_line_options as opts
from exactly_lib.help.concepts.configuration_parameters import actor
from exactly_lib.help.concepts.plain_concepts.suite_reporter import SUITE_REPORTER_CONCEPT
from exactly_lib.help.cross_reference_id import TestSuiteSectionInstructionCrossReference
from exactly_lib.help.suite_reporters import names_and_cross_references as reporters
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.cli_program_documentation import CliProgramSyntaxDocumentation
from exactly_lib.help.utils.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_set import INSTRUCTION_NAME__ACTOR
from exactly_lib.test_suite.parser import SECTION_NAME__CONF
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class SuiteCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)
        self.parser = TextParser({
            'actor': formatting.concept(actor.ACTOR_CONCEPT.name().singular),
            'interpreter_actor': formatting.term(case_opts.INTERPRETER_ACTOR_TERM),
            'TEST_SUITE_FILE': _FILE_ARGUMENT.name,
            'reporter_name_list': ','.join(map(_reporter_name, reporters.ALL_SUITE_REPORTERS)),
            'default_reporter_name': _reporter_name(reporters.DEFAULT_REPORTER),

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
            self._reporter_argument(),
        ]

    def _actor_argument(self) -> cli_syntax.DescribedArgument:
        extra_format_map = {
            'interpreter_program': _ACTOR_OPTION.argument,
        }
        return cli_syntax.DescribedArgument(_ACTOR_OPTION,
                                            self.parser.fnap(_ACTOR_OPTION_DESCRIPTION, extra_format_map),
                                            see_also=[
                                                actor.ACTOR_CONCEPT.cross_reference_target(),
                                                TestSuiteSectionInstructionCrossReference(SECTION_NAME__CONF,
                                                                                          INSTRUCTION_NAME__ACTOR),
                                            ])

    def _reporter_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(_REPORTER_OPTION,
                                            self.parser.fnap(_REPORTER_OPTION_DESCRIPTION),
                                            see_also=[SUITE_REPORTER_CONCEPT.cross_reference_target()] +
                                                     reporters.all_suite_reporters_cross_refs()
                                            )


def synopsis() -> cli_syntax.Synopsis:
    command_line = arg.CommandLine([
        arg.Single(arg.Multiplicity.MANDATORY,
                   arg.Constant(common_opts.SUITE_COMMAND)),
        arg.Single(arg.Multiplicity.OPTIONAL,
                   _REPORTER_OPTION),
        arg.Single(arg.Multiplicity.OPTIONAL,
                   _ACTOR_OPTION),
        arg.Single(arg.Multiplicity.MANDATORY,
                   _FILE_ARGUMENT),
    ],
        prefix=program_info.PROGRAM_NAME)
    return cli_syntax.Synopsis(command_line,
                               docs.text('Runs a test suite.'))


_DESCRIPTION = """\
Runs the test suite in file {TEST_SUITE_FILE}.
"""

_ACTOR_OPTION_DESCRIPTION = """\
Specifies a default {interpreter_actor} to use for every test case in the suite.


Note: An {actor} specified in the suite will have precedence over the {actor}
specified by this option.


{interpreter_program} is the absolute path of an executable program,
followed by optional arguments (using shell syntax).
"""

_ACTOR_OPTION = arg.option(long_name=opts.OPTION_FOR_ACTOR__LONG,
                           argument=case_opts.ACTOR_OPTION_ARGUMENT)

_REPORTER_OPTION = arg.option(long_name=opts.OPTION_FOR_REPORTER__LONG,
                              argument=opts.REPORTER_OPTION_ARGUMENT)

_REPORTER_OPTION_DESCRIPTION = """\
Specifies in which format to report the execution of the test suite
(stdout, stderr, exitcode).


Options: {reporter_name_list} (default {default_reporter_name}).
"""

_FILE_ARGUMENT = arg.Named(opts.TEST_SUITE_FILE_ARGUMENT)


def _reporter_name(x: SingularNameAndCrossReferenceId) -> str:
    return formatting.cli_argument_option_string(x.singular_name)
