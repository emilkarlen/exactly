from exactly_lib.act_phase_setups import command_line as actor
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.actors.names_and_cross_references import COMMAND_LINE_ACTOR
from exactly_lib.help.actors.single_command_line_base import SingleCommandLineActorDocumentationBase
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.plain_concepts.sandbox import SANDBOX_CONCEPT
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_content
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.phase_names import ACT_PHASE_NAME
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case import sandbox_directory_structure as sds
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import text


class CommandLineActorDocumentation(SingleCommandLineActorDocumentationBase):
    def __init__(self):
        super().__init__(COMMAND_LINE_ACTOR)
        from exactly_lib.execution.exit_values import EXECUTION__VALIDATE
        format_map = {
            'phase': phase_name_dictionary(),
            'home_directory': HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular,
            'sandbox': SANDBOX_CONCEPT.name().singular,
            'result_subdir': sds.SUB_DIRECTORY__RESULT,
            'VALIDATION': EXECUTION__VALIDATE.exit_identifier,
            'LINE_COMMENT_MARKER': LINE_COMMENT_MARKER,
        }
        self._parser = TextParser(format_map)

    def single_line_description_str(self) -> str:
        return self._parser.format(_SINGLE_LINE_DESCRIPTION)

    def act_phase_contents(self) -> doc.SectionContents:
        return doc.SectionContents(self._parser.fnap(_ACT_PHASE_CONTENTS))

    def act_phase_contents_syntax(self) -> doc.SectionContents:
        documentation = _ActPhaseSyntax()
        initial_paragraphs = self._parser.fnap(_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH)
        sub_sections = []
        synopsis_section = doc.Section(text('SYNOPSIS'),
                                       invokation_variants_content(None,
                                                                   documentation.invokation_variants(),
                                                                   documentation.syntax_element_descriptions()))
        sub_sections.append(synopsis_section)
        return doc.SectionContents(initial_paragraphs, sub_sections)

    def _see_also_specific(self) -> list:
        return super()._see_also_specific()


DOCUMENTATION = CommandLineActorDocumentation()


class _ActPhaseSyntax:
    CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

    ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()

    def __init__(self):
        self.executable = a.Named('EXECUTABLE')
        self.argument = a.Named('ARGUMENT')
        self.command = a.Constant('COMMAND')
        from exactly_lib.help.concepts.configuration_parameters.actor import ACTOR_CONCEPT
        fm = {
            'EXECUTABLE': self.executable.name,
            'ARGUMENT': self.argument.name,
            'actor': formatting.concept(ACTOR_CONCEPT.name().singular),
            'act_phase': ACT_PHASE_NAME.emphasis,
            'home_directory_concept': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular)
        }
        self._parser = TextParser(fm)

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
                                     self._paragraphs(_ARGUMENT_SYNTAX_ELEMENT)),
            SyntaxElementDescription(self.command.name,
                                     self._paragraphs(_COMMAND_SYNTAX_ELEMENT))
        ]

    def _cl_syntax_for_args(self, argument_usages: list) -> str:
        cl = a.CommandLine(argument_usages)
        return self._cl_syntax(cl)

    def _cl_syntax(self, command_line: a.CommandLine) -> str:
        return self.CL_SYNTAX_RENDERER.as_str(command_line)

    def _arg_syntax(self, arg: a.Argument) -> str:
        return self.ARG_SYNTAX_RENDERER.visit(arg)

    def _cli_argument_syntax_element_description(self,
                                                 argument: a.Argument,
                                                 description_rest: list) -> SyntaxElementDescription:
        return SyntaxElementDescription(self._arg_syntax(argument),
                                        description_rest)

    def _paragraphs(self, s: str, extra: dict = None) -> list:
        """
        :rtype: [`ParagraphItem`]
        """
        return self._parser.fnap(s, extra)


_SINGLE_LINE_DESCRIPTION = 'Executes a command line - either an executable file or a shell command'

_ACT_PHASE_CONTENTS = """\
A single command line.


Any number of empty lines and comment lines are allowed.
"""

_ACT_PHASE_CONTENTS_SYNTAX_INITIAL_PARAGRAPH = """\
Comment lines are lines beginning with {LINE_COMMENT_MARKER}
(optionally preceded by space).
"""

_PROGRAM_WITH_ARGUMENTS_INVOKATION_VARIANT = """\
Executes an executable file.
"""

_SHELL_COMMAND_INVOKATION_VARIANT = """\
Executes a shell command using the operating system's shell.
"""

_EXECUTABLE_SYNTAX_ELEMENT = """\
The path of an existing executable file.


If the path is not absolute, then it is relative the {home_directory_concept}.


Uses shell syntax.
"""

_COMMAND_SYNTAX_ELEMENT = """\
A shell command line.


Uses the syntax of the operating system's shell.
(Which shell this is depends on the operating system).
"""

_ARGUMENT_SYNTAX_ELEMENT = """\
A command line argument.


Uses shell syntax.
"""
