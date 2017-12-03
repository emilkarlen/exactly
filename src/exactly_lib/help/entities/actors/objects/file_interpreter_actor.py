from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, InvokationVariant
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help.entities.actors.objects.common import ARGUMENT_SYNTAX_ELEMENT, \
    SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH, ActPhaseDocumentationSyntaxBase
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render import doc_utils
from exactly_lib.help_texts import instruction_arguments, formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.entity import concepts, conf_params
from exactly_lib.help_texts.entity.actors import FILE_INTERPRETER_ACTOR
from exactly_lib.help_texts.test_case.actors import file_interpreter as help_texts
from exactly_lib.help_texts.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, \
    ACT_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.help_texts.test_suite import formatted_section_names
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case_file_structure import sandbox_directory_structure as sds
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import section_contents
from exactly_lib.util.textformat.textformat_parser import TextParser


class FileInterpreterActorDocumentation(ActorDocumentation):
    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()

    def __init__(self):
        super().__init__(FILE_INTERPRETER_ACTOR)
        from exactly_lib.processing.exit_values import EXECUTION__VALIDATE
        format_map = {
            'phase': PHASE_NAME_DICTIONARY,
            'sandbox': formatting.concept_(concepts.SANDBOX_CONCEPT_INFO),
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'VALIDATION': EXECUTION__VALIDATE.exit_identifier,
            'actor_option': formatting.cli_option(command_line_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
            'LINE_COMMENT_MARKER': formatting.string_constant(LINE_COMMENT_MARKER),
        }
        self._parser = TextParser(format_map)

    def act_phase_contents(self) -> doc.SectionContents:
        return section_contents(self._parser.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> doc.SectionContents:
        documentation = ActPhaseDocumentationSyntax()
        initial_paragraphs = self._parser.fnap(SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH)
        sub_sections = []
        synopsis_section = doc_utils.synopsis_section(
            invokation_variants_content(None,
                                        documentation.invokation_variants(),
                                        documentation.syntax_element_descriptions()))
        sub_sections.append(synopsis_section)
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _see_also_specific(self) -> list:
        return [
            concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target,
            TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                   ACTOR_INSTRUCTION_NAME),
            TestSuiteSectionInstructionCrossReference(formatted_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                      ACTOR_INSTRUCTION_NAME),
        ]


DOCUMENTATION = FileInterpreterActorDocumentation()


class ActPhaseDocumentationSyntax(ActPhaseDocumentationSyntaxBase):
    def __init__(self):
        self.file = instruction_arguments.FILE_ARGUMENT
        self.argument = a.Named(help_texts.ARGUMENT)
        fm = {
            'FILE': self.file.name,
            'ARGUMENT': self.argument.name,
            'actor': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'act_phase': ACT_PHASE_NAME.emphasis,
            'home_directory_concept': formatting.conf_param_(conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO),
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
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
