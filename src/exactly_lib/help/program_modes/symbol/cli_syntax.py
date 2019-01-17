from typing import List, Optional

import exactly_lib.cli.definitions.program_modes.symbol.command_line_options
from exactly_lib import program_info
from exactly_lib.cli.definitions import common_cli_options as common_opts
from exactly_lib.cli.definitions.program_modes.symbol.command_line_options import OPTION_FOR_SYMBOL_REFERENCES__LONG
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import concepts, syntax_elements
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.contents_structure.cli_program import CliProgramSyntaxDocumentation
from exactly_lib.help.program_modes.common.cli_syntax import FILES_DESCRIPTION_WITH_DEFAULT_SUITE, \
    TEST_CASE_FILE_ARGUMENT
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

_INDIVIDUAL_REFERENCES_OPTION = arg.short_long_option(long_name=OPTION_FOR_SYMBOL_REFERENCES__LONG)


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
        ]

    def files(self) -> Optional[docs.SectionContents]:
        return _TP.section_contents(FILES_DESCRIPTION_WITH_DEFAULT_SUITE)

    def outcome(self, environment: ConstructionEnvironment) -> Optional[docs.SectionContents]:
        return _TP.section_contents(_OUTCOME)

    def _test_case_option_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            CASE_OPTION_ARGUMENT,
            _TP.fnap(_CORRESPONDS_TO_TEST_CASE_ARGUMENT))

    def see_also(self) -> List[SeeAlsoTarget]:
        return [
            PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_CLI),
        ]


CASE_OPTION_ARGUMENT = arg.Named('TEST-CASE-OPTION')
SYMBOL_OPTION_ARGUMENT = arg.Named('SYMBOL-OPTION')


def synopsis_general() -> cli_syntax.Synopsis:
    command_line = _command_line([
        arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                   SYMBOL_OPTION_ARGUMENT)
    ])
    return cli_syntax.Synopsis(command_line,
                               _TP.text(_SINGLE_LINE_DESCRIPTION_FOR_CLI_SYNTAX))


def synopsis_all() -> cli_syntax.Synopsis:
    command_line = _command_line([])
    return cli_syntax.Synopsis(command_line,
                               paragraphs=_TP.fnap(_DESCRIPTION_PARAGRAPHS_ALL))


def synopsis_individual() -> cli_syntax.Synopsis:
    command_line = _command_line([
        arg.Single(arg.Multiplicity.MANDATORY,
                   syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument),
        arg.Single(arg.Multiplicity.OPTIONAL,
                   _INDIVIDUAL_REFERENCES_OPTION),
    ])
    return cli_syntax.Synopsis(command_line,
                               paragraphs=_TP.fnap(_DESCRIPTION_PARAGRAPHS_INDIVIDUAL))


def _command_line(additional_arguments: List[arg.ArgumentUsage]) -> arg.CommandLine:
    return arg.CommandLine(
        _common_initial_args() + additional_arguments,
        prefix=program_info.PROGRAM_NAME
    )


def _common_initial_args() -> List[arg.ArgumentUsage]:
    return [
        arg.Single(arg.Multiplicity.MANDATORY,
                   arg.Constant(common_opts.SYMBOL_COMMAND)),
        arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                   CASE_OPTION_ARGUMENT),
        arg.Single(arg.Multiplicity.MANDATORY,
                   TEST_CASE_FILE_ARGUMENT),
    ]


_SINGLE_LINE_DESCRIPTION_FOR_CLI_SYNTAX = """\
Reports usage of {symbol:s} in the test case {TEST_CASE_FILE}.
"""

_DESCRIPTION_PARAGRAPHS_ALL = """\
Reports all {symbol:s} defined in the case.


Each symbol is reported on a separate line,
together with its type and the number of references to it.
"""

_DESCRIPTION_PARAGRAPHS_INDIVIDUAL = """\
Reports information about a {symbol} that has been defined in the case.


If only {SYMBOL_NAME} is given, the definition of the {symbol} is reported.


If {ref_option} is given, all references to the {symbol} are reported. 
"""

_OUTCOME = """\
The report is printed on stdout.


Errors are reported with {exit_code:s} and {exit_identifier:s}
corresponding to the outcome of running the corresponding test case.

But the test case is not executed,
so no execution errors occur.
"""

_CORRESPONDS_TO_TEST_CASE_ARGUMENT = """\
Corresponds to the options for running a test case.
"""

_TP = TextParser({
    'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
    'SYMBOL_NAME': syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.singular_name,
    'exit_code': misc_texts.EXIT_CODE,
    'exit_identifier': misc_texts.EXIT_IDENTIFIER,
    'TEST_CASE_FILE': TEST_CASE_FILE_ARGUMENT.name,
    'default_suite_file': file_names.DEFAULT_SUITE_FILE,
    'ref_option': exactly_lib.cli.definitions.program_modes.symbol.command_line_options.OPTION_FOR_SYMBOL_REFERENCES,
})
