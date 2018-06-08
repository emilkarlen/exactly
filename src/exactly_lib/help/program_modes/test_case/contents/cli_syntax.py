from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.cli.program_modes.test_case import argument_parsing
from exactly_lib.common.help.see_also import CrossReferenceIdSeeAlsoItem, see_also_items_from_cross_refs
from exactly_lib.definitions.entity.concepts import SANDBOX_CONCEPT_INFO, SHELL_SYNTAX_CONCEPT_INFO, \
    PREPROCESSOR_CONCEPT_INFO, ACTOR_CONCEPT_INFO
from exactly_lib.help.contents_structure.cli_program import CliProgramSyntaxDocumentation
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
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
        self.parser = TextParser({
            'TEST_CASE_FILE': _FILE_ARGUMENT.name,
        })
        self.synopsis = synopsis()

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(self.synopsis.maybe_single_line_description,
                                          docs.SectionContents(self.synopsis.paragraphs +
                                                               self.parser.fnap(_DESCRIPTION),
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
                               docs.text('Runs a test case.'))


_DESCRIPTION = """\
Runs the test case in file {TEST_CASE_FILE}.
"""

_FILE_ARGUMENT = arg.Named(opt.TEST_CASE_FILE_ARGUMENT)

_OPTION_PLACEHOLDER_ARGUMENT = arg.Named('OPTION')

_ACTOR_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_ACTOR__LONG,
                                      argument=opt.ACTOR_OPTION_ARGUMENT)

_KEEP_SANDBOX_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__LONG,
                                             short_name=opt.OPTION_FOR_KEEPING_SANDBOX_DIRECTORY__SHORT)

_EXECUTING_ACT_PHASE_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_EXECUTING_ACT_PHASE__LONG)

_PREPROCESSOR_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_PREPROCESSOR__LONG,
                                             argument=opt.PREPROCESSOR_OPTION_ARGUMENT)

_SUITE_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_SUITE__LONG,
                                      argument=opt.SUITE_OPTION_METAVAR)
