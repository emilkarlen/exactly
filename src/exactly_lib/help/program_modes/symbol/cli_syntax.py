from typing import List, Optional

from exactly_lib import program_info
from exactly_lib.cli.definitions import common_cli_options as common_opts
from exactly_lib.cli.definitions.program_modes.symbol import command_line_options
from exactly_lib.definitions import misc_texts, instruction_arguments
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import concepts, syntax_elements
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.contents_structure.cli_program import CliProgramSyntaxDocumentation
from exactly_lib.help.program_modes.common.cli_syntax import FILES_DESCRIPTION_WITH_DEFAULT_SUITE
from exactly_lib.help.program_modes.test_suite.contents.cli_syntax import DEFAULT_SUITE_FILES_DESCRIPTION
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser

_INDIVIDUAL_REFERENCES_OPTION = arg.short_long_option(long_name=command_line_options.OPTION_FOR_SYMBOL_REFERENCES__LONG)


def root(header: str) -> SectionHierarchyGenerator:
    return h.with_fixed_root_target(
        PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.SYMBOL_CLI),
        h.leaf(
            header,
            ProgramDocumentationSectionContentsConstructor(SymbolCliSyntaxDocumentation()))
    )


class SymbolCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(_TP.text(misc_texts.SYMBOL_COMMAND_SINGLE_LINE_DESCRIPTION),
                                          docs.section_contents([]))

    def synopsises(self) -> List[cli_syntax.Synopsis]:
        return [
            synopsis_all(),
            synopsis_individual()
        ]

    def argument_descriptions(self) -> List[cli_syntax.DescribedArgument]:
        return [
            self._test_case_option_argument(),
            self._test_suite_option_argument(),
        ]

    def files(self) -> Optional[docs.SectionContents]:
        list_items = [
            docs.list_item(_TP.text(_FILES_WHEN_REPORTING_FOR_A_CASE_HEADER),
                           _TP.fnap(FILES_DESCRIPTION_WITH_DEFAULT_SUITE)
                           ),
            docs.list_item(_TP.text(_FILES_WHEN_REPORTING_FOR_A_SUITE_HEADER),
                           _TP.fnap(DEFAULT_SUITE_FILES_DESCRIPTION)
                           ),
        ]
        return docs.section_contents([
            docs.simple_list_with_space_between_elements_and_content(
                list_items,
                docs.lists.ListType.ITEMIZED_LIST
            )
        ])

    def outcome(self, environment: ConstructionEnvironment) -> Optional[docs.SectionContents]:
        return _TP.section_contents(_OUTCOME)

    def _test_case_option_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            CASE_OPTION_ARGUMENT,
            _TP.fnap(_CORRESPONDS_TO_TEST_CASE_ARGUMENT))

    def _test_suite_option_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            SUITE_OPTION_ARGUMENT,
            _TP.fnap(_CORRESPONDS_TO_TEST_SUITE_ARGUMENT))

    def see_also(self) -> List[SeeAlsoTarget]:
        return [
            PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_CLI),
            PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_SUITE_CLI),
        ]


CASE_OPTION_ARGUMENT = arg.Named('TEST-CASE-OPTION')
SUITE_OPTION_ARGUMENT = arg.Named('TEST-SUITE-OPTION')
SYMBOL_OPTION_ARGUMENT = arg.Named('SYMBOL-OPTION')


def synopsis_general() -> cli_syntax.Synopsis:
    command_line = _command_line__case([
        arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                   SYMBOL_OPTION_ARGUMENT)
    ])
    return cli_syntax.Synopsis(command_line,
                               _TP.text(_SINGLE_LINE_DESCRIPTION_FOR_CLI_SYNTAX))


def synopsis_all() -> cli_syntax.Synopsis:
    return cli_syntax.Synopsis(_command_line__case([]),
                               paragraphs=_TP.fnap(_DESCRIPTION_PARAGRAPHS_ALL),
                               additional_command_lines=[_command_line__suite([])])


def synopsis_individual() -> cli_syntax.Synopsis:
    additional_arguments = [
        arg.Single(arg.Multiplicity.MANDATORY,
                   syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument),
        arg.Single(arg.Multiplicity.OPTIONAL,
                   _INDIVIDUAL_REFERENCES_OPTION),
    ]
    return cli_syntax.Synopsis(_command_line__case(additional_arguments),
                               paragraphs=_TP.fnap(_DESCRIPTION_PARAGRAPHS_INDIVIDUAL),
                               additional_command_lines=[_command_line__suite(additional_arguments)])


def _command_line__case(additional_arguments: List[arg.ArgumentUsage]) -> arg.CommandLine:
    return arg.CommandLine(
        _common_initial_args__case() + additional_arguments,
        prefix=program_info.PROGRAM_NAME
    )


def _command_line__suite(additional_arguments: List[arg.ArgumentUsage]) -> arg.CommandLine:
    return arg.CommandLine(
        _common_initial_args__suite() + additional_arguments,
        prefix=program_info.PROGRAM_NAME
    )


def _common_initial_args__case() -> List[arg.ArgumentUsage]:
    return [
        arg.Single(arg.Multiplicity.MANDATORY,
                   arg.Constant(common_opts.SYMBOL_COMMAND)),
        arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                   CASE_OPTION_ARGUMENT),
        arg.Single(arg.Multiplicity.MANDATORY,
                   instruction_arguments.FILE_ARGUMENT),
    ]


def _common_initial_args__suite() -> List[arg.ArgumentUsage]:
    return [
        arg.Single(arg.Multiplicity.MANDATORY,
                   arg.Constant(common_opts.SYMBOL_COMMAND)),
        arg.Single(arg.Multiplicity.MANDATORY,
                   arg.Constant(common_opts.SUITE_COMMAND)),
        arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                   SUITE_OPTION_ARGUMENT),
        arg.Single(arg.Multiplicity.MANDATORY,
                   instruction_arguments.FILE_ARGUMENT),
    ]


_SINGLE_LINE_DESCRIPTION_FOR_CLI_SYNTAX = """\
Reports usage of {symbol:s} in the test case or test suite {FILE}.
"""

_DESCRIPTION_PARAGRAPHS_ALL = """\
Reports all user defined {symbol:s} in the case/suite.


Each symbol is reported on a separate line,
together with its type and the number of references to it.
"""

_DESCRIPTION_PARAGRAPHS_INDIVIDUAL = """\
Reports information about a {symbol}.


If only {SYMBOL_NAME} is given, the definition of the {symbol} is reported.


If {ref_option} is given, all references to the {symbol} are reported. 
"""

_OUTCOME = """\
The report is printed on {stdout}.


Errors are reported with {exit_code:s} and {exit_identifier:s}
corresponding to the outcome of running the corresponding test case or test suite.
But the case/suite is not executed,
so no execution errors occur.
"""

_CORRESPONDS_TO_TEST_CASE_ARGUMENT = """\
Corresponds to the options for running a test case.
"""

_CORRESPONDS_TO_TEST_SUITE_ARGUMENT = """\
Corresponds to the options for running a test suite.
"""

_FILES_WHEN_REPORTING_FOR_A_CASE_HEADER = 'When reporting from a test case'
_FILES_WHEN_REPORTING_FOR_A_SUITE_HEADER = 'When reporting from a test suite'

_TP = TextParser({
    'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
    'SYMBOL_NAME': syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.singular_name,
    'exit_code': misc_texts.EXIT_CODE,
    'stdout': misc_texts.STDOUT,
    'exit_identifier': misc_texts.EXIT_IDENTIFIER,
    'TEST_CASE_FILE': instruction_arguments.FILE_ARGUMENT.name,
    'TEST_SUITE_FILE': instruction_arguments.FILE_ARGUMENT.name,
    'FILE': instruction_arguments.FILE_ARGUMENT.name,
    'default_suite_file': file_names.DEFAULT_SUITE_FILE,
    'ref_option': command_line_options.OPTION_FOR_SYMBOL_REFERENCES,
})
