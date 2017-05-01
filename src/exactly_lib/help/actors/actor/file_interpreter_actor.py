from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options
from exactly_lib.common.help.cross_reference_id import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help.actors.actor.common import ARGUMENT_SYNTAX_ELEMENT, \
    SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH, ActPhaseDocumentationSyntaxBase
from exactly_lib.help.actors.contents_structure import ActorDocumentation
from exactly_lib.help.actors.names_and_cross_references import FILE_INTERPRETER_ACTOR
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.concepts.plain_concepts.shell_syntax import SHELL_SYNTAX_CONCEPT
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME, ACT_PHASE_NAME
from exactly_lib.help_texts.test_suite import formatted_section_names
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import section_contents
from exactly_lib.util.textformat.structure.structures import text


class FileInterpreterActorDocumentation(ActorDocumentation):
    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()

    def __init__(self):
        super().__init__(FILE_INTERPRETER_ACTOR)
        from exactly_lib.execution.exit_values import EXECUTION__VALIDATE
        format_map = {
            'phase': phase_name_dictionary(),
            'sandbox': formatting.concept(SANDBOX_CONCEPT.name().singular),
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'VALIDATION': EXECUTION__VALIDATE.exit_identifier,
            'actor_option': formatting.cli_option(command_line_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'shell_syntax_concept': formatting.concept(SHELL_SYNTAX_CONCEPT.singular_name()),
            'LINE_COMMENT_MARKER': formatting.string_constant(LINE_COMMENT_MARKER),
        }
        self._parser = TextParser(format_map)

    def act_phase_contents(self) -> doc.SectionContents:
        return section_contents(self._parser.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> doc.SectionContents:
        documentation = ActPhaseDocumentationSyntax()
        initial_paragraphs = self._parser.fnap(SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH)
        sub_sections = []
        synopsis_section = doc.Section(text('SYNOPSIS'),
                                       invokation_variants_content(None,
                                                                   documentation.invokation_variants(),
                                                                   documentation.syntax_element_descriptions()))
        sub_sections.append(synopsis_section)
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _see_also_specific(self) -> list:
        return [
            SHELL_SYNTAX_CONCEPT.cross_reference_target(),
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   ACTOR_INSTRUCTION_NAME),
            TestSuiteSectionInstructionCrossReference(formatted_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                      ACTOR_INSTRUCTION_NAME),
        ]


DOCUMENTATION = FileInterpreterActorDocumentation()


class ActPhaseDocumentationSyntax(ActPhaseDocumentationSyntaxBase):
    def __init__(self):
        self.file = path_syntax.FILE_ARGUMENT
        self.argument = a.Named('ARGUMENT')
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        fm = {
            'FILE': self.file.name,
            'ARGUMENT': self.argument.name,
            'actor': formatting.concept(ACTOR_CONCEPT.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
            'home_directory_concept': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'shell_syntax_concept': formatting.concept(SHELL_SYNTAX_CONCEPT.name().singular),
        }
        super().__init__(TextParser(fm))

    def invokation_variants(self) -> list:
        executable_arg = a.Single(a.Multiplicity.MANDATORY, self.file)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, self.argument)
        return [
            InvokationVariant(self._cl_syntax_for_args([executable_arg,
                                                        optional_arguments_arg])),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.file.name,
                                     self._paragraphs(_SOURCE_FILE_SYNTAX_ELEMENT)),
            SyntaxElementDescription(self.argument.name,
                                     self._paragraphs(ARGUMENT_SYNTAX_ELEMENT)),
        ]


_SOURCE_FILE_SYNTAX_ELEMENT = """\
The path of an existing source code file.


If the path is not absolute, then it is relative the {home_directory_concept}.


Uses {shell_syntax_concept}.
"""

_ACT_PHASE_CONTENTS = """\
A single line which is a file name followed by optional arguments.


The file name and arguments may be quoted according to {shell_syntax_concept}.
"""
