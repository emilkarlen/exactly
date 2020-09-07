from typing import List, Optional

from exactly_lib import program_info
from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.cli.definitions import common_cli_options as common_opts
from exactly_lib.cli.definitions.program_modes.test_suite import command_line_options as opts
from exactly_lib.common.help import headers
from exactly_lib.common.help.see_also import see_also_items_from_cross_refs
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import suite_reporters as reporters
from exactly_lib.definitions.entity.actors import SOURCE_INTERPRETER_ACTOR
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.contents_structure.cli_program import CliProgramSyntaxDocumentation
from exactly_lib.help.program_modes.test_suite.contents.specification import outcome
from exactly_lib.help.render.cli_program import \
    ProgramDocumentationSectionContentsConstructor
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.cli_syntax.elements import argument as arg
from exactly_lib.util.cli_syntax.elements import cli_program_syntax as cli_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h
from exactly_lib.util.textformat.section_target_hierarchy.as_section_contents import \
    SectionContentsConstructorFromHierarchyGenerator
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str) -> SectionHierarchyGenerator:
    return h.with_fixed_root_target(
        PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_SUITE_CLI),
        h.leaf(
            header,
            ProgramDocumentationSectionContentsConstructor(TestSuiteCliSyntaxDocumentation()))
    )


class TestSuiteCliSyntaxDocumentation(CliProgramSyntaxDocumentation):
    def __init__(self):
        super().__init__(program_info.PROGRAM_NAME)
        self.synopsis = synopsis()

    def description(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(_TP.text(misc_texts.SUITE_COMMAND_SINGLE_LINE_DESCRIPTION),
                                          docs.SectionContents(self.synopsis.paragraphs +
                                                               _TP.fnap(_DESCRIPTION_PARAGRAPH),
                                                               []))

    def synopsises(self) -> List[cli_syntax.Synopsis]:
        return [
            cli_syntax.Synopsis(command_line)
            for command_line in self.synopsis.command_lines
        ]

    def argument_descriptions(self) -> List[cli_syntax.DescribedArgument]:
        return [
            self._actor_argument(),
            self._reporter_argument(),
        ]

    def files(self) -> Optional[SectionContents]:
        return _TP.section_contents(DEFAULT_SUITE_FILES_DESCRIPTION)

    def outcome(self, environment: ConstructionEnvironment) -> Optional[docs.SectionContents]:
        contents_constructor = SectionContentsConstructorFromHierarchyGenerator(
            outcome.root('unused'))
        ret_val = contents_constructor.apply(environment)
        return ret_val

    def _actor_argument(self) -> cli_syntax.DescribedArgument:
        extra_format_map = {
            'interpreter_program': _ACTOR_OPTION.argument,
        }
        return cli_syntax.DescribedArgument(_ACTOR_OPTION,
                                            _TP.fnap(_ACTOR_OPTION_DESCRIPTION, extra_format_map),
                                            see_also_items=see_also_items_from_cross_refs([
                                                concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
                                                concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target,
                                                phase_infos.CONFIGURATION.instruction_cross_reference_target(
                                                    instruction_names.ACTOR_INSTRUCTION_NAME),
                                            ]))

    def _reporter_argument(self) -> cli_syntax.DescribedArgument:
        return cli_syntax.DescribedArgument(_REPORTER_OPTION,
                                            _TP.fnap(_REPORTER_OPTION_DESCRIPTION),
                                            see_also_items=see_also_items_from_cross_refs(
                                                [concepts.SUITE_REPORTER_CONCEPT_INFO.cross_reference_target] +
                                                reporters.all_suite_reporters_cross_refs()
                                            ))


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
                               _TP.text(_DESCRIPTION_PARAGRAPH))


_DESCRIPTION_PARAGRAPH = """\
Runs the test suite in file {TEST_SUITE_FILE}.
"""

_ACTOR_OPTION_DESCRIPTION = """\
Specifies a default {interpreter_actor} {actor} to use for every test case in the suite.


{interpreter_program} {is_a_system_cmd}


{NOTE} An {actor} specified in the test suite or individual test cases
will have precedence over the {actor} specified by this option.
"""

_ACTOR_OPTION = arg.short_long_option(long_name=common_cli_options.OPTION_FOR_ACTOR__LONG,
                                      argument=common_cli_options.ACTOR_OPTION_ARGUMENT)

_REPORTER_OPTION = arg.short_long_option(long_name=opts.OPTION_FOR_REPORTER__LONG,
                                         argument=opts.REPORTER_OPTION_ARGUMENT)

_REPORTER_OPTION_DESCRIPTION = """\
Specifies in which format to report the execution of the test suite
(stdout, stderr, exit code).


Options: {reporter_name_list} (default {default_reporter_name}).
"""

_FILE_ARGUMENT = arg.Named(opts.TEST_SUITE_FILE_ARGUMENT)

DEFAULT_SUITE_FILES_DESCRIPTION = """\
If {TEST_SUITE_FILE} is a directory
that contains a file "{default_suite_file}",
then this file becomes the suite file argument.
"""


def _reporter_name(x: SingularNameAndCrossReferenceId) -> str:
    return formatting.cli_argument_option_string(x.singular_name)


_TP = TextParser({
    'actor': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
    'interpreter_actor': formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name),
    'TEST_SUITE_FILE': _FILE_ARGUMENT.name,
    'reporter_name_list': ','.join(map(_reporter_name, reporters.ALL_SUITE_REPORTERS)),
    'default_reporter_name': _reporter_name(reporters.DEFAULT_REPORTER),
    'suite_reporter': formatting.concept_(concepts.SUITE_REPORTER_CONCEPT_INFO),
    'default_suite_file': file_names.DEFAULT_SUITE_FILE,
    'NOTE': headers.NOTE_LINE_HEADER,
    'is_a_system_cmd': misc_texts.IS_A_SYSTEM_CMD,
})
