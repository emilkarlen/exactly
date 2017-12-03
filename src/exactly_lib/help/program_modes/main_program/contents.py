from exactly_lib import program_info
from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND
from exactly_lib.cli.cli_environment.program_modes.help import arguments_for as help_arguments
from exactly_lib.cli.cli_environment.program_modes.help import command_line_options as clo
from exactly_lib.help.contents_structure.cli_program import CliProgramSyntaxDocumentation
from exactly_lib.help.program_modes.test_case.contents import cli_syntax as test_case_cli_syntax
from exactly_lib.help.program_modes.test_suite.contents import cli_syntax as test_suite_cli_syntax
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class MainCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(docs.text(_SINGLE_LINE_DESCRIPTION),
                                          docs.SectionContents([], []))

    def synopsises(self) -> list:
        return [
            test_case_cli_syntax.synopsis(),
            test_suite_cli_syntax.synopsis(),
            _help_toc_synopsis(),
            _html_help_synopsis(),
            _simple_argument_synopsis(),
        ]

    def argument_descriptions(self) -> list:
        return []


_SINGLE_LINE_DESCRIPTION = 'Runs a test case, a test suite, or displays help.'


def _help_toc_synopsis() -> cli_syntax.Synopsis:
    return _help_synopsis(help_arguments.help_help(),
                          'Help on the {} command.'.format(HELP_COMMAND))


def _html_help_synopsis() -> cli_syntax.Synopsis:
    return _help_synopsis(help_arguments.html_doc(),
                          'Outputs all available help as html.')


def _simple_argument_synopsis() -> cli_syntax.Synopsis:
    help_arg = arg.Single(arg.Multiplicity.MANDATORY,
                          arg.Option(arg.OptionName(long_name='help')))
    return _synopsis_for_args([help_arg],
                              'Displays simple help on command line arguments.')


def _help_synopsis(additional_mandatory_constant_arguments: list,
                   single_line_description: str) -> cli_syntax.Synopsis:
    constants = [clo.HELP] + additional_mandatory_constant_arguments
    return _synopsis_for_args(list(map(_single_mandatory_constant, constants)),
                              single_line_description)


def _synopsis_for_args(argument_usages: list,
                       single_line_description: str) -> arg.CommandLine:
    return cli_syntax.Synopsis(arg.CommandLine(argument_usages,
                                               prefix=program_info.PROGRAM_NAME),
                               docs.text(single_line_description))


def _single_mandatory_constant(constant: str) -> arg.ArgumentUsage:
    return arg.Single(arg.Multiplicity.MANDATORY,
                      arg.Constant(constant))
