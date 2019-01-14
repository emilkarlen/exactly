from typing import List

from exactly_lib import program_info
from exactly_lib.cli.definitions.program_modes.help import arguments_for
from exactly_lib.cli.definitions.program_modes.help import command_line_options as clo
from exactly_lib.definitions import doc_format, formatting
from exactly_lib.definitions.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib.definitions.entity.all_entity_types import ALL_ENTITY_TYPES_IN_DISPLAY_ORDER
from exactly_lib.help.contents_structure.cli_program import CliProgramSyntaxDocumentation
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.cli_syntax.elements.cli_program_syntax import DescribedArgument
from exactly_lib.util.cli_syntax.render.cli_program_syntax import CommandLineSyntaxRenderer
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import empty_section_contents


class HelpCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)

    def description(self) -> DescriptionWithSubSections:
        text = '{}s help system.'.format(formatting.program_name(program_info.PROGRAM_NAME))
        return DescriptionWithSubSections(docs.text(text),
                                          empty_section_contents())

    def initial_paragraphs(self) -> List[ParagraphItem]:
        command_line = arg.CommandLine([
            arg.Single(arg.Multiplicity.MANDATORY,
                       _c(clo.HELP)),
            arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                       _n('ARGUMENT'))],
            prefix=program_info.PROGRAM_NAME)

        command_line_syntax_text = CommandLineSyntaxRenderer().apply(command_line)
        return docs.paras(command_line_syntax_text)

    def synopsises(self) -> List[cli_syntax.Synopsis]:
        non_entities_help = [
            _synopsis([], 'Gives a brief description of the program.'),
            _synopsis([_c(clo.HELP)], 'Displays this help.'),
            _synopsis([_c(clo.HTML_DOCUMENTATION)],
                      'Generates a HTML version of all help information available in the program.'),
            _synopsis(_ns(arguments_for.case_cli_syntax()), 'Describes the test case command line syntax.'),
            _synopsis(_ns(arguments_for.case_specification()), 'Specification of the test case functionality.'),

            _synopsis(_ns(arguments_for.case_phase_for_name('PHASE')), 'Describes a test case phase.'),
            _synopsis(_ns(arguments_for.case_instructions_in_phase('PHASE')),
                      'Lists instructions in PHASE.'),
            _synopsis(_ns(arguments_for.case_instruction_in_phase('PHASE', 'INSTRUCTION')),
                      'Describes an instruction in a test case phase.'),

            _synopsis(_ns(arguments_for.case_instructions()),
                      'Lists instructions per test case phase.'),
            _synopsis(_ns(arguments_for.case_instruction_search('INSTRUCTION')),
                      'Describes all test case instructions with the given name.'),
            _synopsis(_ns(arguments_for.suite_cli_syntax()), 'Describes the test suite command line syntax.'),
            _synopsis(_ns(arguments_for.suite_specification()),
                      'Specification of the test suite functionality.'),
            _synopsis(_ns(arguments_for.suite_section_for_name('SECTION')), 'Describes a test suite section.'),
            _synopsis(_ns(arguments_for.suite_instruction_in_section('SECTION', 'INSTRUCTION')),
                      'Describes an instruction in a test suite section.'),
            _synopsis(_ns(arguments_for.symbol_cli_syntax()),
                      'Describes the symbol usages report command line syntax.'),
        ]

        return non_entities_help + self._entities_help()

    def argument_descriptions(self) -> List[DescribedArgument]:
        return []

    @staticmethod
    def _entities_help() -> List[cli_syntax.Synopsis]:
        def row(names: EntityTypeNames) -> List[docs.TableCell]:
            return [
                docs.text_cell(doc_format.syntax_text(names.identifier)),
                docs.text_cell(names.name.plural.capitalize()),
            ]

        entities_table = docs.plain_table(map(row, ALL_ENTITY_TYPES_IN_DISPLAY_ORDER))

        arguments = [
            arg.Single(arg.Multiplicity.MANDATORY,
                       _c(clo.HELP)),
            arg.Single(arg.Multiplicity.MANDATORY,
                       _n('ENTITY-TYPE')),
            arg.Single(arg.Multiplicity.OPTIONAL,
                       _n('ENTITY-NAME'))
        ]
        single_line_description = 'Lists all entities of a type; or describes a given entity.'
        return [
            cli_syntax.Synopsis(arg.CommandLine(arguments),
                                docs.text(single_line_description),
                                [entities_table])
        ]


def _synopsis(additional_arguments: list,
              single_line_description: str) -> cli_syntax.Synopsis:
    arguments = [_c(clo.HELP)] + additional_arguments
    return cli_syntax.Synopsis(arg.CommandLine(list(map(_single_mandatory_arg, arguments))),
                               docs.text(single_line_description))


def _ns(names: list) -> list:
    return list(map(_n, names))


def _single_mandatory_arg(argument: arg.Argument) -> arg.ArgumentUsage:
    return arg.Single(arg.Multiplicity.MANDATORY,
                      argument)


_c = arg.Constant

_n = arg.Named
