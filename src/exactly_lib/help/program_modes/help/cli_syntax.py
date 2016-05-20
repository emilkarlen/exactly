from exactly_lib import program_info
from exactly_lib.cli.cli_environment.common_cli_options import HELP_COMMAND
from exactly_lib.cli.program_modes.help import argument_parsing as opt
from exactly_lib.cli.program_modes.help import arguments_for
from exactly_lib.help.utils.cli_program_documentation import CliProgramSyntaxDocumentation
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class HelpCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)

    def description(self) -> DescriptionWithSubSections:
        cmd_line_description = ' '.join([self.program_name, HELP_COMMAND, 'ARGUMENT...'])
        text = '"%s" %s' % (cmd_line_description, 'is able to display help about some topics.')
        return DescriptionWithSubSections(docs.text(text),
                                          docs.SectionContents([], []))

    def synopsises(self) -> list:
        return [
            _synopsis([], 'Brief description of the program.'),
            _synopsis([_c(opt.HELP)], 'Displays this help.'),
            _synopsis([_c(opt.HTML_DOCUMENTATION)],
                      'Generates a HTML version of all help information available in the program.'),
            _synopsis(_ns(arguments_for.case_cli_syntax()), 'Describes the test case command line syntax.'),
            _synopsis(_ns(arguments_for.case_specification()), 'Describes the test case functionality.'),
            _synopsis(_ns(arguments_for.case_phase_for_name('PHASE')), 'Describes a test case phase.'),
            _synopsis(_ns(arguments_for.case_instruction_in_phase('PHASE', 'INSTRUCTION')),
                      'Describes an instruction in a test case phase.'),
            _synopsis(_ns(arguments_for.case_instructions()), 'Lists instructions per test case phase.'),
            _synopsis(_ns(arguments_for.case_instruction_search('INSTRUCTION')),
                      'Describes all test case instructions with the given name.'),
            _synopsis(_ns(arguments_for.suite_cli_syntax()), 'Describes the test suite command line syntax.'),
            _synopsis(_ns(arguments_for.suite_specification()), 'Describes the test suite functionality.'),
            _synopsis(_ns(arguments_for.suite_section_for_name('SECTION')), 'Describes a test suite section.'),
            _synopsis(_ns(arguments_for.suite_instruction_in_section('SECTION', 'INSTRUCTION')),
                      'Describes an instruction in a suite section.'),
            _synopsis(_ns(arguments_for.concept_list()), 'Lists all concepts.'),
            _synopsis(_ns(arguments_for.concept_single('CONCEPT')), 'Describes a concept.'),
        ]

    def argument_descriptions(self) -> list:
        return []


def _synopsis(additional_arguments: list,
              single_line_description: str) -> cli_syntax.Synopsis:
    arguments = [_c(opt.HELP)] + additional_arguments
    return cli_syntax.Synopsis(arg.CommandLine(list(map(_single_mandatory_arg, arguments))),
                               docs.text(single_line_description))


def _ns(names: list) -> list:
    return list(map(_n, names))


def _single_mandatory_arg(argument: arg.Argument) -> arg.ArgumentUsage:
    return arg.Single(arg.Multiplicity.MANDATORY,
                      argument)


def _c(s: str) -> arg.Argument:
    return arg.Constant(s)


def _n(s: str) -> arg.Argument:
    return arg.Named(s)
