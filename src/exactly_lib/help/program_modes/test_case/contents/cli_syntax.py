from typing import List, Optional

from exactly_lib import program_info
from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.cli.definitions.program_modes.test_case import command_line_options as opt
from exactly_lib.cli.program_modes.test_case import argument_parsing
from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, see_also_items_from_cross_refs
from exactly_lib.definitions.entity.concepts import SANDBOX_CONCEPT_INFO, SHELL_SYNTAX_CONCEPT_INFO, \
    PREPROCESSOR_CONCEPT_INFO, ACTOR_CONCEPT_INFO
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.contents_structure.cli_program import CliProgramSyntaxDocumentation
from exactly_lib.help.program_modes.test_case.contents.specification import outcome as case_outcome_help
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import leaf
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


def generator(header: str) -> SectionHierarchyGenerator:
    return leaf(header, ProgramDocumentationSectionContentsConstructor(TestCaseCliSyntaxDocumentation()))


class TestCaseCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)
        self.synopsis = synopsis()

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(_TP.text(_SINGLE_LINE_DESCRIPTION),
                                          docs.SectionContents(self.synopsis.paragraphs +
                                                               _TP.fnap(_DESCRIPTION_PARAGRAPH),
                                                               []))

    def synopsises(self) -> List[cli_syntax.Synopsis]:
        return [
            cli_syntax.Synopsis(self.synopsis.command_line)
        ]

    def argument_descriptions(self) -> List[cli_syntax.DescribedArgument]:
        return [
            self._actor_argument(),
            self._keep_sandbox_argument(),
            self._execute_act_phase_argument(),
            self._preprocessor_argument(),
            self._suite_argument(),
        ]

    def outcome(self, environment: ConstructionEnvironment) -> Optional[docs.SectionContents]:
        paragraphs = case_outcome_help.TEXT_PARSER.fnap(case_outcome_help.REPORTING)
        paragraphs += _TP.fnap(_OUTCOME_INITIAL_PARAGRAPHS_EXTRA)
        return docs.section_contents(paragraphs,
                                     [docs.section(case_outcome_help.ALL_EXIT_VALUES_SUMMARY_TABLE_HEADER,
                                                   [case_outcome_help.all_exit_values_summary_table()])])

    def _actor_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            _ACTOR_OPTION,
            argument_parsing.TEXT_PARSER.fnap(argument_parsing.ACTOR_OPTION_DESCRIPTION),
            see_also_items=see_also_items_from_cross_refs([
                ACTOR_CONCEPT_INFO.cross_reference_target,
                SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target
            ]),
        )

    def _keep_sandbox_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            _KEEP_SANDBOX_OPTION,
            argument_parsing.TEXT_PARSER.fnap(argument_parsing.KEEPING_SANDBOX_OPTION_DESCRIPTION),
            see_also_items=[
                CrossReferenceIdSeeAlsoItem(
                    SANDBOX_CONCEPT_INFO.cross_reference_target),
            ])

    def _execute_act_phase_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            _EXECUTING_ACT_PHASE_OPTION,
            argument_parsing.TEXT_PARSER.fnap(argument_parsing.EXECUTING_ACT_PHASE_OPTION_DESCRIPTION),
        )

    def _preprocessor_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            _PREPROCESSOR_OPTION,
            argument_parsing.TEXT_PARSER.fnap(argument_parsing.PREPROCESSOR_OPTION_DESCRIPTION),
            see_also_items=see_also_items_from_cross_refs([
                PREPROCESSOR_CONCEPT_INFO.cross_reference_target,
                SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target
            ]
            ))

    def _suite_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(
            _SUITE_OPTION,
            argument_parsing.TEXT_PARSER.fnap(argument_parsing.SUITE_OPTION_DESCRIPTION),
        )


def synopsis() -> cli_syntax.Synopsis:
    command_line = arg.CommandLine([
        arg.Single(arg.Multiplicity.ZERO_OR_MORE,
                   _OPTION_PLACEHOLDER_ARGUMENT),
        arg.Single(arg.Multiplicity.MANDATORY,
                   _FILE_ARGUMENT)],
        prefix=program_info.PROGRAM_NAME)
    return cli_syntax.Synopsis(command_line,
                               _TP.text(_DESCRIPTION_PARAGRAPH))


_SINGLE_LINE_DESCRIPTION = 'Runs a test case'

_DESCRIPTION_PARAGRAPH = """Runs the test case in file {TEST_CASE_FILE}.


If there exists a file "{default_suite_file}" in the same directory as {TEST_CASE_FILE},
then this file must be a test suite, and the test case is run as part of this suite. 
"""

_OUTCOME_INITIAL_PARAGRAPHS_EXTRA = """\
See test case specification for details.
"""

_FILE_ARGUMENT = arg.Named(opt.TEST_CASE_FILE_ARGUMENT)

_OPTION_PLACEHOLDER_ARGUMENT = arg.Named('OPTION')

_ACTOR_OPTION = arg.short_long_option(long_name=common_cli_options.OPTION_FOR_ACTOR__LONG,
                                      argument=common_cli_options.ACTOR_OPTION_ARGUMENT)

_KEEP_SANDBOX_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG,
                                             short_name=opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT)

_EXECUTING_ACT_PHASE_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_EXECUTING_ACT_PHASE__LONG)

_PREPROCESSOR_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_PREPROCESSOR__LONG,
                                             argument=opt.PREPROCESSOR_OPTION_ARGUMENT)

_SUITE_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_SUITE__LONG,
                                      argument=opt.SUITE_OPTION_METAVAR)

_TP = TextParser({
    'TEST_CASE_FILE': _FILE_ARGUMENT.name,
    'default_suite_file': file_names.DEFAULT_SUITE_FILE,
})
