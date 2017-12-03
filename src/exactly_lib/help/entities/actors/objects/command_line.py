from exactly_lib import program_info
from exactly_lib.act_phase_setups import command_line as actor
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.entities.actors.contents_structure import ActorDocumentation
from exactly_lib.help.entities.actors.objects.common import \
    SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH, \
    ARGUMENT_SYNTAX_ELEMENT, ActPhaseDocumentationSyntaxBase
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.render import doc_utils
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.help_texts.entity import concepts, conf_params
from exactly_lib.help_texts.entity.actors import COMMAND_LINE_ACTOR
from exactly_lib.help_texts.test_case.actors import command_line as command_line_actor
from exactly_lib.help_texts.test_case.phase_names import ACT_PHASE_NAME, PHASE_NAME_DICTIONARY
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.textformat_parser import TextParser


class CommandLineActorDocumentation(ActorDocumentation):
    def __init__(self):
        super().__init__(COMMAND_LINE_ACTOR)
        self._tp = TextParser({
            'phase': PHASE_NAME_DICTIONARY,
            'LINE_COMMENT_MARKER': formatting.string_constant(LINE_COMMENT_MARKER),
        })

    def act_phase_contents(self) -> doc.SectionContents:
        return doc.SectionContents(self._tp.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> doc.SectionContents:
        documentation = ActPhaseDocumentationSyntax()
        initial_paragraphs = self._tp.fnap(SINGLE_LINE_PROGRAM_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH)
        sub_sections = []
        synopsis_section = doc_utils.synopsis_section(
            invokation_variants_content(None,
                                        documentation.invokation_variants(),
                                        documentation.syntax_element_descriptions()))
        sub_sections.append(synopsis_section)
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _see_also_specific(self) -> list:
        return cross_reference_id_list([
            conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO,
            concepts.SHELL_SYNTAX_CONCEPT_INFO,
        ])


DOCUMENTATION = CommandLineActorDocumentation()


class ActPhaseDocumentationSyntax(ActPhaseDocumentationSyntaxBase):
    def __init__(self):
        self.executable = a.Named(command_line_actor.EXECUTABLE)
        self.argument = a.Named(command_line_actor.ARGUMENT)
        self.command = a.Constant(command_line_actor.COMMAND)
        fm = {
            'EXECUTABLE': self.executable.name,
            'ARGUMENT': self.argument.name,
            'actor': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'act_phase': ACT_PHASE_NAME.emphasis,
            'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
        }
        super().__init__(TextParser(fm))

    def invokation_variants(self) -> list:
        executable_arg = a.Single(a.Multiplicity.MANDATORY, self.executable)
        optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, self.argument)
        shell_command_argument = a.Single(a.Multiplicity.MANDATORY,
                                          a.Constant(actor.SHELL_COMMAND_MARKER))
        command_argument = a.Single(a.Multiplicity.MANDATORY, self.command)
        return [
            InvokationVariant(self._cl_syntax_for_args([executable_arg,
                                                        optional_arguments_arg]),
                              self._parser.fnap(_PROGRAM_WITH_ARGUMENTS_INVOKATION_VARIANT)),
            InvokationVariant(self._cl_syntax_for_args([shell_command_argument,
                                                        command_argument]),
                              self._parser.fnap(_SHELL_COMMAND_INVOKATION_VARIANT)),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            SyntaxElementDescription(self.executable.name,
                                     self._paragraphs(_EXECUTABLE_SYNTAX_ELEMENT)),
            SyntaxElementDescription(self.argument.name,
                                     self._paragraphs(ARGUMENT_SYNTAX_ELEMENT)),
            SyntaxElementDescription(self.command.name,
                                     self._paragraphs(_COMMAND_SYNTAX_ELEMENT))
        ]


_ACT_PHASE_CONTENTS = """\
A single command line.


Any number of empty lines and comment lines are allowed.
"""

_PROGRAM_WITH_ARGUMENTS_INVOKATION_VARIANT = """\
Executes an executable file.
"""

_SHELL_COMMAND_INVOKATION_VARIANT = """\
Executes a shell command using the operating system's shell.
"""

_EXECUTABLE_SYNTAX_ELEMENT = """\
The path of an existing executable file.


If the path is not absolute, then it is searched for in the operating system's path,
which is dependent on the current operating system.


Uses {shell_syntax_concept}.
"""

_COMMAND_SYNTAX_ELEMENT = """\
A shell command line.


Uses the syntax of the current operating system's shell.

Note that this is not the same as the {shell_syntax_concept} built into {program_name}.
"""
